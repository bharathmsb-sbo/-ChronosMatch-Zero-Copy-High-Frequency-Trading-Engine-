# ChronosMatch – Zero-Copy High-Frequency Trading (HFT) Engine

A modular, lightweight order matching engine and market simulation system built in Python. Designed for price-time priority execution, low-latency memory mapping (`mmap`), and circular ring buffer processing.

---

## Key Features

* **Core Matching Engine (`order_matching.py` & `order_book.py`):** Real-time limit order book maintaining discrete bid/ask queues with price-time priority matching logic.
* **Ring Buffer Queue (`ring_buffer.py`):** Fixed-capacity circular memory buffer ($O(1)$) preventing dynamic memory reallocation overhead.
* **Memory-Mapped I/O (`mmap_engine.py`):** Binary data exchange module using direct memory mapping to minimize file I/O latency.
* **Order Management Modules:**
  * `order_cancel.py`: Cancels active resting orders by unique Order ID.
  * `order_modify.py`: Modifies price or quantity of unmatched resting orders.
* **Trade Event Logger (`trade_logger.py`):** Millisecond-accurate timestamped event logging for order lifecycle tracking.
* **Synthetic Market Simulator (`market_simulator.py`):** Generates randomized, realistic bid/ask order flows across configurable price spreads.
* **Monitoring & Interactive Controls:**
  * `dashboard.py`: Live terminal dashboard showing top-of-book depth and market spread.
  * `interactive_order.py`: Terminal CLI interface for manual order placement.
  * `export_trades.py`: Exports executed trade history to CSV format.
* **Benchmarking & Testing:**
  * `benchmark.py`: High-volume throughput and execution latency stress tests.
  * `test_engine.py`: Unit test coverage for core matching and execution logic.

---

## Project Structure

```text
-ChronosMatch-Zero-Copy-High-Frequency-Trading-Engine-/
├── docs/
│   └── project_analysis.md      # Architecture and performance breakdown
├── src/
│   ├── benchmark.py             # Performance and throughput testing
│   ├── dashboard.py             # Terminal market monitor
│   ├── export_trades.py         # CSV trade data exporter
│   ├── interactive_order.py     # Manual CLI order entry
│   ├── main_engine.py           # Core engine pipeline orchestrator
│   ├── market_simulator.py      # Synthetic order flow generator
│   ├── mmap_engine.py           # Zero-copy memory mapped persistence
│   ├── order_book.py            # Limit order book data structure
│   ├── order_cancel.py          # Order cancellation module
│   ├── order_matching.py        # Price-time matching logic
│   ├── order_modify.py          # Order update module
│   ├── ring_buffer.py           # Fixed-size circular buffer
│   ├── test_engine.py           # Unit testing suite
│   └── trade_logger.py          # Real-time event logger
├── .gitignore
└── README.md
