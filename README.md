# ChronosMatch: Zero-Copy High-Frequency Trading Engine

A simple Python-based Order Matching Engine, Market Simulator, and Low-Latency Zero-Copy Architecture.

## Project Structure
* `src/order_matching.py`: Basic single-order comparison and trade execution.
* `src/order_book.py`: Order book matching logic using price priority.
* `src/market_simulator.py`: Automatically generates random Buy and Sell orders.
* `src/main_engine.py`: Runs a live simulation connecting the simulator to the matching engine.
* `src/ring_buffer.py`: Circular ring buffer queue for fast order ingestion without memory reallocation.
* `src/mmap_engine.py`: Memory-mapped file demo for zero-copy binary order reading and writing.
* `src/test_engine.py`: Automated test cases for verifying match logic.
* `src/benchmark.py`: Measures execution speed and throughput over batches of orders.
* `src/export_trades.py`: Exports executed trade history into a CSV file.
* `src/interactive_order.py`: Allows manual terminal order entry to test matching.