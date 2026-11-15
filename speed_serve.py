# Speed-Serve - Serve timed executions: handlers in, latency stats out
# Part of the Kapildhinwa2010-dev Toolkit.
"""ServeNet - model registry and request envelopes (service layer).

Lineage: the *-Serve toolkit repos. Models are registered with metadata and
version; requests travel as validated envelopes; responses carry latency and
payload size so the registry can be monitored without a web framework.
"""

from __future__ import annotations

import time

import numpy as np

__all__ = ["Envelope", "ModelRecord", "ServeRegistry"]


class Envelope:
    """Validated request payload."""

    def __init__(self, request_id: str, payload: np.ndarray) -> None:
        if not request_id:
            raise ValueError("request_id must be non-empty")
        payload = np.asarray(payload, dtype=np.float64)
        if payload.size == 0:
            raise ValueError("payload must be non-empty")
        self.request_id = request_id
        self.payload = payload

    def nbytes(self) -> int:
        return int(self.payload.nbytes)


class ModelRecord:
    """A registered model with version and callable."""

    def __init__(self, name: str, version: str, fn) -> None:
        if not name or not version:
            raise ValueError("name and version must be non-empty")
        if not callable(fn):
            raise TypeError("fn must be callable")
        self.name = name
        self.version = version
        self.fn = fn
        self.calls = 0

    def invoke(self, payload: np.ndarray) -> np.ndarray:
        result = self.fn(payload)
        self.calls += 1
        return np.asarray(result)


class ServeRegistry:
    """Registry with versioned lookup and served-request statistics."""

    def __init__(self) -> None:
        self._models: dict = {}
        self.stats = {"requests": 0, "total_latency_ms": 0.0, "total_bytes": 0}

    def register(self, name: str, version: str, fn) -> ModelRecord:
        record = ModelRecord(name, version, fn)
        self._models[(name, version)] = record
        return record

    def get(self, name: str, version: str = "latest") -> ModelRecord:
        if version == "latest":
            candidates = [r for (n, _) in self._models if n == name]
            if not candidates:
                raise KeyError("unknown model: {}".format(name))
            version = max(v for (n, v) in self._models if n == name)
        key = (name, version)
        if key not in self._models:
            raise KeyError("unknown model: {}@{}".format(name, version))
        return self._models[key]

    def serve(self, name: str, envelope: Envelope, version: str = "latest") -> dict:
        model = self.get(name, version)
        start = time.perf_counter()
        result = model.invoke(envelope.payload)
        latency_ms = (time.perf_counter() - start) * 1000.0
        self.stats["requests"] += 1
        self.stats["total_latency_ms"] += latency_ms
        self.stats["total_bytes"] += envelope.nbytes()
        return {
            "request_id": envelope.request_id,
            "model": model.name,
            "version": model.version,
            "shape": tuple(int(d) for d in result.shape),
            "latency_ms": latency_ms,
        }

    def summary(self) -> dict:
        requests = self.stats["requests"]
        return {
            "models": len(self._models),
            "requests": requests,
            "avg_latency_ms": (self.stats["total_latency_ms"] / requests) if requests else 0.0,
            "total_bytes": self.stats["total_bytes"],
        }

__all__.append("TimingService")


class TimingService:
    """Serve timed executions of registered handlers.

    Handlers are registered callables. Each execution is timed with
    perf_counter and its latency recorded; a per-handler report gives
    call count and min/avg/max latency. Timings are wall-clock on the
    running machine; only relative comparisons are meaningful.
    """

    def __init__(self) -> None:
        self._handlers: dict = {}
        self._latencies: dict = {}

    def register(self, name: str, fn) -> None:
        if not name:
            raise ValueError("name must be non-empty")
        if not callable(fn):
            raise TypeError("handler must be callable")
        self._handlers[name] = fn
        self._latencies.setdefault(name, [])

    def execute(self, name: str, *args, **kwargs):
        """Run a handler, record its latency, return its result."""
        if name not in self._handlers:
            raise KeyError("unknown handler: {}".format(name))
        start = time.perf_counter()
        result = self._handlers[name](*args, **kwargs)
        self._latencies[name].append((time.perf_counter() - start) * 1000.0)
        return result

    def serve(self, request_id: str, name: str, *args, **kwargs) -> dict:
        """Serve one timed execution; returns result and latency."""
        if not request_id:
            raise ValueError("request_id must be non-empty")
        start = time.perf_counter()
        result = self.execute(name, *args, **kwargs)
        total_ms = (time.perf_counter() - start) * 1000.0
        return {"request_id": request_id, "handler": name,
                "result": result, "latency_ms": total_ms}

    def report(self, name: str) -> dict:
        """Per-handler call count and min/avg/max latency in ms."""
        if name not in self._handlers:
            raise KeyError("unknown handler: {}".format(name))
        samples = self._latencies[name]
        if not samples:
            return {"calls": 0, "min_ms": 0.0, "avg_ms": 0.0, "max_ms": 0.0}
        return {
            "calls": len(samples),
            "min_ms": min(samples),
            "avg_ms": sum(samples) / len(samples),
            "max_ms": max(samples),
        }

