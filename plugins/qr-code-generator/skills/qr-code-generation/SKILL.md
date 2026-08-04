---
name: qr-code-generation
description: Create exact-payload QR codes with deterministic safe themes, optional image-generation-assisted backgrounds, secret-safe manifests, and real decoder verification. Use when the user asks for a QR code, styled or branded QR, themed QR asset, menu QR, Wi-Fi QR, vCard QR, or an image-generation-assisted QR concept.
---

# QR Code Generation

Use the local QR helper for payload encoding, deterministic rendering,
compositing, and verification. Use the host image capability only for an
optional decorative theme or background. The image model never owns the QR
matrix and never establishes scanability.

Read the relevant references before the first operation:

- [payload and privacy](references/payload-and-privacy.md)
- [style and theme contract](references/style-and-theme-contract.md)
- [image generation and compositing](references/image-generation-and-compositing.md)
- [verification and recovery](references/verification-and-recovery.md)
- [dependencies and licensing](references/dependencies-and-licensing.md)

## Operating boundary

- Preserve the exact user payload. Do not trim, normalize, shorten, rewrite,
  append tracking parameters, or infer missing URL/text content.
- Encode the exact UTF-8 payload and retain its SHA-256 digest as the identity
  used by manifests and verification.
- Keep raw payloads out of prompts, logs, issue comments, examples, and evidence
  by default. Treat URLs containing tokens, passwords, OTPs, private identifiers,
  and credential-shaped strings as sensitive.
- Use the helper's deterministic renderer before any theme or image-generation
  step. Keep the verified baseline when a visual variant fails.
- Keep at least the standard four-module quiet zone. Do not overlay generated
  artwork, text, ornaments, logos, gradients, or shadows over the quiet zone,
  finder patterns, timing patterns, alignment patterns, or data modules.
- Use only user-authorized or appropriately licensed logos/background references.
  Do not scrape or download an online image merely because it looks suitable.
- Never call a theme preview `scannable`, `production-ready`, or `verified`
  until a real decoder reads the exact payload from the final raster.

## Required workflow

1. Confirm the exact payload, payload type, output purpose, format, dimensions or
   scale, error-correction level, target surface, viewing distance, lighting,
   and whether a logo or image-generation-assisted theme is requested.
2. If the payload is sensitive, keep it local and explain that it will not be
   sent to the image capability. Ask only for the additional consent needed for
   a local output manifest that includes raw payload text.
3. Build a request JSON using schema v1. Prefer `url` for a URL and `text` for
   arbitrary text; `wifi`, `vcard`, and `custom` describe the payload semantics
   but do not rewrite the exact string.
4. Run `validate` before writing. Reject unsafe paths, unsupported formats,
   invalid colors, excessive dimensions, missing output settings, and a logo
   without suitable error correction.
5. Run `render` to create and verify the deterministic baseline. Read the JSON
   manifest and confirm the state is `verified` for a PNG or
   `verification_unavailable` when the decoder is not available. Do not hide a
   failed verification behind a successful file write.
6. Resolve a built-in or custom theme. Version 1 keeps modules square and
   changes only tested colors, finder treatment, frame, and surrounding
   composition. Prefer a high-contrast baseline when the output surface is
   unknown.
7. If image generation is requested, prepare a prompt containing visual theme
   instructions and the literal placeholder `[QR SAFE AREA]`. Never include the
   raw payload or private URL values. Call the host image capability for a new
   background or theme direction only after the baseline is verified.
8. Run `compose` with the approved background. The helper places the unchanged
   QR image in a protected opaque safe area and keeps the generated artwork
   outside it. Do not accept an image-model output that contains its own QR.
9. Run `verify` against the final manifest. Compare decoded UTF-8 text and its
   digest to the original payload digest. If the result is a mismatch, reject
   the variant and preserve the baseline.
10. Deliver the verified asset, secret-safe manifest, final style/theme
    description, decoder evidence, and any limitation. Label image-generation
    concepts separately from verified QR outputs.

## Helper commands

From the repository root:

```text
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  validate --input /absolute/path/request.json
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  render --input /absolute/path/request.json --output-dir /absolute/path/output
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  compose --input /absolute/path/request.json \
  --qr /absolute/path/output/verified.png \
  --background /absolute/path/background.png \
  --output-dir /absolute/path/output
python plugins/qr-code-generator/scripts/qr_code_generator.py \
  verify --input /absolute/path/output/manifest.json
```

The helper has no provider client and performs no network access. It emits
structured JSON and never prints the raw payload in normal output.
The pinned real decoder for v1 is ZXing-C++.

## Theme routing

- `minimal` is the default when no visual brief is supplied.
- `editorial` suits restrained ink/paper brand systems.
- `botanical` suits natural, warm backgrounds outside the safe area.
- `night` uses a light QR field against a dark surrounding composition.
- `festival` uses a bold accent and decorative frame without touching the QR.
- A custom theme must specify colors, border, quiet zone, scale, background
  behavior, and whether image generation is allowed.

Do not promise that an arbitrary module shape, transparency, gradient, tiny
output, or logo will scan. Add a tested renderer extension before offering it.

## Review gate

Reject or revise when:

- the decoded text differs from the exact payload;
- the decoder is unavailable but the result is labelled verified;
- a quiet zone is missing or covered;
- a background, logo, shadow, gradient, or text changes a functional pattern;
- foreground/background contrast is weak or the output is too small for its use;
- a generated background contains a second QR or misleading encoded text;
- a manifest contains an unauthorized raw payload, token, password, or private
  identifier;
- a failed variant replaced the last verified baseline.

## Delivery

Return:

- the verified PNG and/or SVG output;
- the secret-safe manifest and payload digest;
- the selected theme and resolved style tokens;
- decoder name/version and exact verification state;
- the image-generation prompt or prompt digest only when it is safe to share;
- explicit limitations, rejected variants, and a recovery recommendation.
