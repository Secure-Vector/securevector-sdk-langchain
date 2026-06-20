"""SecureVector SDK for LangChain.

Enforcement (recommended) — the documented ``wrap_tool_call`` middleware::

    from securevector_sdk_langchain import secure_middleware
    from langchain.agents import create_agent

    agent = create_agent(
        model, tools,
        middleware=[secure_middleware(mode="enforce")],
    )

Observe-only logging for legacy AgentExecutor / raw LCEL chains::

    from securevector_sdk_langchain import SecureVectorCallbackHandler
    chain.invoke(payload, config={"callbacks": [SecureVectorCallbackHandler()]})

Either way, every tool call runs the local SecureVector app's three controls —
tool-call permissions, secret/data-leak detection, threat detection — and each
decision is written to the app's tamper-evident audit chain with
``runtime_kind="langchain"``. Requires the SecureVector app running locally
(installed automatically as the ``securevector-ai-monitor`` dependency).
"""

import logging
from typing import Optional

from ._version import __version__
from .config import Config
from .errors import AppUnreachable, SecureVectorError, ToolBlocked
from .handler import SecureVectorCallbackHandler
from .middleware import secure_middleware

log = logging.getLogger("securevector_sdk_langchain")

__all__ = [
    "__version__",
    "secure_middleware",
    "install",
    "SecureVectorCallbackHandler",
    "Config",
    "SecureVectorError",
    "ToolBlocked",
    "AppUnreachable",
]


def install(mode: str = "observe", base_url: Optional[str] = None, **kwargs):
    """Convenience alias for :func:`secure_middleware` — returns the middleware
    to pass to ``create_agent(..., middleware=[install(mode="enforce")])``."""
    return secure_middleware(mode=mode, base_url=base_url, **kwargs)
