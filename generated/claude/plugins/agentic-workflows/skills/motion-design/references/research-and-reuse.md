# Research and reuse

Inspected 11 October 2026. These are reference implementations and documentation,
not behavioral authority for the user's project. Pin any borrowed implementation,
check its current license, and retain required notices. Our instructions and
starter are original; no upstream renderer is vendored.

| Source | Useful responsibility | Adaptation boundary |
| --- | --- | --- |
| [HyperFrames](https://github.com/heygen-com/hyperframes/tree/64c47cf3d1b00aa6dd76a3d40256f235654eacb1) | Existing HTML-to-video engine and runtime adapters, Apache-2.0 | Reuse the renderer; do not import its broad routing, global updates, or provider workflows to create one video |
| [Howseen motion design](https://github.com/howseen-ai/claude-motion-design/tree/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f) | Seek-driven Playwright capture, draft/master review, subframe blur and seam probes, MIT | Project paths, brand rules, preferences, and approval pauses are author-specific; its template is not a portable CLI |
| [Whaley Claude Motion](https://github.com/whaleyxbt/claude-motion/tree/e627941543d9988b155dc610bb9cc0115a5e365e) | Shared visual/audio timeline, precomputed simulations and contact-sheet review, MIT | Its capture script needs stronger browser/encoder failure handling before direct reuse |
| [Canvas motion skill](https://github.com/abhimahamkali/claude-motion-skill/tree/37d44b5d2db8e28c4ebf011cb8f1bd1e260ac09c) | Compact analogy/storyboard/still-review workflow | No standalone license file was found at the inspected revision; consult the author before copying code |
| [Bang Motion](https://github.com/bangtutorial/bang-motion/tree/c1aa65e921c970d858705fcb4a53a8294d1a4131) | Choreography and seek-driven Puppeteer frame export, MIT | Tailor art direction and avoid importing an unrelated After Effects bridge |
| [Official GSAP skills](https://github.com/greensock/gsap-skills/tree/aed9cfd3277740755f6bfc1155c7aa645403b760) | Correct timeline, SVG, easing and plugin APIs | Supporting knowledge, not a finished-video workflow |
| [Remotion skills](https://www.remotion.dev/docs/ai/skills) | React compositions, rendering and captions | Good when the project already uses React video templates; inspect the current Remotion license |

Primary contracts:

- [HyperFrames frame adapters](https://hyperframes.heygen.com/concepts/frame-adapters)
- [HyperFrames rendering](https://hyperframes.heygen.com/guides/rendering)
- [Playwright screenshots](https://playwright.dev/docs/screenshots) and [videos](https://playwright.dev/docs/videos)
- [GSAP timelines](https://gsap.com/docs/v3/GSAP/Timeline/)
- [Anime.js seek](https://animejs.com/documentation/timeline/timeline-methods/seek/)
- [WAAPI currentTime](https://developer.mozilla.org/en-US/docs/Web/API/Animation/currentTime)
- [FFmpeg formats](https://ffmpeg.org/ffmpeg-formats.html)
