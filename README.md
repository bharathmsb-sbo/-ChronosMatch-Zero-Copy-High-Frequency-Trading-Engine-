# ChronosMatch: Zero-Copy High-Frequency Trading Engine

A simple Python-based Order Matching Engine and Market Simulator.

## Project Structure
* `src/order_matching.py`: Basic single-order comparison and trade execution.
* `src/order_book.py`: Order book matching logic using price priority.
* `src/market_simulator.py`: Automatically generates random Buy and Sell orders.
* `src/main_engine.py`: Runs a live simulation connecting the simulator to the matching engine.
* `src/test_engine.py`: Automated test cases for verifying match logic.
* `src/benchmark.py`: Measures execution speed and throughput over batches of orders.

## How to Run
Run the main engine:
```bash
python src/main_engine.py