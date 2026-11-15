# Speed-Serve

[![CI](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/codeql.yml)

Serve timed executions of registered handlers: result plus latency, with min/avg/max reports.

## What it does

TimingService registers callables and executes them under perf_counter
timing. Every execution returns its result and latency; a per-handler
report gives call count and min/avg/max latency in milliseconds.

    from speed_serve import TimingService

    service = TimingService()
    service.register("square", lambda x: x * x)
    out = service.serve("req-1", "square", 4)
    print(out["result"], out["latency_ms"])
    print(service.report("square"))

## API

- TimingService.register / execute / serve / report
- ServeRegistry - the generic base registry (unchanged from DNA-Serve)

## Honest results and limitations

- Timings are wall-clock on the machine running the code and vary with
  CPU load; only relative comparisons within one process are meaningful.
- Latency includes the timing overhead itself, which dominates for very
  fast handlers.
- No concurrency: handlers run inline on the calling thread.

## Status

Part of the kapildhinwa2010-dev toolkit experiments. CI and CodeQL run on
every push to main. License: MIT.
