
# CHRONOSMATCH – ZERO-COPY HIGH-FREQUENCY TRADING ENGINE

ChronosMatch is a Python-based order matching engine designed to simulate the basic working of a high-frequency trading system.

## Main Objective

The main objectives of the project are:

1. Add BUY and SELL orders
2. Store and manage orders
3. Match BUY and SELL orders
4. Generate executed trade results
5. Measure basic performance through benchmarking

## Features

* Order management
* BUY and SELL order handling
* Order validation
* Price-priority order sorting
* Basic order book
* Order matching
* Trade execution
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
│   ├── matching_engine.py
│   └── order_book.py
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
├── .gitignore
└── README.md
```

## Project Flow

```text
        BUY Order ──┐
                    │
                    ▼
                OrderBook
                    │
        SELL Order ─┘
                    │
                    ▼
             MatchingEngine
                    │
                    ▼
              Price Match?
                 /     \
               Yes      No
                │        │
                ▼        ▼
         Executed Trade  Remaining Order
                │
                ▼
              Logger
```

## How It Works

ChronosMatch works in the following steps:

1. A BUY or SELL order is created.
2. The order is validated before being added.
3. BUY and SELL orders are stored in the order book.
4. BUY orders are sorted from highest to lowest price.
5. SELL orders are sorted from lowest to highest price.
6. The Matching Engine compares BUY and SELL orders.
7. If the BUY price is greater than or equal to the SELL price, the orders are matched.
8. The trade quantity is calculated using the smaller available quantity.
9. The executed trade is generated and logged.
10. Any remaining quantity stays in the order book.

## Price Priority

Price priority determines which order gets matched first.

* **BUY orders:** highest price gets priority.
* **SELL orders:** lowest price gets priority.

Example:

```text
BUY:
101 → Priority 1
100 → Priority 2

SELL:
100 → Priority 1
102 → Priority 2
```

## Example

### BUY Order

```text
Price: 100
Quantity: 10
```

### SELL Order

```text
Price: 100
Quantity: 5
```

Since the BUY price (100) is equal to the SELL price (100), the orders can be matched.

### Executed Trade

```text
Price: 100
Quantity: 5
```

The remaining BUY quantity is:

```text
10 - 5 = 5
```

## Validation

The Matching Engine performs basic order validation, including:

* `order_id` must be present.
* `side` must be either `BUY` or `SELL`.
* Price must be greater than zero.
* Quantity must be greater than zero.

Invalid orders are rejected instead of being processed.

## Unit Testing

Unit testing was performed using **pytest** to verify important parts of the Matching Engine.

Tests include:

* BUY order addition
* SELL order addition
* Price-priority sorting
* Order validation
* Matching behavior

The test suite was executed successfully during development.

## Performance Benchmark

Performance testing was added using Python's `time.perf_counter()`.

The benchmark measures the execution time and throughput of the order matching operation.

### Order Matching Benchmark

Test configuration:

* BUY orders: 1,000
* SELL orders: 1,000
* Total orders: 2,000

### Results

| Metric                |                  Result |
| --------------------- | ----------------------: |
| Average matching time |        0.085399 seconds |
| Minimum matching time |        0.079075 seconds |
| Maximum matching time |        0.103408 seconds |
| Throughput            | 23,433.24 orders/second |

These results represent the performance observed in the current local benchmark environment.

## Benchmarking Tool

Performance benchmarking is implemented in:

```text
benchmark.py
```

The benchmark measures:

* Order addition time
* Order matching time
* Average execution time
* Minimum execution time
* Maximum execution time
* Orders processed per second

## Logging

The project includes a logging system to record important events such as:

```text
Trade executed
Order matching completed
```

Logging helps in monitoring and debugging the matching process.

## Technologies Used

* Python
* Git
* GitHub
* Pytest
* VS Code

## Current Project Status

The project currently includes:

* Order management
* BUY/SELL handling
* Order validation
* Price-priority sorting
* Order matching
* Trade execution
* Logging
* Unit testing
* Performance benchmarking
* GitHub version control


