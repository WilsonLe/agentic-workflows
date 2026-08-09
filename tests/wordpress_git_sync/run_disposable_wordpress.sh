#!/usr/bin/env bash
set -euo pipefail

test_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
compose_file="$test_dir/docker-compose.yml"
project_name="amsoft-wp-git-sync-${RANDOM}-${RANDOM}"

cleanup() {
  docker compose --project-name "$project_name" --file "$compose_file" down --volumes --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM

docker compose --project-name "$project_name" --file "$compose_file" up --detach db wordpress

ready=0
for _attempt in $(seq 1 60); do
  if docker compose --project-name "$project_name" --file "$compose_file" run --rm cli wp core is-installed >/dev/null 2>&1; then
    ready=1
    break
  fi
  if docker compose --project-name "$project_name" --file "$compose_file" run --rm cli wp db check >/dev/null 2>&1; then
    printf '%s\n' 'disposable-test-only' | docker compose --project-name "$project_name" --file "$compose_file" run --rm -T cli wp core install \
      --url=http://wordpress --title='AMSoft Sync Integration' --admin_user=integration \
      --admin_email=integration@example.invalid --skip-email --prompt=admin_password >/dev/null
  fi
  sleep 1
done

if [[ "$ready" != "1" ]]; then
  echo "Disposable WordPress did not become ready." >&2
  exit 1
fi

docker compose --project-name "$project_name" --file "$compose_file" run --rm cli wp plugin activate amsoft-wordpress-git-sync >/dev/null
docker compose --project-name "$project_name" --file "$compose_file" run --rm cli wp eval-file /integration/integration.php
