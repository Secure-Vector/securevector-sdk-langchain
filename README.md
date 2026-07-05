# SecureVector SDK for LangChain

[![PyPI](https://img.shields.io/pypi/v/securevector-sdk-langchain)](https://pypi.org/project/securevector-sdk-langchain/)
[![Downloads](https://img.shields.io/pypi/dm/securevector-sdk-langchain)](https://pypistats.org/packages/securevector-sdk-langchain)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/securevector-sdk-langchain/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

> Bring the SecureVector local threat monitor's three controls — **tool-call
> permissions**, **secret / data-leak detection**, and **threat detection** —
> to every LangChain tool call, with tamper-evident audit logging. One import.

```bash
pip install securevector-sdk-langchain
```

> 📦 **One install — batteries included.** `pip install securevector-sdk-langchain`
> **also installs the local SecureVector app** (`securevector-ai-monitor`): the
> adapter **and** the detection engine + tamper-evident audit chain arrive in a
> single `pip install`. The SDK is a thin interception layer — **the app must be
> running locally** (`securevector-app --web`) for it to do anything.

> 🌐 **Pointing at your own cloud? Use the lightweight install.** If you've deployed
> SecureVector to your own cloud, you don't need the bundled
> local app. Install **only the adapter** on the machine where your agents run, and
> point it at your deployment:
>
> ```bash
> # lightweight — adapter only, no local app (your env already has langchain)
> pip install securevector-sdk-langchain --no-deps
>
> # point at your SecureVector endpoint — all you need for a private (in-VPC) endpoint
> export SECUREVECTOR_SDK_APP_URL=https://<your-securevector-endpoint>
>
> # OPTIONAL: only if your endpoint is publicly exposed and gated with an inbound token.
> # A private endpoint in your own VPC needs no key. To gate a public one, use a free
> # SecureVector cloud account API key or an SVET token — it gates access only; no agent
> # data is sent to SecureVector.
> export SECUREVECTOR_API_KEY=<SecureVector account key or SVET token>
> ```
> The adapter then forwards every tool call to your remote deployment instead of a
> local app. The default `pip install securevector-sdk-langchain` (no `--no-deps`)
> still bundles the app for local use.

## Quick start

**Enforcement (recommended)** — the documented `wrap_tool_call` middleware,
which can cleanly block a tool before it runs:

```python
from securevector_sdk_langchain import secure_middleware
from langchain.agents import create_agent

agent = create_agent(
    model, tools,
    middleware=[secure_middleware(mode="enforce")],
)
```

A denied tool is short-circuited with a `ToolMessage` (the model sees a clean
"blocked by policy" result) — no exceptions, no crashed runs.

**Observe-only logging** for legacy `AgentExecutor` / raw LCEL chains, where the
middleware surface isn't available:

```python
from securevector_sdk_langchain import SecureVectorCallbackHandler

chain.invoke(payload, config={"callbacks": [SecureVectorCallbackHandler()]})
```

> Why two paths? LangChain **callbacks are an observability surface** — they
> cannot reliably block a tool call. The **`wrap_tool_call` middleware is the
> documented interception/short-circuit point**, so enforcement lives there.

**LLM cost tracking** — add `cost_tracking_middleware()` and every model call's
token usage (input / output / cached) posts to the app's **Cost Tracking**,
where the pricing table turns it into real dollars (your agent runs on your own
API keys) and per-agent budgets apply:

```python
from securevector_sdk_langchain import secure_middleware, cost_tracking_middleware

agent = create_agent(
    model, tools,
    middleware=[secure_middleware(mode="enforce"), cost_tracking_middleware()],
)
```

Records are attributed to `agent_id="langchain-agent"` by default — name your
agent with `cost_tracking_middleware(agent_id="checkout-bot")` or
`SECUREVECTOR_SDK_AGENT_ID`. The callback handler captures the same usage via
`on_llm_end` for legacy chains. Cost capture is best-effort: an unreachable app
never breaks the agent.

## What happens on every tool call

Before a tool runs, the SDK:

1. **(a) Permissions** — resolves an allow/block verdict for the tool, using the
   app's own precedence: cloud-pushed **synced** policy → local **override** →
   **essential** registry → default-allow.
2. **(b)+(c) Secret & threat scan** — sends the serialized tool input through the
   app's `/analyze` pipeline.

After the tool returns, the result is scanned the same way to catch secrets /
exfiltration in tool output. Every decision is written to the app's audit chain
tagged `runtime_kind="langchain"`.

## observe vs enforce

| | local app reachable | local app unreachable |
|---|---|---|
| **observe** (default) | log + advisory verdict; tool always runs | tool runs (fail-open) |
| **enforce** (opt-in) | tool runs only if the verdict ≠ block | **tool denied** (fail-closed) |

```python
agent = create_agent(model, tools, middleware=[secure_middleware(mode="enforce")])
```

Enforce mode prints a one-time disclosure to stderr. (Enforcement requires the
middleware path; the observe-only callback handler always runs in observe mode.)

## Configuration

All optional, via env or `install(...)` kwargs:

| Env var | Default | Meaning |
|---|---|---|
| `SECUREVECTOR_SDK_APP_URL` | `http://127.0.0.1:8741` | local app base URL |
| `SECUREVECTOR_SDK_MODE` | `observe` | `observe` or `enforce` |
| `SECUREVECTOR_SDK_TIMEOUT_MS` | `3000` | per-call verdict timeout |
| `SECUREVECTOR_SDK_RISK_THRESHOLD` | `70` | risk score that blocks in enforce mode |
| `SECUREVECTOR_SDK_AGENT_ID` | `langchain-agent` | agent id shown in Cost Tracking |
| `SECUREVECTOR_SDK_DISABLED` | _(unset)_ | set truthy to no-op |

## Compliance

The tool-call-level, attributed, tamper-evident audit trail this produces is
exactly the **action-layer logging** auditors ask for under **EU AI Act
Art. 12 / 15**. This SDK produces the local evidence; the cloud governance
surface turns it into an auditor-ready pack.

## Trademarks

**SecureVector** is the product name of this SDK. **LangChain** and
**LangGraph** are trademarks of LangChain, Inc. This is an independent,
community SDK that *integrates with* LangChain via its public callback API. It
is **not affiliated with, sponsored by, or endorsed by LangChain, Inc.** The
name uses "langchain" only descriptively, to identify the framework this
package works with (nominative fair use).

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
