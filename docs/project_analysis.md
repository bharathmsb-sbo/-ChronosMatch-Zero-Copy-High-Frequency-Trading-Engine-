# ChronosMatch – Zero-Copy High-Frequency Trading Engine

## 1. Project Overview

ChronosMatch is a Zero-Copy High-Frequency Trading Engine.

Domain: FinTech & Low-Latency Systems

### Main Goal

- Process a large number of Buy and Sell orders.
- Match orders with very low latency.
- Reduce unnecessary data serialization and copying.
- Use Cython and memory mapping for performance.
- Monitor trading performance in real time.

---

## 2. What is HFT?

HFT means High-Frequency Trading.

It is a system that processes a large number of trading orders at very high speed.

For example, a Buy order for 50 shares at ₹100 and a Sell order for 30 shares at ₹100 can be matched when the prices are compatible.

In this case, 30 shares can be matched and the remaining Buy quantity is 20 shares.

Speed and low latency are very important in HFT.

---

## 3. Problems

### Garbage Collection

Python uses Garbage Collection to remove unused objects.

In a low-latency system, unpredictable pauses can affect performance.

ChronosMatch reduces Python-object interaction in the performance-critical matching process.

### Serialization

Using JSON or Pickle between processes requires serialization and data transfer overhead.

This can add extra processing and copying.

ChronosMatch uses memory-based communication to reduce unnecessary serialization and copying.

---

## 4. Main Architecture

ChronosMatch is built using four major stages:

### Order Generation

The Market Simulator creates mock Buy and Sell orders using Python asyncio.

### Memory-Based Data Transfer

The generated order information is converted into a suitable byte representation using struct and stored in an mmap-based Ring Buffer.

### Order Matching

The Cython Matching Engine reads the order data, maintains the Order Book, and applies the matching logic.

### Performance Monitoring

The system measures execution latency and displays the trading performance through a terminal-based dashboard.

---

## 5. Main Modules

### 1. Market Simulator

The Market Simulator generates mock Buy and Sell orders.

It uses Python asyncio to simulate high-volume market traffic.

The project specifies a target of 100,000 mock orders per second.

### 2. Zero-Copy IPC Bus

The IPC layer uses:

- mmap
- struct
- Ring Buffer

Its purpose is to share order data between processes and reduce unnecessary serialization and copying.

### 3. Cython Matching Engine

The Cython Matching Engine is the core of the system.

Its responsibilities are:

- Read orders from the Ring Buffer.
- Maintain the Order Book.
- Compare Buy and Sell orders.
- Apply matching logic.
- Generate trade results.

The project specifies C-types, C-structs, pointers, and reduced Python-object interaction for the performance-critical matching logic.

### 4. Latency Monitor

The Latency Monitor measures order execution time using:

`time.perf_counter_ns()`

The project also uses Python `curses` to display real-time trading and performance information in the terminal.

---

## 6. Order Data

Each trading order contains three main values:

- Order ID
- Price
- Quantity

Example:

Order ID: 101  
Price: 100  
Quantity: 50

This information is handled in the memory-based communication layer.

---

## 7. Ring Buffer

A Ring Buffer is a circular storage area.

Orders are written continuously.

When the buffer reaches the end, it starts again from the beginning.

The Ring Buffer is used to handle a continuous stream of high-speed order data.

---

## 8. Order Book

The Order Book contains the current waiting Buy and Sell orders.

Example:

BUY SIDE          SELL SIDE

₹100 × 500        ₹101 × 200  
₹99 × 300         ₹102 × 400  
₹98 × 200         ₹103 × 300

The Matching Engine continuously checks these orders for possible trades.

---

## 9. Price-Time Priority

The project uses Price-Time Priority for order matching.

The two main rules are:

1. A better price gets priority.
2. If two orders have the same price, the earlier order gets priority.

For example, if multiple Buy orders have the same price, the order that arrived first gets higher priority.

---

## 10. Matching Example

Suppose the Order Book contains:

BUY ₹100 × 50  
SELL ₹100 × 30

The matching engine can match 30 shares.

After the trade:

- 30 shares are matched.
- 20 Buy shares remain in the Order Book.

This matching process is continuously performed as new orders arrive.

---

## 11. Memory Mapping

The memory-mapping part uses `mmap` and `struct`.

Order ID, Price, and Quantity are handled as raw bytes.

The purpose is to provide an efficient memory-based path for order data.

### Market Firehose

The Market Simulator uses asyncio to continuously generate mock trade orders.

The project targets 100,000 mock orders per second and sends the generated orders through the IPC layer.

### Goal

The goal is to create a fast and continuous order-data pipeline.

---

## 12. Matching Engine and Dashboard

### Matching Engine

The Cython Matching Engine handles the core trading logic.

It is responsible for:

- Maintaining the Limit Order Book.
- Applying Price-Time Priority.
- Comparing Buy and Sell orders.
- Executing matching logic.

### Dashboard

The project uses a curses-based terminal dashboard.

It can display:

- Order Book information
- Bid and Ask values
- Order processing information
- Latency and performance information

The dashboard provides real-time visibility into the trading engine.

---

## 13. Project Review

### IPC Audit

The project includes testing the IPC architecture with 1 million orders between processes.

The purpose is to verify that the memory-based communication approach can handle high-volume order transfer.

### Engine Verification

The Matching Engine must correctly match corresponding Buy and Sell orders.

This verifies that the Order Book and matching logic are functioning correctly.

---

## 14. Optimization and Metrics

The project focuses on improving the performance of the Cython Matching Engine.

Main activities include:

- Optimizing the Cython code.
- Reducing Python-object interactions.
- Using C-level types.
- Measuring execution time using `time.perf_counter_ns()`.

### Goal

The main goal is to improve performance and reduce latency.

---

## 15. Persistence and Final Polish

Matched trades are stored in a permanent ledger using SQLite or ClickHouse.

A background process is used to persist matched trades.

The terminal dashboard is also improved to provide better monitoring.

Large Whale orders can be highlighted when they clear multiple price levels.

### Goal

The final system should be stable, auditable, and suitable for demonstration.

---

## 16. Final Objective

ChronosMatch brings together:

- Python asyncio for high-volume order generation.
- mmap for memory-based communication.
- struct for raw order-data representation.
- Ring Buffer for continuous order storage.
- Cython for performance-critical matching.
- Order Book and Price-Time Priority for trade matching.
- perf_counter_ns() for latency measurement.
- curses for real-time terminal monitoring.
- SQLite or ClickHouse for trade persistence.

The overall objective is to build a low-latency trading engine that can process and match a large number of Buy and Sell orders while reducing unnecessary data transfer and monitoring execution performance.