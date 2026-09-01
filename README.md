# CHRONOSMATCH – ZERO-COPY HIGH-FREQUENCY TRADING ENGINE

ChronosMatch is a Python and Cython-based order matching engine designed to simulate the basic working of a high-frequency trading system.

## Main Objective

The main objectives of the project are:

1. Add BUY and SELL orders
2. Store and manage orders
3. Match BUY and SELL orders
4. Generate executed trade results
5. Implement Price-Time Priority
6. Use memory-mapped RingBuffer for efficient order data handling
7. Improve performance using Cython
8. Measure performance through benchmarking

## Features

* Order management
* BUY and SELL order handling
* Order validation
* Price-Time Priority
* Basic order book
* Order matching
* Trade execution
* Partial order matching
* Order cancellation
* Order modification
* Memory-mapped RingBuffer
* Cython-based Matching Engine
* Cython-based Order Book
* Cython-based RingBuffer
* Logging system
* Unit testing
* Performance benchmarking
* Git and GitHub version control

## Project Structure

```text
ChronosMatch/
│
├── engine/
│   ├── __init__.py
│   ├── matching_engine.pyx
│   ├── order_book.pyx
│   └── ring_buffer.pyx
│
├── utils/
│   ├── __init__.py
│   └── logger.py
│
├── tests/
│   └── test_matching_engine.py
│
├── main.py
├── benchmark.py
├── benchmark_mmap.py
├── setup.py
├── .gitignore
└── README.md
```

## Project Flow

```text
              BUY / SELL Orders
                      │
                      ▼
            Memory-Mapped RingBuffer
                      │
                      ▼
                 OrderBook
                      │
                      ▼
              MatchingEngine
                      │
                      ▼
              Price-Time Priority
                      │
              ┌───────┴───────┐
              │               │
             Match          No Match
              │               │
              ▼               ▼
       Executed Trade    Remaining Order
              │
              ▼
            Logger
```

## How It Works

ChronosMatch works in the following steps:

1. A BUY or SELL order is created.
2. The order is written into the memory-mapped RingBuffer.
3. The order is read from the RingBuffer.
4. The order is validated before being added to the Matching Engine.
5. BUY and SELL orders are stored.
6. BUY orders receive priority based on highest price.
7. SELL orders receive priority based on lowest price.
8. Orders with the same price are prioritized using sequence/time priority.
9. The Matching Engine compares BUY and SELL orders.
10. If the BUY price is greater than or equal to the SELL price, the orders are matched.
11. The trade quantity is calculated using the smaller available quantity.
12. The executed trade is generated and logged.
13. Any remaining quantity stays in the order book.

## Price-Time Priority

Price-Time Priority determines which order gets matched first.

### BUY Orders

Higher price gets priority.

If two BUY orders have the same price, the order that arrived first gets priority.

### SELL Orders

Lower price gets priority.

If two SELL orders have the same price, the order that arrived first gets priority.

Example:

```text
BUY:

Price 101 → Priority 1
Price 100 → Priority 2

SELL:

Price 100 → Priority 1
Price 102 → Priority 2
```

## Order Cancellation

Orders can be cancelled using their `order_id`.

Example:

```text
Order ID: 2
Side: BUY
Price: 101
Quantity: 5
```

After cancellation, the order is removed from the active order list.

## Order Modification

Existing orders can be modified by changing their price or quantity.

A modified order receives a new sequence number, meaning it gets new time priority.

## Partial Matching

The Matching Engine supports partial order matching.

Example:

```text
BUY
Price: 100
Quantity: 10

SELL
Price: 100
Quantity: 8
```

Executed trade:

```text
Price: 100
Quantity: 8
```

Remaining BUY quantity:

```text
10 - 8 = 2
```

The remaining quantity stays active in the order book.

## Validation

The Matching Engine performs basic order validation:

* `order_id` must be present.
* `side` must be either `BUY` or `SELL`.
* Price must be greater than zero.
* Quantity must be greater than zero.

Invalid orders are rejected instead of being processed.

## Memory Mapping

ChronosMatch uses Python's `mmap` module to implement a memory-mapped RingBuffer for efficient order data handling.

Order data is stored in a fixed-size binary format using Python's `struct` module.

The memory-mapped buffer is integrated into the order flow:

```text
BUY/SELL Order
      ↓
Memory-Mapped RingBuffer
      ↓
Read Order
      ↓
OrderBook
      ↓
MatchingEngine
      ↓
Executed Trade
```

The RingBuffer supports:

* Writing order data into mapped memory
* Reading order data from mapped memory
* Fixed-size binary records
* Circular buffer indexing

## Cython Optimization

The core components have been implemented using Cython:

```text
matching_engine.pyx
order_book.pyx
ring_buffer.pyx
```

Cython `cdef` declarations are used for selected variables and classes to reduce Python-level overhead.

The Cython modules are compiled using `setup.py`.

## Unit Testing

Unit testing is performed using `pytest`.

The current test suite covers:

* BUY order addition
* SELL order addition
* BUY price priority
* BUY/SELL matching
* Invalid order side
* Invalid price
* Invalid quantity
* Order cancellation
* Price-Time Priority
* Order modification

Current test result:

```text
10 passed
```

## Performance Benchmark

Performance testing is performed using Python's `time.perf_counter()`.

### Order Matching Benchmark

Test configuration:

* BUY orders: 1,000
* SELL orders: 1,000
* Total orders: 2,000

Results:

| Metric                |                  Result |
| --------------------- | ----------------------: |
| Average matching time |        0.085399 seconds |
| Minimum matching time |        0.079075 seconds |
| Maximum matching time |        0.103408 seconds |
| Throughput            | 23,433.24 orders/second |

These results represent the performance observed in the local benchmark environment.

### Memory Mapping Benchmark

The memory-mapped RingBuffer was benchmarked with 1,000 and 10,000 orders.

#### 1,000 Orders

| Metric            |           Result |
| ----------------- | ---------------: |
| Average time      | 0.000233 seconds |
| Minimum time      | 0.000230 seconds |
| Maximum time      | 0.000241 seconds |
| Orders per second |     4,291,108.82 |

#### 10,000 Orders

| Metric            |           Result |
| ----------------- | ---------------: |
| Average time      | 0.002333 seconds |
| Minimum time      | 0.002314 seconds |
| Maximum time      | 0.002357 seconds |
| Orders per second |     4,286,106.16 |

These results represent the performance observed in the current local benchmark environment.

## Benchmarking Tools

Performance benchmarking is implemented in:

```text
benchmark.py
benchmark_mmap.py
```

The benchmarks measure:

* Order addition time
* Order matching time
* Average execution time
* Minimum execution time
* Maximum execution time
* Orders processed per second

## Logging

The project includes a logging system to record important events such as:

```text
Order added
Order cancelled
Order modified
Trade executed
Order matching completed
```

Logging helps with monitoring and debugging the matching process.

## Technologies Used

* Python
* Cython
* mmap
* struct
* Pytest
* Git
* GitHub
* VS Code

## Current Project Status

The project currently includes:

* Order management
* BUY/SELL handling
* Order validation
* Price-Time Priority
* Order matching
* Partial matching
* Trade execution
* Order cancellation
* Order modification
* Memory-mapped RingBuffer
* Cython Matching Engine
* Cython Order Book
* Cython RingBuffer
* Logging
* Unit testing
* Performance benchmarking
* GitHub version control

### Current Verification

```text
Cython MatchingEngine     → PASS
Cython OrderBook          → PASS
Cython RingBuffer         → PASS
End-to-End main.py        → PASS
Pytest                    → 10 passed
Memory Mapping Benchmark  → PASS
```
