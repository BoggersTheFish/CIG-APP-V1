"""
Tool registry for agentic workflows: register and invoke named tools with logging.
Use from research_agent or autonomous loops to call external tools and record state changes.
"""
from __future__ import annotations

import time
from typing import Any, Callable


class ToolRegistry:
    """Register callables by name and invoke with logging."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}
        self.log: list[dict[str, Any]] = []

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._handlers[name] = fn

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Run tool and append to log. Returns result or raises."""
        start = time.time()
        entry: dict[str, Any] = {
            "tool": name,
            "args": kwargs,
            "timestamp": start,
        }
        try:
            fn = self._handlers.get(name)
            if fn is None:
                entry["error"] = f"Unknown tool: {name}"
                self.log.append(entry)
                raise KeyError(entry["error"])
            result = fn(**kwargs)
            entry["result"] = result
            entry["duration_s"] = time.time() - start
            self.log.append(entry)
            return result
        except Exception as e:
            entry["error"] = str(e)
            entry["duration_s"] = time.time() - start
            self.log.append(entry)
            raise

    def clear_log(self) -> None:
        self.log.clear()


# Default registry for process-wide use
_default_registry: ToolRegistry | None = None


def get_default_registry() -> ToolRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry
