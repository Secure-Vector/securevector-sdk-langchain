# Changelog

All notable changes to `securevector-sdk-langchain` are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0]

### Added
- Initial LangChain adapter (Phase 1 of the SecureVector SDK roadmap, story #174).
- `secure_middleware(mode=...)` — the primary interception path, built on
  LangChain v1's documented `wrap_tool_call` middleware. Runs the three controls
  on every tool call and, in enforce mode, short-circuits a denied tool with a
  `ToolMessage` (no exceptions):
  - **(a)** tool-call permission resolution (synced → override → essential → default-allow),
  - **(b)** secret / data-leak detection on tool input and output,
  - **(c)** threat detection on tool input and output.
- `SecureVectorCallbackHandler` — observe-only audit logging for legacy
  `AgentExecutor` / raw LCEL chains where middleware isn't available (callbacks
  cannot reliably block, so this never enforces).
- `install(mode=...)` is an alias for `secure_middleware`;
  `import securevector_sdk_langchain.auto` registers observe-mode logging.
- `observe` (fail-open, default) and `enforce` (fail-closed) modes.
- Requires `langchain>=1.0` for the `wrap_tool_call` middleware API.
- Audit forwarding to the local app's tamper-evident chain with
  `runtime_kind="langchain"` attribution.
- CI + Test PyPI (develop) / PyPI (main release) publishing via OIDC trusted
  publishing, mirroring `securevector-guardian-model`.
