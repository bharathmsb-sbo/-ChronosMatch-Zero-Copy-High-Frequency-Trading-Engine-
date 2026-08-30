from engine.matching_engine import MatchingEngine
from engine.order_book import OrderBook
from engine.ring_buffer import RingBuffer
from utils.logger import get_logger


logger = get_logger("ChronosMatch")

engine = MatchingEngine()
order_book = OrderBook()
ring_buffer = RingBuffer(capacity=10)


# Orders
orders = [
    {
        "order_id": 1,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    },
    {
        "order_id": 2,
        "side": "BUY",
        "price": 101,
        "quantity": 5
    },
    {
        "order_id": 3,
        "side": "SELL",
        "price": 100,
        "quantity": 8
    },
    {
        "order_id": 4,
        "side": "SELL",
        "price": 102,
        "quantity": 4
    }
]


# Write orders into memory-mapped ring buffer
for order in orders:
    ring_buffer.write(
        order["order_id"],
        order["side"],
        order["price"],
        order["quantity"]
    )


# Read orders from ring buffer
while True:
    order = ring_buffer.read()

    if order is None:
        break

    order_book.add_order(order)
    engine.add_order(order)


# Show Order Book
order_book.show_orders()

# Cancel Order
engine.cancel_order(2)
order_book.cancel_order(2)
print("\nOrder Book After Cancellation:")
order_book.show_orders()




# Match Orders
trades = engine.match_orders()

logger.info("Order matching completed")


# Display Results
print("\nExecuted Trades:")
print(trades)

print("\nRemaining BUY Orders:")
print(engine.buy_orders)

print("\nRemaining SELL Orders:")
print(engine.sell_orders)