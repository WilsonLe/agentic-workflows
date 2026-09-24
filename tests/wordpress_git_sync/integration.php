<?php

use AMSoft\WordPressGitSync\Canonicalizer;
use AMSoft\WordPressGitSync\Rest_Controller;

if (!defined('ABSPATH')) {
    fwrite(STDERR, "WordPress is not loaded.\n");
    exit(2);
}

function integration_assert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

function integration_request(string $method, array $route, array $payload): WP_REST_Request
{
    $request = new WP_REST_Request($method, '/amsoft/v1/integration');
    foreach ($route as $key => $value) {
        $request->set_param($key, $value);
    }
    $request->set_header('content-type', 'application/json');
    $request->set_body((string) wp_json_encode($payload));
    return $request;
}

$page_id = wp_insert_post([
    'post_type' => 'page',
    'post_title' => 'Integration before',
    'post_content' => '<!-- wp:paragraph --><p>Before.</p><!-- /wp:paragraph -->',
    'post_excerpt' => 'Before.',
    'post_name' => 'integration-sync',
    'post_status' => 'publish',
], true);
integration_assert(!is_wp_error($page_id), 'Could not create disposable page.');

$entry = [
    'object_type' => 'page',
    'object_key' => 'page:integration-sync',
    'post_id' => (int) $page_id,
    'managed_fields' => ['title', 'content', 'excerpt', 'slug', 'status', 'template'],
    'remote_fields' => ['author_ref', 'date_gmt'],
    'ownership' => 'shared-guarded',
    'classification' => 'public',
    'adapter_config' => [],
];
update_option(Rest_Controller::REGISTRY_OPTION, ['page:page:integration-sync' => $entry], false);

$controller = new Rest_Controller(new Canonicalizer());
$route = ['object_type' => 'page', 'object_key' => 'page:integration-sync'];
$get = $controller->get_object(integration_request('GET', $route, []));
integration_assert($get instanceof WP_REST_Response, 'Initial read did not return a REST response.');
$before = $get->get_data();
integration_assert($before['guard'] === 'atomic-compare-and-swap', 'Atomic guard is absent.');

$desired = $before['object'];
$desired['data']['title']['raw'] = 'Integration after';
$desired['data']['content']['raw'] = '<!-- wp:paragraph --><p>After.</p><!-- /wp:paragraph -->';
$contract_mismatch = $desired;
$contract_mismatch['ownership'] = 'git';
$mismatch_payload = [
    'schema_version' => 1,
    'object' => $contract_mismatch,
    'expected_sha256' => $before['sha256'],
    'expected_revision' => $before['revision'],
    'idempotency_key' => 'docker-integration-mismatch',
    'dry_run' => true,
];
$mismatch = $controller->apply_object(integration_request('POST', $route, $mismatch_payload));
integration_assert(is_wp_error($mismatch), 'Ownership contract mismatch unexpectedly succeeded.');
integration_assert($mismatch->get_error_code() === 'amsoft_contract_mismatch', 'Ownership mismatch returned the wrong error.');
$payload = [
    'schema_version' => 1,
    'object' => $desired,
    'expected_sha256' => $before['sha256'],
    'expected_revision' => $before['revision'],
    'idempotency_key' => 'docker-integration-0001',
    'dry_run' => true,
];
$dry_run = $controller->apply_object(integration_request('POST', $route, $payload));
integration_assert($dry_run instanceof WP_REST_Response, 'Dry run failed.');
integration_assert($dry_run->get_data()['dry_run'] === true, 'Dry run mutated its contract.');
integration_assert(get_post((int) $page_id)->post_title === 'Integration before', 'Dry run changed WordPress.');

$payload['dry_run'] = false;
$applied = $controller->apply_object(integration_request('POST', $route, $payload));
integration_assert($applied instanceof WP_REST_Response, 'Guarded apply failed.');
integration_assert($applied->get_data()['idempotent_replay'] === false, 'First apply was marked as replay.');
integration_assert(get_post((int) $page_id)->post_title === 'Integration after', 'Apply was not read back.');

$replayed = $controller->apply_object(integration_request('POST', $route, $payload));
integration_assert($replayed instanceof WP_REST_Response, 'Idempotent replay failed.');
integration_assert($replayed->get_data()['idempotent_replay'] === true, 'Replay was not recognized.');

$payload['idempotency_key'] = 'docker-integration-stale';
$stale = $controller->apply_object(integration_request('POST', $route, $payload));
integration_assert(is_wp_error($stale), 'Stale apply unexpectedly succeeded.');
integration_assert($stale->get_error_code() === 'amsoft_stale_remote', 'Stale apply returned the wrong error.');

$queue_before = get_option(Rest_Controller::EVENT_QUEUE_OPTION, []);
Rest_Controller::capture_managed_save((int) $page_id, get_post((int) $page_id), true);
$queue_after = get_option(Rest_Controller::EVENT_QUEUE_OPTION, []);
integration_assert(count($queue_after) === count($queue_before) + 1, 'Public editor save was not queued.');
$event = array_values($queue_after)[0];
$actual_event_keys = array_keys($event);
$expected_event_keys = [
    'schema_version', 'event', 'site_key', 'environment', 'identity',
    'correlation_id', 'actor', 'autosave', 'revision', 'classification',
];
sort($actual_event_keys);
sort($expected_event_keys);
integration_assert($actual_event_keys === $expected_event_keys, 'Queued event differs from the automation contract.');

$attachment_id = wp_insert_attachment([
    'post_title' => 'Synthetic integration media',
    'post_excerpt' => 'Media before.',
    'post_name' => 'integration-media',
    'post_status' => 'inherit',
    'post_mime_type' => 'image/png',
], false, 0, true);
integration_assert(!is_wp_error($attachment_id), 'Could not create disposable attachment.');
$media_meta = [
    '_amsoft_media_logical_id' => 'images/integration-media',
    '_amsoft_media_source_sha256' => str_repeat('1', 64),
    '_amsoft_media_bytes' => 1024,
    '_amsoft_media_width' => 100,
    '_amsoft_media_height' => 100,
    '_wp_attachment_image_alt' => 'Media before.',
    '_amsoft_media_credit' => 'Synthetic fixture',
    '_amsoft_media_license' => 'MIT',
    '_amsoft_media_storage' => ['kind' => 'release-artifact', 'locator' => 'release://integration/media.png'],
    '_amsoft_media_status' => 'available',
];
foreach ($media_meta as $meta_key => $meta_value) {
    update_post_meta((int) $attachment_id, $meta_key, $meta_value);
}
$registry = get_option(Rest_Controller::REGISTRY_OPTION, []);
$media_entry = [
    'object_type' => 'attachment',
    'object_key' => 'images:integration-media',
    'post_id' => (int) $attachment_id,
    'managed_fields' => [
        'logical_id', 'source_sha256', 'mime_type', 'bytes', 'width', 'height',
        'alt_text', 'caption', 'credit', 'license', 'storage', 'status',
    ],
    'remote_fields' => [],
    'ownership' => 'manifest',
    'classification' => 'public',
    'adapter_config' => [],
];
$registry['attachment:images:integration-media'] = $media_entry;
update_option(Rest_Controller::REGISTRY_OPTION, $registry, false);
$media_route = ['object_type' => 'attachment', 'object_key' => 'images:integration-media'];
$media_get = $controller->get_object(integration_request('GET', $media_route, []));
integration_assert($media_get instanceof WP_REST_Response, 'Attachment read did not return a REST response.');
$media_before = $media_get->get_data();
$media_desired = $media_before['object'];
$media_desired['data']['source_sha256'] = str_repeat('2', 64);
$media_desired['data']['mime_type'] = 'image/webp';
$media_desired['data']['bytes'] = 2048;
$media_desired['data']['alt_text'] = 'Media after.';
$media_desired['data']['caption']['raw'] = 'Media after.';
$media_payload = [
    'schema_version' => 1,
    'object' => $media_desired,
    'expected_sha256' => $media_before['sha256'],
    'expected_revision' => $media_before['revision'],
    'idempotency_key' => 'docker-integration-media-0001',
    'dry_run' => false,
];
$media_applied = $controller->apply_object(integration_request('POST', $media_route, $media_payload));
integration_assert($media_applied instanceof WP_REST_Response, 'Attachment guarded apply failed.');
$media_readback = $media_applied->get_data()['readback']['object']['data'];
integration_assert($media_readback['status'] === 'available', 'Attachment availability was treated as post status.');
integration_assert($media_readback['caption']['raw'] === 'Media after.', 'Attachment caption did not round-trip.');
integration_assert($media_readback['mime_type'] === 'image/webp', 'Attachment MIME type did not round-trip.');

fwrite(STDOUT, wp_json_encode([
    'ok' => true,
    'wordpress' => get_bloginfo('version'),
    'php' => PHP_VERSION,
    'identity' => $before['identity'],
    'before_sha256' => $before['sha256'],
    'after_sha256' => $applied->get_data()['after_sha256'],
    'media_after_sha256' => $media_applied->get_data()['after_sha256'],
    'guard' => $before['guard'],
]) . "\n");
