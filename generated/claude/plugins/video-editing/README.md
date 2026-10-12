# Video Editing

Storyboard and edit footage, images, animated scenes and sound with one timeline.
This source component is included in the complete Agentic Workflows bundle:

- [Video Editing](skills/video-editing/SKILL.md): storyboards, local asset indexing,
  reference breakdowns, cuts, blending, transitions, keyframes and final review.
- [Speech-to-Text](skills/speech-to-text/SKILL.md): searchable source-timed transcripts
  and caption handoffs.
- [Text-to-Speech](skills/text-to-speech/SKILL.md): narration takes, pronunciation,
  voice provenance and measured timing.
- [Audio Editing](skills/audio-editing/SKILL.md): restoration, EQ/dynamics,
  automation, spatial processing, stem/mix delivery and loudness evidence.
- [Typography](skills/typography/SKILL.md): static font discovery/downloads, labeled
  indexes, size/formatting, shaping and readable titles/captions.
- [Motion Design](skills/motion-design/SKILL.md) and
  [Music Composition](skills/music-composition/SKILL.md): existing scene rendering,
  video verification and editable score synthesis, mirrored from their owners.

Install the one `agentic-workflows` marketplace plugin for Codex or Claude Code;
OpenCode V2 uses the generated portable bundle. See the root README for host setup.
This directory is a maintained source component, not a second marketplace listing.
Invoke `$video-editing` (or `@video-editing` in OpenCode V2); individual speech,
audio and typography workflows also work independently.

Python 3.10+ and ffprobe run the local media index helper. Editing needs an existing
editor or FFmpeg; animated shots use Motion Design's pinned rendering runtime.
Speech and font operations use selected existing runtimes/models and font tools;
the plugin installs no models, voices, fonts or services. Local options and official
tool references live in the corresponding skills. Network/cloud/paid actions retain
their own scoped authority.

The helper creates a technical index; editorial labels, transcripts and font records
remain distinct assets. Finished video delivery includes the edit/timeline, indexed
assets, font provenance, speech sidecars and stems when relevant. Package checks do
not establish speech accuracy, voice quality, licensed asset use or final playback.
