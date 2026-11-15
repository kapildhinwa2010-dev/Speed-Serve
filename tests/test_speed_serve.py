import numpy as np
import pytest

from speed_serve import Envelope, ServeRegistry


def _identity(x):
    return x


def _double(x):
    return x * 2.0


def test_envelope_rejects_empty_id():
    with pytest.raises(ValueError):
        Envelope("", np.ones(3))


def test_envelope_rejects_empty_payload():
    with pytest.raises(ValueError):
        Envelope("r1", np.array([]))


def test_envelope_nbytes():
    env = Envelope("r1", np.ones((4, 4)))
    assert env.nbytes() == 128


def test_model_record_requires_callable():
    with pytest.raises(TypeError):
        ServeRegistry().register("m", "1.0", "not-callable")


def test_register_and_get_latest():
    registry = ServeRegistry()
    registry.register("m", "1.0", _identity)
    registry.register("m", "2.0", _double)
    assert registry.get("m").version == "2.0"


def test_get_specific_version():
    registry = ServeRegistry()
    registry.register("m", "1.0", _identity)
    registry.register("m", "2.0", _double)
    assert registry.get("m", "1.0").version == "1.0"


def test_get_unknown_raises():
    registry = ServeRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")


def test_invoke_counts_calls():
    registry = ServeRegistry()
    record = registry.register("m", "1.0", _double)
    out = record.invoke(np.array([1.0, 2.0]))
    assert np.array_equal(out, np.array([2.0, 4.0]))
    assert record.calls == 1


def test_serve_returns_metadata():
    registry = ServeRegistry()
    registry.register("m", "1.0", _double)
    response = registry.serve("m", Envelope("r1", np.ones((2, 2))))
    assert response["request_id"] == "r1"
    assert response["model"] == "m"
    assert response["shape"] == (2, 2)
    assert response["latency_ms"] >= 0.0


def test_summary_tracks_requests():
    registry = ServeRegistry()
    registry.register("m", "1.0", _identity)
    registry.serve("m", Envelope("r1", np.ones(4)))
    registry.serve("m", Envelope("r2", np.ones(4)))
    summary = registry.summary()
    assert summary["requests"] == 2
    assert summary["models"] == 1
    assert summary["total_bytes"] == 2 * 32
