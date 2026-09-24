# Encrypted transfer contract

## Supported data

Version 1 transfers exactly:

- preferred workflow IDs;
- one optional default workflow ID;
- one optional BCP 47-style response-language tag;
- Railway account-token credentials;
- Cloudflare scoped user/account API-token credentials;
- DigitalOcean personal access-token credentials.

Provider command configuration, account/resource IDs, paths, environment variables, logs, caches,
CLI YAML, arbitrary plugin settings, and free-form fields are excluded.

## Envelope

`.agenticx` is strict UTF-8 JSON. Visible fields identify the fixed format/envelope version, origin
plugin, mode, KDF parameters, cipher, nonce, and ciphertext. The encrypted payload uses its own
strict schema version. Unknown or missing fields fail closed.

Portable mode normalizes the passphrase with Unicode NFKC, derives a 256-bit key with the
versioned scrypt parameters in the envelope, and encrypts with AES-256-GCM. Local-session mode uses
a random 256-bit OS-user key. Canonical visible metadata is authenticated as associated data.
Any metadata, nonce, tag, or ciphertext modification makes authentication fail before parsing.

The implementation uses a pinned `cryptography` runtime dependency. It does not implement a cipher
or KDF itself.

## Mode compatibility

`local-session` is a convenience mode:

- macOS uses a Keychain item belonging to the current OS user;
- Windows uses a CurrentUser DPAPI-protected local key;
- another OS user or machine cannot decrypt the file.

`portable-passphrase` is the cross-machine and cross-OS mode. macOS and Windows use identical
UTF-8, Unicode normalization, canonical JSON, scrypt, and AES-GCM rules. No OS path or key-store
reference enters the encrypted payload.

There is no universal plugin key, self-decrypting export, plaintext mode, automatic cross-machine
fallback, or passphrase recovery. Losing the passphrase makes a portable export unrecoverable.

## Import transaction

Import authenticates and validates the complete file before changing local state. It creates
protected snapshots, stages allowlisted preferences and credential records, then verifies every
included provider through read-only identity/account calls. All staged values commit only when all
verifications succeed. Any provider failure restores the entire prior local state.

Import does not install plugins or dependencies other than the helper's declared runtime
dependency. Both sessions must already have compatible central-plugin versions.

## Secret handling

The passphrase is accepted only through a masked native prompt or a user-controlled terminal
`getpass` prompt. It never belongs in chat, argv, environment variables, logs, screenshots, Git,
or the export. Decrypted payloads and provider tokens are never emitted. Output may contain only
provider names, credential types, preference field names, status, and sanitized errors.

Treat every `.agenticx` file as a sensitive encrypted credential backup: restrict access, transmit
it only through intended channels, and delete it separately when no longer needed.
