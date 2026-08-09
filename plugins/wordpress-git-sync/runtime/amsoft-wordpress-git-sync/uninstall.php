<?php

declare(strict_types=1);

if (!defined('WP_UNINSTALL_PLUGIN')) {
    exit;
}

// Managed-object registry, idempotency evidence, and queued events are retained by default.
// Destructive removal requires a separately reviewed operator action and recovery evidence.
