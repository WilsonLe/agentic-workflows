# Verification and recovery

## Verification states

- `verified`: the final PNG decoded and its UTF-8 text hashes to the expected
  payload digest.
- `verification_unavailable`: no real decoder is installed or the requested
  decoder channel could not run.
- `decode_mismatch`: a decoder returned different content.
- `geometry_failure`: size, quiet zone, or safe-area rules failed.
- `style_rejected`: the theme contains unsafe colors or unsupported features.
- `image_capability_unavailable`: optional host image generation did not run.
- `failed_recoverable`: the variant failed but the baseline remains available.

Never collapse these states into a generic successful file-write message.

## Recovery

- Keep the first verified baseline immutable for the task.
- Write each variant to a new path and reject collisions.
- If a theme or logo fails, remove only the task-owned temporary output and
  return the baseline plus the failure reason.
- Do not blindly retry an unknown image-provider result. Inspect the output and
  reuse the exact generated input when the host workflow permits it.
- A manifest records output digests and the decoder evidence channel, not a
  claim that a QR is usable everywhere.

## Evidence limits

Decoder evidence proves payload readability for the tested output and device-
independent decoder. It does not prove every camera, print process, distance,
lighting condition, or production surface. When a user needs a printed asset,
recommend a real scan check at the intended size and viewing distance.
