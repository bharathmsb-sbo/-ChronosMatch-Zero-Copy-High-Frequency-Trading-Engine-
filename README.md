# ChronosMatch

A learning/demo low-latency matching-engine project for FinTech systems programming.

> This is a research/education simulator, not a production HFT system. Real HFT requires kernel/network tuning, exchange protocols, hardware timestamping, CPU isolation, NUMA awareness, NIC tuning, and extensive validation.

## Architecture

```text
asyncio Market Simulator
        |
        v
Python mmap + struct Ring Buffer  <---- shared memory file ---->  Cython Matching Engine
        |                                                        |
        |                                                        v
        +---------------------> curses Dashboard <-------- Metrics/State
                                                                     |
                                                                     v
                                                              SQLite Ledger
```

## Features

- Fixed-size mmap ring buffer using raw bytes and `struct`.
- Single-producer/single-consumer process design with sequence counters.
- Cython price-time-priority limit order book.
- asyncio order firehose simulator.
- curses terminal dashboard.
- `perf_counter_ns()` ingress/match/egress timestamps.
- SQLite trade ledger flusher.
- Whale-order detection when one order consumes multiple price levels.
- Stress test for 1,000,000 ring-buffer messages.

## Requirements

- Python 3.11+ recommended.
- Linux/macOS recommended for the curses dashboard. Windows can run the engine/simulator, but native `curses` is not included with standard CPython.
- GCC/Clang or MSVC-compatible C compiler for Cython extension.

Install:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install -U pip setuptools wheel cython
python -m pip install -e .
```

## Run

Terminal 1 — start the matching engine:

```bash
python scripts/run_engine.py
```

Terminal 2 — blast simulated orders:

```bash
python scripts/run_simulator.py --rate 100000 --duration 20
```

Terminal 3 — dashboard:

```bash
python scripts/run_dashboard.py
```

Terminal 4 — ledger flusher:

```bash
python scripts/run_ledger.py
```

The shared-memory file is `./chronosmatch.mmap`; the SQLite database is `./chronosmatch.db`.

## Important implementation detail

The ring buffer has fixed-width binary records. No JSON or Pickle is used for the order path. The Cython matching loop operates on C-level fields after the record is read, while the Python process performs the mmap I/O. The demo deliberately uses a single producer and single consumer so ownership of head/tail positions stays simple and deterministic.

## Tests

```bash
python -m pytest -q
```

Run the million-order benchmark:

```bash
python scripts/benchmark_ipc.py --orders 1000000
```

## Suggested week-by-week progression

### Week 1
- Study the binary record layout.
- Run ring-buffer tests.
- Increase/decrease ring capacity and record size.
- Benchmark mmap versus JSON/Pickle in the included benchmark.

### Week 2
- Study `cython_engine/orderbook.pyx`.
- Verify price-time matching.
- Run the dashboard while the simulator is active.

### Week 3
- Inspect timestamp metrics.
- Profile the engine.
- Keep Python objects out of the matching loop.
- Experiment with compiler optimization flags only after measuring.

### Week 4
- Run the ledger flusher.
- Test crash/restart behavior.
- Add persistence/checkpointing.
- Add exchange-specific order semantics and richer metrics.
