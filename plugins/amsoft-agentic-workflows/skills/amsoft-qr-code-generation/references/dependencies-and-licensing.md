# Dependencies and licensing

QR Code Generation uses replaceable runtime adapters and does not copy
third-party source into the plugin.

| Dependency | Pinned version | Role | Upstream license/notice |
| --- | --- | --- | --- |
| Segno | 1.6.6 | Deterministic QR encoding and SVG/PNG rendering | BSD 3-Clause; the installed distribution carries its copyright and disclaimer |
| Pillow | 11.3.0 | Bounded raster loading, logo composition, and background compositing | MIT-CMU License; Pillow distributions also carry notices for bundled codec libraries |
| zxing-cpp | 2.3.0 | Independent QR decode verification | Apache License 2.0 for the Python binding/library; wheel-provided native notices remain authoritative |

The installation contract is the repository root pyproject.toml plus
uv.lock, with Python 3.12 and uv sync --locked. The helper imports only
the pinned packages, never calls a provider, and never uses the network.

When redistributing or rebuilding the runtime, retain the license and notice
files supplied by each dependency distribution. The AMSoft proprietary license
covers only this plugin's authored files and does not replace third-party
terms.
