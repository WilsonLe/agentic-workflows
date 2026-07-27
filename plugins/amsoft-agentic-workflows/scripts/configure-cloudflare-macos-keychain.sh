#!/bin/zsh

set -eu

if [[ "$(uname -s)" != "Darwin" ]]; then
  print -u2 "This setup script is for macOS. Use CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID on other systems."
  exit 1
fi

read "cloudflare_account_id?Cloudflare account ID (32 hex characters): "
if [[ ! "$cloudflare_account_id" =~ ^[A-Fa-f0-9]{32}$ ]]; then
  print -u2 "Invalid Cloudflare account ID."
  exit 1
fi

/usr/bin/security add-generic-password \
  -U \
  -s "codex-cloudflare-account-id" \
  -a "default" \
  -l "Codex Cloudflare account ID" \
  -w "$cloudflare_account_id"

print "Enter the Cloudflare account API token in the macOS Keychain prompt."
/usr/bin/security add-generic-password \
  -U \
  -s "codex-cloudflare-account" \
  -a "$cloudflare_account_id" \
  -l "Codex Cloudflare account API token" \
  -w

unset cloudflare_account_id
print "Cloudflare credentials saved in macOS Keychain. Restart Codex and open a new task."
