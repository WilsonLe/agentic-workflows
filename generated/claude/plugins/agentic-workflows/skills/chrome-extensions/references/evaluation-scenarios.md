# Evaluation scenarios

Run these prompts in a fresh host with the plugin discoverable. Record observed routing,
files, checks, and tool outcomes. No runtime evaluation is claimed by these scenarios.

| Prompt | Expected behavior | Failure to catch |
| --- | --- | --- |
| Build a quick-notes popup that persists locally | MV3, justified storage, saved state, store record, build and Chrome checks | In-memory persistence or declaring success from manifest alone |
| Add a side panel to my extension | Verify API/version, sidePanel permission, accessible behavior, metadata update | Unnecessary all-site access |
| My worker loses state after it sleeps | Reproduce restart, durable storage, top-level listeners | Keeping the worker alive to hide the defect |
| Test this in my signed-in Chrome | Identify authorized profile, verify connection/tool capabilities, retain native approval | Assuming autoConnect supports every extension tool |
| Summarize page text with built-in AI | Check chosen API/context, availability, downloads, cancellation, fallback and disclosures | Cloud fallback without consent or calling a DOM-only API in a worker |
| Prepare this for the store | Truthful listing and per-permission/privacy reconciliation | Uploading or claiming approval without authority/evidence |
| Use a new CSS API in a popup | Check target compatibility and fallback; keyboard/narrow-size checks | Assuming Baseline covers extension APIs |
