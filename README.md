# ChronosMatch – Zero-Copy High-Frequency Trading (HFT) Engine

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-Low--Latency%20Modular-orange.svg)

A lightweight, low-latency limit order matching engine and market simulation environment implemented in Python. ChronosMatch is engineered to demonstrate high-throughput core financial mechanics, utilizing fixed-capacity ring buffers, zero-copy memory-mapped file persistence (`mmap`), and deterministic price-time priority matching algorithms.

---

## Architecture Overview

The system operates across four primary layers:
1. **Ingestion & Buffering:** Ingests synthetic or manual order streams into an $O(1)$ circular queue (`ring_buffer.py`) to eliminate heap allocation overhead.
2. **Matching Core:** Organizes bids and asks in price-time priority queues, processing full fills, partial fills, cancellations, and order modifications in sub-millisecond cycles (`order_book.py`, `order_matching.py`).
3. **Persistence & Shared State:** Utilizes binary memory mapping (`mmap_engine.py`) for low-overhead inter-process data exchange and writes completed fills to disk (`export_trades.py`).
4. **Analytics & Monitoring:** Provides live terminal-based order book tracking (`dashboard.py`), structured millisecond event logging (`trade_logger.py`), and trade metrics computation (`market_analytics.py`).

---

## Key Features

* **Price-Time Priority Matching Engine:** Real-time limit order matching for resting bids and asks.
* **Deterministic Ring Buffer (`ring_buffer.py`):** Pre-allocated, fixed-size circular memory buffer enabling $O(1)$ enqueue and dequeue operations without garbage collection spikes.
* **Memory-Mapped Persistence (`mmap_engine.py`):** Zero-copy shared memory interface bypassing OS file I/O bottlenecks.
* **Order Management System (OMS):**
  * `order_cancel.py`: Immediate cancellation of resting orders by unique `order_id`.
  * `order_modify.py`: Dynamic in-flight updates to order price and size while respecting queue priority rules.
* **Execution Analytics & Logging:**
  * `market_analytics.py`: Real-time calculation of Total Volume, Trade Counts, and Volume-Weighted Average Price (VWAP).
  * `trade_logger.py`: High-precision timestamped event logging across order lifecycles.
* **Simulation & Dashboards:**
  * `market_simulator.py`: Configurable stochastic order generation engine simulating market depth and realistic spreads.
  * `dashboard.py`: Real-time terminal UI displaying order book depth and spread metrics.
  * `interactive_order.py`: Command-line interface for manual trader order injection.

---

## Project Structure

```text
-ChronosMatch-Zero-Copy-High-Frequency-Trading-Engine-/
├── docs/
│   └── project_analysis.md      # Performance benchmarks and architectural analysis
├── src/
│   ├── benchmark.py             # Latency profiling and throughput stress-testing
│   ├── dashboard.py             # Terminal order book monitor
│   ├── export_trades.py         # CSV trade persistence utility
│   ├── interactive_order.py     # Interactive CLI order entry
│   ├── main_engine.py           # Core engine pipeline orchestrator
│   ├── market_analytics.py      # Volume and VWAP metrics calculator
│   ├── market_simulator.py      # Synthetic order flow generator
│   ├── mmap_engine.py           # Memory-mapped binary IPC interface
│   ├── order_book.py            # Limit order book data structure
│   ├── order_cancel.py          # Resting order cancellation handler
│   ├── order_matching.py        # Core matching and fill algorithm
│   ├── order_modify.py          # Dynamic order parameter modifier
│   ├── ring_buffer.py           # High-speed circular queue
│   ├── test_engine.py           # Automated unit test suite
│   └── trade_logger.py          # Timestamped event logger
├── .gitignore                   # Ignored files and cache rules
└── README.md                    # System documentation