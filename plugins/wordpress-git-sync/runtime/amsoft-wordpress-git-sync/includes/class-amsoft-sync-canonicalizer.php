<?php

declare(strict_types=1);

namespace AMSoft\WordPressGitSync;

use InvalidArgumentException;

final class Canonicalizer
{
    public const SERIALIZER = 'amsoft-wordpress-managed-object-json-v1';

    /** @var array<string, array<int, string>> */
    private const FIELDS = [
        'post' => ['title', 'content', 'excerpt', 'slug', 'status', 'date_gmt', 'parent_ref', 'author_ref', 'terms', 'meta', 'featured_media_ref', 'template'],
        'page' => ['title', 'content', 'excerpt', 'slug', 'status', 'date_gmt', 'parent_ref', 'author_ref', 'terms', 'meta', 'featured_media_ref', 'template'],
        'cpt' => ['post_type', 'title', 'content', 'excerpt', 'slug', 'status', 'date_gmt', 'parent_ref', 'author_ref', 'terms', 'meta', 'featured_media_ref', 'template'],
        'wp_template' => ['title', 'content', 'slug', 'status', 'theme', 'area'],
        'wp_template_part' => ['title', 'content', 'slug', 'status', 'theme', 'area'],
        'wp_navigation' => ['title', 'content', 'slug', 'status'],
        'wp_global_styles' => ['title', 'slug', 'status', 'theme', 'settings', 'styles'],
        'wp_block' => ['title', 'content', 'slug', 'status', 'sync_behavior'],
        'attachment' => ['logical_id', 'source_sha256', 'mime_type', 'bytes', 'width', 'height', 'alt_text', 'caption', 'credit', 'license', 'storage', 'status'],
        'acf_field_group' => ['key', 'title', 'fields', 'location', 'active', 'modified'],
        'acf_values' => ['target_ref', 'field_group_refs', 'values', 'status'],
    ];

    private const OWNERSHIP = ['git', 'wordpress', 'shared-guarded', 'manifest', 'runtime-generated', 'read-only', 'excluded'];
    private const STATES = ['active', 'read-only', 'unsupported', 'excluded', 'deleted'];
    private const CLASSIFICATIONS = ['public', 'internal', 'restricted'];
    private const FORBIDDEN_KEYS = ['application_password', 'authorization', 'cookie', 'cookies', 'credential', 'credentials', 'nonce', 'password', 'private_key', 'secret', 'signed_url', 'token'];

    /** @param mixed $value
     *  @return mixed
     */
    public function normalize($value)
    {
        if (is_float($value)) {
            throw new InvalidArgumentException('Floating-point values are not canonical.');
        }
        if (is_string($value)) {
            $value = str_replace(["\r\n", "\r"], "\n", $value);
            if (class_exists('Normalizer')) {
                /** @var string|false $normalized */
                $normalized = \Normalizer::normalize($value, \Normalizer::FORM_C);
                if ($normalized !== false) {
                    return $normalized;
                }
            }
            return $value;
        }
        if (is_array($value)) {
            if (!array_is_list($value)) {
                ksort($value, SORT_STRING);
            }
            foreach ($value as $key => $nested) {
                $value[$key] = $this->normalize($nested);
            }
            return $value;
        }
        if ($value === null || is_bool($value) || is_int($value)) {
            return $value;
        }
        throw new InvalidArgumentException('Unsupported canonical value.');
    }

    /** @param array<string, mixed> $value */
    public function bytes(array $value): string
    {
        $encoded = wp_json_encode(
            $this->normalize($value),
            JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE
        );
        if (!is_string($encoded)) {
            throw new InvalidArgumentException('Canonical JSON encoding failed.');
        }
        return $encoded . "\n";
    }

    /** @param array<string, mixed> $value */
    public function digest(array $value): string
    {
        return hash('sha256', $this->bytes($value));
    }

    /** @param array<string, mixed> $object
     *  @return array<string, mixed>
     */
    public function validate_object(array $object): array
    {
        $required = [
            'schema_version', 'kind', 'object_type', 'object_key', 'environment', 'ownership',
            'managed_fields', 'remote_fields', 'data', 'references', 'provenance', 'state',
            'classification', 'tombstone',
        ];
        $keys = array_keys($object);
        sort($keys);
        $expected = $required;
        sort($expected);
        if ($keys !== $expected || ($object['schema_version'] ?? null) !== 1 || ($object['kind'] ?? null) !== 'wordpress-managed-object') {
            throw new InvalidArgumentException('Managed object differs from the v1 contract.');
        }
        $type = $object['object_type'];
        $key = $object['object_key'];
        if (!is_string($type) || !isset(self::FIELDS[$type]) || !is_string($key)) {
            throw new InvalidArgumentException('Managed object identity is unsupported.');
        }
        $identity = $type . ':' . $key;
        if (!preg_match('/^[a-z][a-z0-9_-]{1,31}:[a-z0-9][a-z0-9._:-]{0,198}$/', $identity) || str_contains($identity, '..') || ctype_digit($key)) {
            throw new InvalidArgumentException('Managed object identity is not portable.');
        }
        if (!in_array($object['environment'], ['local', 'development', 'staging', 'production'], true)
            || !in_array($object['ownership'], self::OWNERSHIP, true)
            || !in_array($object['state'], self::STATES, true)
            || !in_array($object['classification'], self::CLASSIFICATIONS, true)
            || !is_bool($object['tombstone'])
            || $object['tombstone'] !== ($object['state'] === 'deleted')) {
            throw new InvalidArgumentException('Managed object lifecycle fields are invalid.');
        }
        if (!is_array($object['managed_fields']) || !is_array($object['remote_fields']) || !is_array($object['data']) || !is_array($object['references']) || !is_array($object['provenance'])) {
            throw new InvalidArgumentException('Managed object collections are invalid.');
        }
        $managed = array_values($object['managed_fields']);
        $remote = array_values($object['remote_fields']);
        if (array_filter($managed, static fn ($field): bool => !is_string($field))
            || array_filter($remote, static fn ($field): bool => !is_string($field))
            || count($managed) !== count(array_unique($managed))
            || count($remote) !== count(array_unique($remote))
            || array_intersect($managed, $remote)) {
            throw new InvalidArgumentException('Managed field ownership is ambiguous.');
        }
        $unknown = array_diff(array_merge($managed, $remote), self::FIELDS[$type]);
        if ($unknown || array_diff(array_keys($object['data']), array_merge($managed, $remote)) || array_diff($managed, array_keys($object['data']))) {
            throw new InvalidArgumentException('Managed object contains unsupported or unowned fields.');
        }
        if (in_array($object['ownership'], ['runtime-generated', 'read-only', 'excluded'], true) && $managed) {
            throw new InvalidArgumentException('Read-only ownership cannot declare managed fields.');
        }
        if (count($object['references']) !== count(array_unique($object['references'], SORT_REGULAR))) {
            throw new InvalidArgumentException('Managed object references must be unique.');
        }
        foreach ($object['references'] as $reference) {
            if (!is_string($reference) || !preg_match('/^[a-z][a-z0-9_-]{1,31}:[a-z0-9][a-z0-9._:-]{0,198}$/', $reference)) {
                throw new InvalidArgumentException('Managed object reference is invalid.');
            }
        }
        if ($this->contains_secret_key($object)) {
            throw new InvalidArgumentException('Secret-shaped fields are prohibited in managed objects.');
        }
        if ($type === 'attachment') {
            $this->validate_media($object['data']);
        }
        if ($type === 'acf_values') {
            $this->validate_acf_values($object['data']);
        }
        return $this->normalize($object);
    }

    /** @param mixed $value */
    private function contains_secret_key($value): bool
    {
        if (!is_array($value)) {
            return false;
        }
        foreach ($value as $key => $nested) {
            if (is_string($key)) {
                $normalized = strtolower(str_replace('-', '_', $key));
                if (in_array($normalized, self::FORBIDDEN_KEYS, true)
                    || str_ends_with($normalized, '_password')
                    || str_ends_with($normalized, '_secret')
                    || str_ends_with($normalized, '_token')) {
                    return true;
                }
            }
            if ($this->contains_secret_key($nested)) {
                return true;
            }
        }
        return false;
    }

    /** @param array<string, mixed> $data */
    private function validate_media(array $data): void
    {
        foreach (['logical_id', 'source_sha256', 'mime_type', 'bytes', 'storage'] as $field) {
            if (!array_key_exists($field, $data)) {
                throw new InvalidArgumentException('Media manifest is incomplete.');
            }
        }
        if (!is_string($data['source_sha256']) || !preg_match('/^[0-9a-f]{64}$/', $data['source_sha256'])
            || !is_int($data['bytes']) || $data['bytes'] < 1 || $data['bytes'] > 104857600
            || !is_string($data['mime_type']) || !preg_match('#^(image|video|audio|application)/[a-z0-9.+-]+$#', $data['mime_type'])
            || !is_array($data['storage']) || !in_array($data['storage']['kind'] ?? null, ['object-store', 'release-artifact', 'git-lfs'], true)
            || empty($data['license']) || empty($data['credit'])) {
            throw new InvalidArgumentException('Media manifest values are invalid or lack rights metadata.');
        }
    }

    /** @param mixed $value */
    private function contains_php_serialization($value): bool
    {
        if (is_string($value)) {
            return (bool) preg_match('/^(a|O|C|s|i|b|d|N):/', $value);
        }
        if (is_array($value)) {
            foreach ($value as $nested) {
                if ($this->contains_php_serialization($nested)) {
                    return true;
                }
            }
        }
        return false;
    }

    /** @param array<string, mixed> $data */
    private function validate_acf_values(array $data): void
    {
        if (!is_string($data['target_ref'] ?? null)
            || !preg_match('/^[a-z][a-z0-9_-]{1,31}:[a-z0-9][a-z0-9._:-]{0,198}$/', $data['target_ref'])
            || !is_array($data['field_group_refs'] ?? null)
            || !is_array($data['values'] ?? null)
            || $this->contains_php_serialization($data['values'])) {
            throw new InvalidArgumentException('ACF values contract is invalid.');
        }
        foreach ($data['field_group_refs'] as $reference) {
            if (!is_string($reference) || !str_starts_with($reference, 'acf_field_group:')) {
                throw new InvalidArgumentException('ACF field-group reference is invalid.');
            }
        }
    }

    /** @param array<string, mixed> $object
     *  @return array<string, mixed>
     */
    public function managed_view(array $object): array
    {
        $object = $this->validate_object($object);
        $fields = $object['managed_fields'];
        sort($fields, SORT_STRING);
        $data = [];
        foreach ($fields as $field) {
            $data[$field] = $object['data'][$field];
        }
        $references = $object['references'];
        sort($references, SORT_STRING);
        return [
            'schema_version' => 1,
            'serializer' => self::SERIALIZER,
            'identity' => $object['object_type'] . ':' . $object['object_key'],
            'object_type' => $object['object_type'],
            'object_key' => $object['object_key'],
            'ownership' => $object['ownership'],
            'managed_fields' => $fields,
            'data' => $data,
            'references' => $references,
            'state' => $object['state'],
            'tombstone' => $object['tombstone'],
        ];
    }

    /** @param array<string, mixed> $object */
    public function managed_digest(array $object): string
    {
        return $this->digest($this->managed_view($object));
    }
}
