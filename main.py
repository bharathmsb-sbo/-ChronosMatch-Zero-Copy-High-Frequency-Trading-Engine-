from engine.matching_engine import MatchingEngine
from engine.order_book import OrderBook
from utils.logger import get_logger

logger = get_logger("ChronosMatch")
engine = MatchingEngine()
order_book = OrderBook()

buy_order = {
    "order_id": 1,
    "side": "BUY",
    "price": 100,
    "quantity": 10
}

sell_order = {
    "order_id": 2,
    "side": "SELL",
    "price": 100,
    "quantity": 5
}

order_book.add_order(buy_order)
order_book.add_order(sell_order)

engine.add_order(buy_order)
engine.add_order(sell_order)

order_book.show_orders()

trades = engine.match_orders()
logger.info("Order matching completed")
print("Executed Trades:")
print(trades)