# Chrome Extensions

Build, change, debug, and prepare Manifest V3 extensions with two shared workflows:

- [Chrome extensions](skills/chrome-extensions/SKILL.md): execution contexts, permissions,
  security, an offline manifest audit, Chrome runtime verification, and Web Store records.
- [Modern Web Guidance](skills/modern-web-guidance/SKILL.md): current web API selection,
  compatibility and fallbacks, accessibility, performance, and built-in AI lifecycle.

These are original Agentic Workflows instructions inspired by
[Chrome's build-with-agents guide](https://developer.chrome.com/docs/extensions/ai/build-with-ai#modern_web_guidance).
They do not redistribute or auto-update Google's upstream skill pack. The companion skill
documents Google's installer when upstream installation is explicitly requested.

## Install and use

After adding the `wilsonle/agentic-workflows` marketplace to your host:

```sh
codex plugin add chrome-extensions@agentic-workflows
# Or in Claude Code:
claude plugin install chrome-extensions@agentic-workflows
```

Start a fresh task/session and invoke `$chrome-extensions` or `$modern-web-guidance`.
Examples: “Build a quick-notes popup with local storage and test it in Chrome”,
“Diagnose worker state loss after suspension”, or “Prepare this extension for store review”.

## Tools and evidence

Python 3.10+ runs the optional, dependency-free audit:

```sh
python3 <installed-skill-root>/scripts/audit_extension.py /absolute/path/to/unpacked-extension
```

Replace `<installed-skill-root>` with the installed `chrome-extensions` skill directory.
The JSON result inventories all four permission fields and reports selected MV3, version,
packaged-file, and CSP problems. Exit 1 indicates errors; exit 0 covers only those static
checks. It never executes extension code or verifies Chrome behavior, full manifest validity,
Web Store policies, or every referenced asset. Review warnings separately.

For actual browser tests, configure optional Chrome DevTools MCP using
[the setup and testing guide](skills/chrome-extensions/references/devtools-testing.md).
It covers isolated profiles, version-dependent existing-profile connections, tool discovery,
and loading/reloading the exact build. Installation does not configure MCP or change a browser.
No runtime/model test is claimed by package validation alone.

Create or update `CHROMEWEBSTORE.md` in the target extension project, using
[the template](skills/chrome-extensions/templates/CHROMEWEBSTORE.md) where appropriate.
Keep permission rationales and data practices consistent with actual behavior. Store preparation,
upload, submission, and publication are distinct outcomes; external release actions require
explicit user authority. Run the target repository's own engineering checks as well.

For the full path from publisher setup to submission, Google's decision, and verified publication,
follow [the Chrome Web Store review and approval checklist](skills/chrome-extensions/references/web-store-review.md).
