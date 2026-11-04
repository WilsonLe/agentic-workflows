# Built-in AI availability and lifecycle

Choose an API for the task before coding: the Prompt, Summarizer, Translator, Language
Detector, Writer, Rewriter, and other APIs have separate availability, language, device,
model, and execution-context constraints. Read the current API-specific documentation
linked from [Chrome's AI entry point](https://developer.chrome.com/docs/ai/get-started).
Never assume a generic `window.ai` sample or a global present in a page works in an extension
worker or content script. Verify the precise global and context; use an extension page or
other documented context when the chosen API is unsupported in the worker.

Check API presence and the documented availability/capability call with the actual options.
Handle unavailable, downloadable, downloading, and available states where the API defines
them. Hardware, free storage, language, model availability, browser channel, and policy can
change the result. Unsupported devices need a usable non-AI path. Do not equate a supported
Chrome version with a ready model.

Start model creation/download from the documented user interaction where required. Show
real download progress and useful errors. Support cancellation, dispose of unused sessions,
bound concurrent work, and use streaming only when it improves the interaction. A mock can
verify state transitions; a model download or actual inference requires browser evidence.

Explain processing and data destinations truthfully. Page text and model output are
untrusted input; render safely, validate outputs, and never execute model text as code or
privileged commands. Bound what page data is read. A cloud fallback changes privacy and
possibly cost: expose the choice and obtain the appropriate consent rather than silently
transmitting input when local inference fails. Never place provider API keys in a distributable
extension; use an appropriate authenticated server boundary if cloud integration is required.

Test unsupported API, unavailable model, download progress/failure, cancellation, supported
languages/options, session reuse/disposal, inference errors, and user-visible fallback.
Reconcile these flows with the extension's `CHROMEWEBSTORE.md` when applicable. Record which
states used mocks and which ran on the real browser/device/model.
