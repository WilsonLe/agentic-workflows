<?php
/**
 * Plugin Name: AMSoft WordPress Git Sync
 * Description: Guarded managed-object registry and atomic compare-and-swap REST runtime.
 * Version: 0.1.0
 * Requires at least: 6.6
 * Requires PHP: 8.1
 * Author: AMSoft
 * License: LicenseRef-AMSoft-Proprietary
 */

declare(strict_types=1);

namespace AMSoft\WordPressGitSync;

if (!defined('ABSPATH')) {
    exit;
}

define('AMSOFT_WORDPRESS_GIT_SYNC_VERSION', '0.1.0');
define('AMSOFT_WORDPRESS_GIT_SYNC_FILE', __FILE__);

require_once __DIR__ . '/includes/class-amsoft-sync-canonicalizer.php';
require_once __DIR__ . '/includes/class-amsoft-sync-rest-controller.php';

add_action('rest_api_init', static function (): void {
    (new Rest_Controller(new Canonicalizer()))->register_routes();
});

add_action('save_post', [Rest_Controller::class, 'capture_managed_save'], 20, 3);

register_activation_hook(__FILE__, static function (): void {
    if (get_option(Rest_Controller::REGISTRY_OPTION, null) === null) {
        add_option(Rest_Controller::REGISTRY_OPTION, [], '', false);
    }
    if (get_option(Rest_Controller::IDEMPOTENCY_OPTION, null) === null) {
        add_option(Rest_Controller::IDEMPOTENCY_OPTION, [], '', false);
    }
    if (get_option(Rest_Controller::EVENT_QUEUE_OPTION, null) === null) {
        add_option(Rest_Controller::EVENT_QUEUE_OPTION, [], '', false);
    }
});
