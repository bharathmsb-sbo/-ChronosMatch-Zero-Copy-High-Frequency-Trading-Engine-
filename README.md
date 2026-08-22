CHRONOSMATCH -ZERO-COPY-HIGH-FREQUENCY-TRADING-ENGINE


   ## The Main Objective of Our Project is-
   1.  Add buy and sell orders
   2. store the orders
   3. Match buy and sell orders 
   4. Generate the trade result
# ChronosMatch

ChronosMatch is a Python-based order matching engine designed to simulate the basic working of a high-frequency trading system.

## Features

- Order management
- BUY and SELL order handling
- Order matching
- Basic order book
- Trade execution
- Logging system

## Project Structure


ChronosMatch/
├── engine/
│   ├── __init__.py
│   ├── matching_engine.py
│   └── order_book.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── main.py
├── .gitignore
└── README.md
                ## FLOW OF PROJECT



BUY Order ──┐
            ├──> OrderBook ──> show orders
SELL Order ─┘

BUY + SELL
     ↓
MatchingEngine
     ↓
Price match?
     ↓
Executed Trade
     ↓
Logger



## How It Works

ChronosMatch works in the following steps:

1. A BUY order and a SELL order are created.
2. Both orders are added to the Order Book.
3. The Matching Engine checks the BUY and SELL orders.
4. If the BUY price is greater than or equal to the SELL price, the orders are matched.
5. The trade quantity is calculated using the smaller order quantity.
6. The executed trade is displayed in the terminal.

### Example

BUY Order:
- Price: 100
- Quantity: 10

SELL Order:
- Price: 100
- Quantity: 5

Since the BUY price (100) is equal to the SELL price (100), the orders are matched.

Executed Trade:
- Price: 100
- Quantity: 5


