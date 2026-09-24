# QR Code Generator

The QR Code Generator plugin creates deterministic QR assets from an exact
payload, applies bounded visual themes, and verifies the final PNG with a real
decoder before reporting it as usable.

## What it does

- Preserves the exact UTF-8 payload without URL rewriting, trimming, tracking
  parameters, or shortening.
- Produces deterministic SVG and PNG QR assets with a documented four-module
  quiet zone and explicit error-correction level.
- Applies safe built-in themes (`minimal`, `editorial`, `botanical`, `night`,
  and `festival`) or a validated custom palette.
- Keeps the QR matrix and finder patterns under deterministic renderer control.
- Optionally composes a user-authorized or host-generated background outside
  the QR safe area.
- Verifies PNG output with ZXing-C++ and reports the decoded payload digest.
- Emits secret-safe JSON manifests and explicit unavailable/rejected states.

## Image generation boundary

The host image capability may create a background, frame, texture, or palette
direction. It never creates the QR modules, finder patterns, encoded text, or
the final scanability claim. Image prompts use `[QR SAFE AREA]` by default and
must not contain the raw payload, credentials, private identifiers, OTPs, or
tokens. The deterministic helper composites the verified QR after any optional
image-generation step.

## Helper

The local helper is:

```text
plugins/qr-code-generator/scripts/qr_code_generator.py
```

The repository validation environment pins Segno for encoding, Pillow for
bounded raster composition, and ZXing-C++ for decode verification. The helper
does not call a provider or perform network access.
Dependency versions, upstream licenses, and the uv sync --locked installation
contract are recorded in the skill's dependencies-and-licensing.md reference.

Example request:

```json
{
  "schema_version": 1,
  "qr_id": "menu-qr",
  "payload_type": "url",
  "payload": "https://example.com/menu?source=table",
  "output": {"format": "png", "scale": 8, "border": 4},
  "error_correction": "H",
  "style": {"theme": "botanical"},
  "privacy": {"allow_raw_payload_in_manifest": false}
}
```

Run the helper from the repository root with an isolated output directory:

```bash
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  validate --input /absolute/path/to/request.json
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  render --input /absolute/path/to/request.json \
  --output-dir /absolute/path/to/output
```

`render` returns a JSON manifest. It does not print the payload. A result is
`verified` only when a real decoder returns the exact original UTF-8 payload;
decoder-unavailable and decode-mismatch are not success states.

## Package boundary

This plugin stores no redirects, analytics, customer data, credentials, hosted
QR state, generated binary fixtures, or provider configuration. It does not
publish, print, upload, or deploy assets. Roll back by reinstalling the prior
marketplace package version.
