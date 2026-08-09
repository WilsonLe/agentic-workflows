<?php

declare(strict_types=1);

namespace AMSoft\WordPressGitSync;

use InvalidArgumentException;
use Throwable;
use WP_Error;
use WP_Post;
use WP_REST_Request;
use WP_REST_Response;

final class Rest_Controller
{
    public const REGISTRY_OPTION = 'amsoft_wordpress_git_sync_registry_v1';
    public const IDEMPOTENCY_OPTION = 'amsoft_wordpress_git_sync_idempotency_v1';
    public const EVENT_QUEUE_OPTION = 'amsoft_wordpress_git_sync_events_v1';
    private const MAX_BODY_BYTES = 2097152;
    private const MAX_IDEMPOTENCY = 500;
    private const MAX_EVENTS = 1000;
    /** @var array<string, array<int, string>> */
    private const RUNTIME_READ_ONLY_FIELDS = [
        'cpt' => ['post_type'],
        'wp_template' => ['theme'],
        'wp_template_part' => ['theme'],
        'wp_global_styles' => ['theme'],
        'wp_block' => ['sync_behavior'],
        'acf_values' => ['target_ref', 'field_group_refs'],
    ];

    private static bool $applying = false;

    public function __construct(private readonly Canonicalizer $canonicalizer)
    {
    }

    public function register_routes(): void
    {
        register_rest_route('amsoft/v1', '/registry', [
            [
                'methods' => 'GET',
                'callback' => [$this, 'get_registry'],
                'permission_callback' => static fn (): bool => current_user_can('edit_posts'),
            ],
            [
                'methods' => 'POST',
                'callback' => [$this, 'register_object'],
                'permission_callback' => static fn (): bool => current_user_can('manage_options'),
            ],
        ]);
        register_rest_route('amsoft/v1', '/events', [
            [
                'methods' => 'GET',
                'callback' => [$this, 'get_events'],
                'permission_callback' => static fn (): bool => current_user_can('manage_options'),
            ],
            [
                'methods' => 'DELETE',
                'callback' => [$this, 'acknowledge_event'],
                'permission_callback' => static fn (): bool => current_user_can('manage_options'),
            ],
        ]);
        register_rest_route('amsoft/v1', '/objects/(?P<object_type>[a-z][a-z0-9_-]{1,31})/(?P<object_key>[a-z0-9][a-z0-9._:-]{0,198})', [
            'methods' => 'GET',
            'callback' => [$this, 'get_object'],
            'permission_callback' => [$this, 'can_read_object'],
        ]);
        register_rest_route('amsoft/v1', '/objects/(?P<object_type>[a-z][a-z0-9_-]{1,31})/(?P<object_key>[a-z0-9][a-z0-9._:-]{0,198})/apply', [
            'methods' => 'POST',
            'callback' => [$this, 'apply_object'],
            'permission_callback' => [$this, 'can_edit_object'],
        ]);
    }

    /** @return array<string, array<string, mixed>> */
    private static function registry(): array
    {
        $registry = get_option(self::REGISTRY_OPTION, []);
        return is_array($registry) ? $registry : [];
    }

    private static function identity(WP_REST_Request $request): string
    {
        return self::validated_identity((string) $request['object_type'], (string) $request['object_key']);
    }

    private static function validated_identity(string $object_type, string $object_key): string
    {
        if (!preg_match('/^[a-z][a-z0-9_-]{1,31}$/', $object_type)
            || !preg_match('/^[a-z0-9][a-z0-9._:-]{0,198}$/', $object_key)
            || str_contains($object_key, '..')
            || ctype_digit($object_key)) {
            return '';
        }
        return $object_type . ':' . $object_key;
    }

    private static function reference_for_post(int $post_id): ?string
    {
        foreach (self::registry() as $identity => $registered) {
            if (is_array($registered) && (int) ($registered['post_id'] ?? 0) === $post_id) {
                return $identity;
            }
        }
        return null;
    }

    private static function post_id_for_reference(string $reference): int
    {
        $registered = self::registry()[$reference] ?? null;
        if (!is_array($registered) || (int) ($registered['post_id'] ?? 0) < 1) {
            throw new InvalidArgumentException('Object reference is not registered on this site.');
        }
        return (int) $registered['post_id'];
    }

    private static function user_reference(int $user_id): ?string
    {
        $user = get_user_by('id', $user_id);
        return $user instanceof \WP_User ? 'user:' . $user->user_login : null;
    }

    private static function user_id_for_reference(string $reference): int
    {
        if (!str_starts_with($reference, 'user:')) {
            throw new InvalidArgumentException('Author reference must use user:<login>.');
        }
        $user = get_user_by('login', substr($reference, 5));
        if (!$user instanceof \WP_User) {
            throw new InvalidArgumentException('Author reference does not resolve on this site.');
        }
        return (int) $user->ID;
    }

    public function can_read_object(WP_REST_Request $request): bool
    {
        $entry = self::registry()[self::identity($request)] ?? null;
        return is_array($entry) && current_user_can('edit_post', (int) $entry['post_id']);
    }

    public function can_edit_object(WP_REST_Request $request): bool
    {
        $entry = self::registry()[self::identity($request)] ?? null;
        if (!is_array($entry) || !current_user_can('edit_post', (int) $entry['post_id'])) {
            return false;
        }
        $post = get_post((int) $entry['post_id']);
        $post_type = $post instanceof WP_Post ? get_post_type_object($post->post_type) : null;
        if (!$post instanceof WP_Post || !$post_type instanceof \WP_Post_Type) {
            return false;
        }
        $managed = (array) ($entry['managed_fields'] ?? []);
        if (in_array('status', $managed, true) && !current_user_can($post_type->cap->publish_posts)) {
            return false;
        }
        if (in_array('author_ref', $managed, true) && !current_user_can($post_type->cap->edit_others_posts)) {
            return false;
        }
        if (in_array('terms', $managed, true)) {
            foreach (get_object_taxonomies($post->post_type, 'objects') as $taxonomy) {
                if ($taxonomy instanceof \WP_Taxonomy && !current_user_can($taxonomy->cap->assign_terms)) {
                    return false;
                }
            }
        }
        if (in_array('meta', $managed, true)) {
            foreach ((array) ($entry['adapter_config']['meta_keys'] ?? []) as $meta_key) {
                if (!is_string($meta_key) || !current_user_can('edit_post_meta', $post->ID, $meta_key)) {
                    return false;
                }
            }
        }
        return true;
    }

    public function get_registry(): WP_REST_Response
    {
        $objects = [];
        foreach (self::registry() as $identity => $entry) {
            if (!is_array($entry) || !current_user_can('edit_post', (int) $entry['post_id'])) {
                continue;
            }
            $record = $this->record($identity, $entry);
            if (!is_wp_error($record)) {
                $objects[] = $record;
            }
        }
        usort($objects, static fn (array $left, array $right): int => strcmp($left['identity'], $right['identity']));
        return new WP_REST_Response(['schema_version' => 1, 'objects' => $objects]);
    }

    public function register_object(WP_REST_Request $request): WP_REST_Response|WP_Error
    {
        $payload = $request->get_json_params();
        if (!is_array($payload) || strlen((string) $request->get_body()) > self::MAX_BODY_BYTES) {
            return new WP_Error('amsoft_invalid_registry', 'Registry payload is invalid.', ['status' => 400]);
        }
        $required = ['object_type', 'object_key', 'post_id', 'managed_fields', 'remote_fields', 'ownership', 'classification'];
        $allowed = array_merge($required, ['adapter_config']);
        $keys = array_keys($payload);
        sort($keys);
        sort($allowed);
        $missing = array_diff($required, array_keys($payload));
        if ($missing || array_diff($keys, $allowed)) {
            return new WP_Error('amsoft_invalid_registry', 'Registry fields differ from the v1 contract.', ['status' => 400]);
        }
        $post = get_post((int) $payload['post_id']);
        if (!$post instanceof WP_Post) {
            return new WP_Error('amsoft_object_not_found', 'Registry target does not exist.', ['status' => 404]);
        }
        $identity = self::validated_identity((string) $payload['object_type'], (string) $payload['object_key']);
        if ($identity === '') {
            return new WP_Error('amsoft_invalid_registry', 'Registry identity is not portable.', ['status' => 400]);
        }
        $object_type = (string) $payload['object_type'];
        if ($object_type === 'acf_field_group') {
            return new WP_Error('amsoft_code_lane_required', 'ACF field groups use the reviewed Git-owned code lane, not runtime registration.', ['status' => 422]);
        }
        $managed_fields = array_values(array_map('sanitize_key', (array) $payload['managed_fields']));
        if (array_intersect($managed_fields, self::RUNTIME_READ_ONLY_FIELDS[$object_type] ?? [])) {
            return new WP_Error('amsoft_read_only_field', 'Runtime registration declares an adapter identity field as writable.', ['status' => 422]);
        }
        $adapter_config = is_array($payload['adapter_config'] ?? null) ? $payload['adapter_config'] : [];
        $allowed_adapter_keys = $object_type === 'acf_values'
            ? ['meta_keys', 'field_keys', 'target_ref', 'field_group_refs']
            : ['meta_keys'];
        if (array_diff(array_keys($adapter_config), $allowed_adapter_keys)) {
            return new WP_Error('amsoft_invalid_adapter', 'Adapter configuration contains unsupported fields.', ['status' => 400]);
        }
        $meta_keys = $adapter_config['meta_keys'] ?? [];
        if (!is_array($meta_keys) || count($meta_keys) !== count(array_unique($meta_keys))) {
            return new WP_Error('amsoft_invalid_adapter', 'Adapter meta keys must be a unique array.', ['status' => 400]);
        }
        foreach ($meta_keys as $meta_key) {
            if (!is_string($meta_key) || !preg_match('/^[A-Za-z0-9_-]{1,191}$/', $meta_key) || !is_registered_meta_key('post', $meta_key, $post->post_type)) {
                return new WP_Error('amsoft_invalid_adapter', 'Adapter meta key is invalid or unregistered.', ['status' => 400]);
            }
        }
        if (in_array('meta', $managed_fields, true) && !$meta_keys) {
            return new WP_Error('amsoft_invalid_adapter', 'Managed post meta requires declared registered meta keys.', ['status' => 400]);
        }
        $entry = [
            'object_type' => $object_type,
            'object_key' => (string) $payload['object_key'],
            'post_id' => $post->ID,
            'managed_fields' => $managed_fields,
            'remote_fields' => array_values(array_map('sanitize_key', (array) $payload['remote_fields'])),
            'ownership' => sanitize_key((string) $payload['ownership']),
            'classification' => sanitize_key((string) $payload['classification']),
            'adapter_config' => $adapter_config,
        ];
        try {
            $this->canonicalizer->validate_object($this->object_from_post($entry, $post));
        } catch (InvalidArgumentException $error) {
            return new WP_Error('amsoft_invalid_registry', $error->getMessage(), ['status' => 400]);
        }
        $registry = self::registry();
        if (isset($registry[$identity]) && (int) ($registry[$identity]['post_id'] ?? 0) !== $post->ID) {
            return new WP_Error('amsoft_identity_collision', 'Portable identity is already assigned to another WordPress object.', ['status' => 409]);
        }
        foreach ($registry as $registered_identity => $registered) {
            if ($registered_identity !== $identity && (int) ($registered['post_id'] ?? 0) === $post->ID) {
                return new WP_Error('amsoft_identity_collision', 'WordPress post is already registered under another identity.', ['status' => 409]);
            }
        }
        $registry[$identity] = $entry;
        update_option(self::REGISTRY_OPTION, $registry, false);
        $stored = self::registry()[$identity] ?? null;
        if (!is_array($stored) || $stored !== $entry) {
            return new WP_Error('amsoft_registry_write_failed', 'Registry write could not be verified.', ['status' => 500]);
        }
        return new WP_REST_Response(['ok' => true, 'identity' => $identity, 'record' => $this->record($identity, $entry)], 201);
    }

    public function get_object(WP_REST_Request $request): WP_REST_Response|WP_Error
    {
        $identity = self::identity($request);
        $entry = self::registry()[$identity] ?? null;
        if (!is_array($entry)) {
            return new WP_Error('amsoft_object_not_found', 'Managed object is not registered.', ['status' => 404]);
        }
        $record = $this->record($identity, $entry);
        return is_wp_error($record) ? $record : new WP_REST_Response($record);
    }

    /** @param array<string, mixed> $entry
     *  @return array<string, mixed>|WP_Error
     */
    private function record(string $identity, array $entry): array|WP_Error
    {
        $post = get_post((int) $entry['post_id']);
        if (!$post instanceof WP_Post) {
            return new WP_Error('amsoft_object_not_found', 'Managed WordPress object no longer exists.', ['status' => 404]);
        }
        try {
            $object = $this->object_from_post($entry, $post);
            return [
                'schema_version' => 1,
                'identity' => $identity,
                'object' => $object,
                'revision' => $post->post_modified_gmt . ':' . $post->ID,
                'modified_gmt' => mysql_to_rfc3339($post->post_modified_gmt),
                'sha256' => $this->canonicalizer->managed_digest($object),
                'guard' => 'atomic-compare-and-swap',
                'atomic_boundary' => 'WordPress database transaction for the registered post and declared fields; external hook side effects are excluded',
            ];
        } catch (InvalidArgumentException $error) {
            return new WP_Error('amsoft_invalid_managed_object', $error->getMessage(), ['status' => 422]);
        }
    }

    /** @param array<string, mixed> $entry
     *  @return array<string, mixed>
     */
    private function object_from_post(array $entry, WP_Post $post): array
    {
        $parent_ref = $post->post_parent > 0 ? self::reference_for_post((int) $post->post_parent) : null;
        $featured_id = (int) get_post_thumbnail_id($post);
        $featured_ref = $featured_id > 0 ? self::reference_for_post($featured_id) : null;
        $author_ref = self::user_reference((int) $post->post_author);
        $terms = [];
        foreach (get_object_taxonomies($post->post_type) as $taxonomy) {
            $post_terms = wp_get_object_terms($post->ID, $taxonomy);
            if (is_wp_error($post_terms)) {
                throw new InvalidArgumentException($post_terms->get_error_message());
            }
            foreach ($post_terms as $term) {
                $terms[] = 'term:' . $taxonomy . ':' . $term->slug;
            }
        }
        sort($terms, SORT_STRING);
        $all = [
            'post_type' => $post->post_type,
            'title' => ['raw' => $post->post_title],
            'content' => ['raw' => $post->post_content],
            'excerpt' => ['raw' => $post->post_excerpt],
            'slug' => $post->post_name,
            'status' => $post->post_status,
            'date_gmt' => mysql_to_rfc3339($post->post_date_gmt),
            'parent_ref' => $parent_ref,
            'author_ref' => $author_ref,
            'terms' => $terms,
            'meta' => [],
            'featured_media_ref' => $featured_ref,
            'template' => get_page_template_slug($post) ?: '',
            'theme' => get_stylesheet(),
            'area' => (string) get_post_meta($post->ID, 'wp_template_part_area', true),
            'sync_behavior' => 'synced',
            'settings' => [],
            'styles' => [],
            'logical_id' => (string) get_post_meta($post->ID, '_amsoft_media_logical_id', true),
            'source_sha256' => (string) get_post_meta($post->ID, '_amsoft_media_source_sha256', true),
            'mime_type' => $post->post_mime_type,
            'bytes' => (int) get_post_meta($post->ID, '_amsoft_media_bytes', true),
            'width' => (int) get_post_meta($post->ID, '_amsoft_media_width', true),
            'height' => (int) get_post_meta($post->ID, '_amsoft_media_height', true),
            'alt_text' => (string) get_post_meta($post->ID, '_wp_attachment_image_alt', true),
            'caption' => ['raw' => $post->post_excerpt],
            'credit' => (string) get_post_meta($post->ID, '_amsoft_media_credit', true),
            'license' => (string) get_post_meta($post->ID, '_amsoft_media_license', true),
            'storage' => get_post_meta($post->ID, '_amsoft_media_storage', true) ?: [],
        ];
        if ($entry['object_type'] === 'attachment') {
            $all['status'] = (string) (get_post_meta($post->ID, '_amsoft_media_status', true) ?: 'available');
        }
        if (in_array('meta', array_merge($entry['managed_fields'], $entry['remote_fields']), true)) {
            $meta = [];
            foreach ((array) ($entry['adapter_config']['meta_keys'] ?? []) as $meta_key) {
                if (!is_string($meta_key) || !is_registered_meta_key('post', $meta_key, $post->post_type)) {
                    throw new InvalidArgumentException('Adapter meta key is invalid or unregistered.');
                }
                $meta[$meta_key] = get_post_meta($post->ID, $meta_key, true);
            }
            $all['meta'] = $meta;
        }
        if ($entry['object_type'] === 'acf_values') {
            if (!function_exists('get_field')) {
                throw new InvalidArgumentException('ACF values adapter requires Advanced Custom Fields.');
            }
            $field_keys = $entry['adapter_config']['field_keys'] ?? [];
            if (!is_array($field_keys) || !$field_keys) {
                throw new InvalidArgumentException('ACF values adapter requires declared field keys.');
            }
            $values = [];
            foreach ($field_keys as $field_key) {
                if (!is_string($field_key) || !preg_match('/^field_[A-Za-z0-9_-]+$/', $field_key)) {
                    throw new InvalidArgumentException('ACF adapter field key is invalid.');
                }
                $values[$field_key] = get_field($field_key, $post->ID, false);
            }
            $all['target_ref'] = (string) ($entry['adapter_config']['target_ref'] ?? '');
            $all['field_group_refs'] = array_values((array) ($entry['adapter_config']['field_group_refs'] ?? []));
            $all['values'] = $values;
        }
        if ($entry['object_type'] === 'wp_global_styles') {
            $decoded = json_decode($post->post_content, true);
            if (is_array($decoded)) {
                $all['settings'] = $decoded['settings'] ?? [];
                $all['styles'] = $decoded['styles'] ?? [];
            }
        }
        $data = [];
        foreach (array_unique(array_merge($entry['managed_fields'], $entry['remote_fields'])) as $field) {
            if (array_key_exists($field, $all)) {
                $data[$field] = $all[$field];
            }
        }
        $owned_fields = array_unique(array_merge($entry['managed_fields'], $entry['remote_fields']));
        $references = [];
        foreach (['parent_ref' => $parent_ref, 'author_ref' => $author_ref, 'featured_media_ref' => $featured_ref] as $field => $reference) {
            if (in_array($field, $owned_fields, true) && is_string($reference) && $reference !== '') {
                $references[] = $reference;
            }
        }
        if (in_array('terms', $owned_fields, true)) {
            $references = array_merge($references, $terms);
        }
        if ($entry['object_type'] === 'acf_values') {
            $references = array_merge($references, (array) ($all['field_group_refs'] ?? []));
            if (is_string($all['target_ref'] ?? null) && $all['target_ref'] !== '') {
                $references[] = $all['target_ref'];
            }
        }
        sort($references, SORT_STRING);
        return $this->canonicalizer->validate_object([
            'schema_version' => 1,
            'kind' => 'wordpress-managed-object',
            'object_type' => $entry['object_type'],
            'object_key' => $entry['object_key'],
            'environment' => wp_get_environment_type(),
            'ownership' => $entry['ownership'],
            'managed_fields' => $entry['managed_fields'],
            'remote_fields' => $entry['remote_fields'],
            'data' => $data,
            'references' => array_values(array_unique($references)),
            'provenance' => ['wordpress_post_id' => $post->ID, 'post_type' => $post->post_type],
            'state' => 'active',
            'classification' => $entry['classification'],
            'tombstone' => false,
        ]);
    }

    public function apply_object(WP_REST_Request $request): WP_REST_Response|WP_Error
    {
        global $wpdb;
        if (strlen((string) $request->get_body()) > self::MAX_BODY_BYTES) {
            return new WP_Error('amsoft_payload_too_large', 'Apply payload exceeds 2 MiB.', ['status' => 413]);
        }
        $payload = $request->get_json_params();
        $payload_keys = is_array($payload) ? array_keys($payload) : [];
        $expected_payload_keys = ['schema_version', 'object', 'expected_sha256', 'expected_revision', 'idempotency_key', 'dry_run'];
        sort($payload_keys);
        sort($expected_payload_keys);
        if (!is_array($payload) || $payload_keys !== $expected_payload_keys || ($payload['schema_version'] ?? null) !== 1) {
            return new WP_Error('amsoft_invalid_apply', 'Apply payload differs from the v1 contract.', ['status' => 400]);
        }
        $identity = self::identity($request);
        $entry = self::registry()[$identity] ?? null;
        if (!is_array($entry)) {
            return new WP_Error('amsoft_object_not_found', 'Managed object is not registered.', ['status' => 404]);
        }
        try {
            $desired = $this->canonicalizer->validate_object((array) $payload['object']);
        } catch (InvalidArgumentException $error) {
            return new WP_Error('amsoft_invalid_managed_object', $error->getMessage(), ['status' => 422]);
        }
        if ($identity !== $desired['object_type'] . ':' . $desired['object_key']) {
            return new WP_Error('amsoft_identity_mismatch', 'Route and object identities differ.', ['status' => 409]);
        }
        $desired_managed = $desired['managed_fields'];
        $registered_managed = array_values((array) $entry['managed_fields']);
        $desired_remote = $desired['remote_fields'];
        $registered_remote = array_values((array) $entry['remote_fields']);
        sort($desired_managed, SORT_STRING);
        sort($registered_managed, SORT_STRING);
        sort($desired_remote, SORT_STRING);
        sort($registered_remote, SORT_STRING);
        if ($desired_managed !== $registered_managed
            || $desired_remote !== $registered_remote
            || $desired['ownership'] !== $entry['ownership']
            || $desired['classification'] !== $entry['classification']
            || $desired['environment'] !== wp_get_environment_type()
            || $desired['state'] !== 'active'
            || $desired['tombstone'] !== false) {
            return new WP_Error('amsoft_contract_mismatch', 'Desired object differs from its registered ownership or lifecycle contract.', ['status' => 409]);
        }
        if (!is_string($payload['expected_sha256']) || !preg_match('/^[0-9a-f]{64}$/', $payload['expected_sha256'])
            || (!is_string($payload['expected_revision']) && !is_int($payload['expected_revision']))
            || (string) $payload['expected_revision'] === ''
            || !is_bool($payload['dry_run'])) {
            return new WP_Error('amsoft_invalid_expectation', 'Expected state or dry-run value is invalid.', ['status' => 400]);
        }
        $idempotency = $payload['idempotency_key'];
        if (!is_string($idempotency) || !preg_match('/^[A-Za-z0-9._:-]{8,128}$/', $idempotency)) {
            return new WP_Error('amsoft_invalid_idempotency', 'Idempotency key is invalid.', ['status' => 400]);
        }
        $request_hash = $this->canonicalizer->digest([
            'identity' => $identity,
            'expected_sha256' => (string) $payload['expected_sha256'],
            'expected_revision' => (string) $payload['expected_revision'],
            'desired_sha256' => $this->canonicalizer->managed_digest($desired),
        ]);
        if ($wpdb->query('START TRANSACTION') === false) {
            return new WP_Error('amsoft_atomic_unavailable', 'WordPress could not start the guarded transaction.', ['status' => 503]);
        }
        try {
            $journal_serialized = $wpdb->get_var($wpdb->prepare(
                "SELECT option_value FROM {$wpdb->options} WHERE option_name = %s FOR UPDATE",
                self::IDEMPOTENCY_OPTION
            ));
            if (!is_string($journal_serialized)) {
                throw new InvalidArgumentException('Idempotency journal is unavailable.');
            }
            $journal = maybe_unserialize($journal_serialized);
            if (!is_array($journal)) {
                throw new InvalidArgumentException('Idempotency journal is invalid.');
            }
            if (isset($journal[$idempotency])) {
                if (!hash_equals((string) $journal[$idempotency]['request_hash'], $request_hash)) {
                    $wpdb->query('ROLLBACK');
                    return new WP_Error('amsoft_idempotency_conflict', 'Idempotency key belongs to another request.', ['status' => 409]);
                }
                $wpdb->query('COMMIT');
                return new WP_REST_Response(array_merge($journal[$idempotency]['result'], ['idempotent_replay' => true]));
            }
            $post_id = (int) $entry['post_id'];
            $locked_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE ID = %d FOR UPDATE", $post_id));
            if ((int) $locked_id !== $post_id) {
                throw new InvalidArgumentException('Managed WordPress object no longer exists.');
            }
            clean_post_cache($post_id);
            $before = $this->record($identity, $entry);
            if (is_wp_error($before)) {
                throw new InvalidArgumentException($before->get_error_message());
            }
            if (!hash_equals((string) $before['sha256'], (string) $payload['expected_sha256']) || (string) $before['revision'] !== (string) $payload['expected_revision']) {
                $wpdb->query('ROLLBACK');
                return new WP_Error('amsoft_stale_remote', 'Remote object changed since the expected baseline.', [
                    'status' => 409,
                    'actual_sha256' => $before['sha256'],
                    'actual_revision' => $before['revision'],
                ]);
            }
            $base_result = [
                'ok' => true,
                'dry_run' => (bool) $payload['dry_run'],
                'identity' => $identity,
                'guard' => 'atomic-compare-and-swap',
                'before_sha256' => $before['sha256'],
                'before_revision' => $before['revision'],
                'desired_sha256' => $this->canonicalizer->managed_digest($desired),
            ];
            if ((bool) $payload['dry_run']) {
                $wpdb->query('ROLLBACK');
                return new WP_REST_Response($base_result);
            }
            self::$applying = true;
            $update = ['ID' => $post_id];
            $field_map = [
                'title' => 'post_title', 'content' => 'post_content', 'excerpt' => 'post_excerpt',
                'slug' => 'post_name', 'status' => 'post_status', 'date_gmt' => 'post_date_gmt',
            ];
            foreach ($desired['managed_fields'] as $field) {
                if ($desired['object_type'] === 'attachment' && $field === 'status') {
                    continue;
                }
                if (isset($field_map[$field])) {
                    $value = $desired['data'][$field];
                    $update[$field_map[$field]] = is_array($value) && array_key_exists('raw', $value) ? (string) $value['raw'] : $value;
                }
            }
            if ($desired['object_type'] === 'attachment' && in_array('caption', $desired['managed_fields'], true)) {
                $caption = $desired['data']['caption'];
                $update['post_excerpt'] = is_array($caption) && array_key_exists('raw', $caption) ? (string) $caption['raw'] : (string) $caption;
            }
            if (in_array('parent_ref', $desired['managed_fields'], true)) {
                $parent_ref = $desired['data']['parent_ref'] ?? null;
                $update['post_parent'] = $parent_ref === null ? 0 : self::post_id_for_reference((string) $parent_ref);
            }
            if (in_array('author_ref', $desired['managed_fields'], true)) {
                $update['post_author'] = self::user_id_for_reference((string) $desired['data']['author_ref']);
            }
            if (in_array('settings', $desired['managed_fields'], true) || in_array('styles', $desired['managed_fields'], true)) {
                $update['post_content'] = wp_json_encode([
                    'version' => 3,
                    'settings' => $desired['data']['settings'] ?? [],
                    'styles' => $desired['data']['styles'] ?? [],
                ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
            }
            $updated = wp_update_post(wp_slash($update), true, false);
            if (is_wp_error($updated)) {
                throw new InvalidArgumentException($updated->get_error_message());
            }
            if (in_array('template', $desired['managed_fields'], true)) {
                update_post_meta($post_id, '_wp_page_template', sanitize_text_field((string) $desired['data']['template']));
            }
            if ($desired['object_type'] === 'wp_template_part' && in_array('area', $desired['managed_fields'], true)) {
                update_post_meta($post_id, 'wp_template_part_area', sanitize_key((string) $desired['data']['area']));
            }
            if ($desired['object_type'] === 'attachment') {
                $media_meta_fields = [
                    'logical_id' => '_amsoft_media_logical_id',
                    'source_sha256' => '_amsoft_media_source_sha256',
                    'bytes' => '_amsoft_media_bytes',
                    'width' => '_amsoft_media_width',
                    'height' => '_amsoft_media_height',
                    'alt_text' => '_wp_attachment_image_alt',
                    'credit' => '_amsoft_media_credit',
                    'license' => '_amsoft_media_license',
                    'storage' => '_amsoft_media_storage',
                    'status' => '_amsoft_media_status',
                ];
                foreach ($media_meta_fields as $field => $meta_key) {
                    if (in_array($field, $desired['managed_fields'], true)) {
                        update_post_meta($post_id, $meta_key, $desired['data'][$field]);
                    }
                }
                if (in_array('mime_type', $desired['managed_fields'], true)) {
                    $mime_result = $wpdb->update($wpdb->posts, ['post_mime_type' => (string) $desired['data']['mime_type']], ['ID' => $post_id], ['%s'], ['%d']);
                    if ($mime_result === false) {
                        throw new InvalidArgumentException('Attachment MIME type update failed.');
                    }
                    clean_post_cache($post_id);
                }
            }
            if (in_array('meta', $desired['managed_fields'], true)) {
                $configured_meta_keys = array_values((array) ($entry['adapter_config']['meta_keys'] ?? []));
                $desired_meta = (array) $desired['data']['meta'];
                $desired_meta_keys = array_keys($desired_meta);
                sort($configured_meta_keys, SORT_STRING);
                sort($desired_meta_keys, SORT_STRING);
                if ($configured_meta_keys !== $desired_meta_keys) {
                    throw new InvalidArgumentException('Apply meta keys differ from the registered adapter contract.');
                }
                foreach ($configured_meta_keys as $meta_key) {
                    if (!is_string($meta_key) || !is_registered_meta_key('post', $meta_key, get_post_type($post_id))) {
                        throw new InvalidArgumentException('Apply includes unregistered post meta.');
                    }
                    update_post_meta($post_id, $meta_key, $desired_meta[$meta_key]);
                }
            }
            if (in_array('terms', $desired['managed_fields'], true)) {
                $desired_terms = [];
                foreach ((array) $desired['data']['terms'] as $term_ref) {
                    if (!is_string($term_ref) || !preg_match('/^term:([a-z0-9_-]+):(.+)$/', $term_ref, $matches)) {
                        throw new InvalidArgumentException('Term reference must use term:<taxonomy>:<slug>.');
                    }
                    $term = get_term_by('slug', $matches[2], $matches[1]);
                    if (!$term instanceof \WP_Term) {
                        throw new InvalidArgumentException('Term reference does not resolve on this site.');
                    }
                    $desired_terms[$matches[1]][] = (int) $term->term_id;
                }
                foreach (get_object_taxonomies(get_post_type($post_id)) as $taxonomy) {
                    $term_result = wp_set_object_terms($post_id, $desired_terms[$taxonomy] ?? [], $taxonomy, false);
                    if (is_wp_error($term_result)) {
                        throw new InvalidArgumentException($term_result->get_error_message());
                    }
                }
            }
            if (in_array('featured_media_ref', $desired['managed_fields'], true)) {
                $media_ref = $desired['data']['featured_media_ref'] ?? null;
                $thumbnail_result = $media_ref === null
                    ? delete_post_thumbnail($post_id)
                    : set_post_thumbnail($post_id, self::post_id_for_reference((string) $media_ref));
                if ($thumbnail_result === false && $media_ref !== null) {
                    throw new InvalidArgumentException('Featured media reference could not be applied.');
                }
            }
            if ($desired['object_type'] === 'acf_values' && in_array('values', $desired['managed_fields'], true)) {
                if (!function_exists('update_field')) {
                    throw new InvalidArgumentException('ACF values adapter requires Advanced Custom Fields.');
                }
                $allowed_field_keys = array_values((array) ($entry['adapter_config']['field_keys'] ?? []));
                foreach ((array) $desired['data']['values'] as $field_key => $field_value) {
                    if (!is_string($field_key) || !in_array($field_key, $allowed_field_keys, true)) {
                        throw new InvalidArgumentException('ACF apply includes an undeclared field key.');
                    }
                    if (update_field($field_key, $field_value, $post_id) === false) {
                        throw new InvalidArgumentException('ACF field update failed canonical writeback.');
                    }
                }
            }
            clean_post_cache($post_id);
            $after = $this->record($identity, $entry);
            if (is_wp_error($after) || !hash_equals($this->canonicalizer->managed_digest($desired), (string) $after['sha256'])) {
                throw new InvalidArgumentException('Canonical readback differs from the desired object.');
            }
            $result = array_merge($base_result, [
                'after_sha256' => $after['sha256'],
                'after_revision' => $after['revision'],
                'readback' => $after,
                'idempotent_replay' => false,
            ]);
            $journal[$idempotency] = ['request_hash' => $request_hash, 'result' => $result];
            if (count($journal) > self::MAX_IDEMPOTENCY) {
                $journal = array_slice($journal, -self::MAX_IDEMPOTENCY, null, true);
            }
            $journal_write = $wpdb->update(
                $wpdb->options,
                ['option_value' => maybe_serialize($journal)],
                ['option_name' => self::IDEMPOTENCY_OPTION],
                ['%s'],
                ['%s']
            );
            if ($journal_write === false || $wpdb->query('COMMIT') === false) {
                throw new InvalidArgumentException('Idempotency journal commit failed.');
            }
            wp_cache_delete(self::IDEMPOTENCY_OPTION, 'options');
            return new WP_REST_Response($result);
        } catch (Throwable $error) {
            $wpdb->query('ROLLBACK');
            if (isset($post_id)) {
                clean_post_cache($post_id);
            }
            wp_cache_delete(self::IDEMPOTENCY_OPTION, 'options');
            return new WP_Error('amsoft_apply_failed', 'Guarded apply failed and was rolled back.', ['status' => 422]);
        } finally {
            self::$applying = false;
        }
    }

    public static function capture_managed_save(int $post_id, WP_Post $post, bool $update): void
    {
        if (self::$applying || !$update || wp_is_post_autosave($post_id) || wp_is_post_revision($post_id)) {
            return;
        }
        foreach (self::registry() as $identity => $entry) {
            if ((int) ($entry['post_id'] ?? 0) !== $post_id || ($entry['classification'] ?? '') !== 'public') {
                continue;
            }
            $events = get_option(self::EVENT_QUEUE_OPTION, []);
            $correlation = wp_generate_uuid4();
            $events[$correlation] = [
                'schema_version' => 1,
                'event' => 'wordpress-save',
                'site_key' => hash('sha256', home_url('/')),
                'environment' => wp_get_environment_type(),
                'identity' => $identity,
                'correlation_id' => $correlation,
                'actor' => get_current_user_id(),
                'autosave' => false,
                'revision' => false,
                'classification' => 'public',
            ];
            if (count($events) > self::MAX_EVENTS) {
                $events = array_slice($events, -self::MAX_EVENTS, null, true);
            }
            update_option(self::EVENT_QUEUE_OPTION, $events, false);
            break;
        }
    }

    public function get_events(): WP_REST_Response
    {
        $events = get_option(self::EVENT_QUEUE_OPTION, []);
        return new WP_REST_Response(['schema_version' => 1, 'events' => array_values(is_array($events) ? $events : [])]);
    }

    public function acknowledge_event(WP_REST_Request $request): WP_REST_Response|WP_Error
    {
        $correlation = sanitize_text_field((string) $request->get_param('correlation_id'));
        $events = get_option(self::EVENT_QUEUE_OPTION, []);
        if (!is_array($events) || !isset($events[$correlation])) {
            return new WP_Error('amsoft_event_not_found', 'Queued event does not exist.', ['status' => 404]);
        }
        unset($events[$correlation]);
        update_option(self::EVENT_QUEUE_OPTION, $events, false);
        return new WP_REST_Response(['ok' => true, 'correlation_id' => $correlation]);
    }
}
