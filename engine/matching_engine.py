from utils.logger import get_logger


class MatchingEngine:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.logger = get_logger("MatchingEngine")

    def add_order(self, order):
        if "order_id" not in order:
            raise ValueError("Order ID is required")

        if order["side"] not in ["BUY", "SELL"]:
            raise ValueError("Invalid order side")

        if order["price"] <= 0:
            raise ValueError("Price must be greater than 0")

        if order["quantity"] <= 0:
            raise ValueError("Quantity must be greater than 0")

        if order["side"] == "BUY":
            self.buy_orders.append(order)

        elif order["side"] == "SELL":
            self.sell_orders.append(order)

        self.logger.info(
            f"Order added: {order}"
        )

    def cancel_order(self, order_id):
        # Search in BUY orders
        for order in self.buy_orders:
            if order["order_id"] == order_id:
                self.buy_orders.remove(order)

                self.logger.info(
                    f"Order cancelled: {order}"
                )

                return True

        # Search in SELL orders
        for order in self.sell_orders:
            if order["order_id"] == order_id:
                self.sell_orders.remove(order)

                self.logger.info(
                    f"Order cancelled: {order}"
                )

                return True

        self.logger.warning(
            f"Order not found: {order_id}"
        )

        return False

    def match_orders(self):
        trades = []

        self.buy_orders.sort(
            key=lambda x: x["price"],
            reverse=True
        )

        self.sell_orders.sort(
            key=lambda x: x["price"]
        )

        for buy in self.buy_orders:
            for sell in self.sell_orders:

                if buy["quantity"] == 0 or sell["quantity"] == 0:
                    continue

                if buy["price"] >= sell["price"]:

                    trade_quantity = min(
                        buy["quantity"],
                        sell["quantity"]
                    )

                    trade = {
                        "buy_order": buy["order_id"],
                        "sell_order": sell["order_id"],
                        "price": sell["price"],
                        "quantity": trade_quantity
                    }

                    trades.append(trade)

                    buy["quantity"] -= trade_quantity
                    sell["quantity"] -= trade_quantity

                    self.logger.info(
                        f"Trade executed: {trade}"
                    )

        self.buy_orders = [
            order for order in self.buy_orders
            if order["quantity"] > 0
        ]

        self.sell_orders = [
            order for order in self.sell_orders
            if order["quantity"] > 0
        ]

        return trades
