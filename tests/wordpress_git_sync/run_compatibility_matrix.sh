#!/usr/bin/env bash
set -euo pipefail

test_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

matrix=(
  "wordpress:6.6-php8.1-apache|wordpress:cli-2.12.0-php8.1"
  "wordpress:6.7-php8.2-apache|wordpress:cli-2.12.0-php8.2"
  "wordpress:6.8-php8.4-apache|wordpress:cli-2.12.0-php8.4"
  "wordpress:6.9-php8.3-apache|wordpress:cli-2.12.0-php8.3"
)

for entry in "${matrix[@]}"; do
  wordpress_image="${entry%%|*}"
  cli_image="${entry##*|}"
  echo "Testing $wordpress_image with $cli_image"
  WORDPRESS_IMAGE="$wordpress_image" WORDPRESS_CLI_IMAGE="$cli_image" \
    "$test_dir/run_disposable_wordpress.sh"
done
