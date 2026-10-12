# Payload and privacy

## Exact payload

The payload is an exact UTF-8 string. The helper must encode the supplied string
without trimming whitespace, changing Unicode normalization, adding a scheme,
rewriting a query string, shortening a URL, or appending analytics parameters.
`payload_sha256` is the SHA-256 digest of those exact UTF-8 bytes.

`payload_type` is descriptive metadata. It may be `text`, `url`, `wifi`,
`vcard`, or `custom`, but it never authorizes a formatter to rewrite the
payload. If a user wants a Wi-Fi or vCard payload assembled from fields, first
show the exact resulting string and obtain approval before rendering it.

## Sensitive values

QR codes can encode private URLs, Wi-Fi passwords, access tokens, OTPs, account
identifiers, or customer information. Treat a payload as sensitive when its
purpose or content suggests private access or identity.

- Do not send sensitive payload text to an image model.
- Do not print it in normal CLI output, logs, issue comments, PR descriptions,
  examples, or validation evidence.
- Store only its digest in default manifests.
- Allow raw payload storage only in an explicitly requested, local, authorized
  output directory. Never commit that file.
- Never accept a credential as a plugin configuration value or ask the user to
  paste a secret into chat merely to generate a QR.

## Output identity

Manifests identify outputs with `qr_id`, `variant_id`, source payload digest,
encoder version, resolved style, output digest, and decoder evidence. A file
path alone is not proof that it belongs to a payload. A successful render is
not proof that the asset decodes.

## Safe examples

Repository examples must use synthetic values such as
`https://example.com/menu?source=table` and must not contain real customer,
restaurant, Wi-Fi, credential, or private URL data.
