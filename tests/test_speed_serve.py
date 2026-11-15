"""Tests for Speed-Serve TimingService: timed handler execution."""

import pytest

from speed_serve import TimingService, ServeRegistry


def test_register_and_execute_returns_result():
    service = TimingService()
    service.register("double", lambda x: x * 2)
    assert service.execute("double", 21) == 42


def test_execute_unknown_handler_raises():
    service = TimingService()
    with pytest.raises(KeyError):
        service.execute("ghost")


def test_report_tracks_latency_stats():
    service = TimingService()
    service.register("noop", lambda: None)
    service.execute("noop")
    service.execute("noop")
    report = service.report("noop")
    assert report["calls"] == 2
    assert 0.0 <= report["min_ms"] <= report["avg_ms"] <= report["max_ms"]


def test_report_empty_handler():
    service = TimingService()
    service.register("idle", lambda: None)
    assert service.report("idle")["calls"] == 0


def test_serve_wraps_result_and_latency():
    service = TimingService()
    service.register("square", lambda x: x * x)
    out = service.serve("r1", "square", 4)
    assert out["result"] == 16
    assert out["handler"] == "square"
    assert out["latency_ms"] >= 0.0


def test_register_validates():
    service = TimingService()
    with pytest.raises(ValueError):
        service.register("", lambda: None)
    with pytest.raises(TypeError):
        service.register("bad", 42)


def test_base_registry_still_works():
    assert ServeRegistry().summary()["requests"] == 0
