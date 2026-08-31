from utils.logger import get_logger


cdef class MatchingEngine:
    cdef public list buy_orders
    cdef public list sell_orders
    cdef int sequence
    cdef object logger

    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.sequence = 0
        self.logger = get_logger("MatchingEngine")

    def add_order(self, dict order):
        if "order_id" not in order:
            raise ValueError("Order ID is required")

        if order["side"] not in ["BUY", "SELL"]:
            raise ValueError("Invalid order side")

        if order["price"] <= 0:
            raise ValueError("Price must be greater than 0")

        if order["quantity"] <= 0:
            raise ValueError("Quantity must be greater than 0")

        self.sequence += 1
        order["sequence"] = self.sequence

        if order["side"] == "BUY":
            self.buy_orders.append(order)
        else:
            self.sell_orders.append(order)

        self.logger.info(f"Order added: {order}")

    def cancel_order(self, order_id):
        cdef dict order

        for order in self.buy_orders:
            if order["order_id"] == order_id:
                self.buy_orders.remove(order)
                self.logger.info(f"Order cancelled: {order}")
                return True

        for order in self.sell_orders:
            if order["order_id"] == order_id:
                self.sell_orders.remove(order)
                self.logger.info(f"Order cancelled: {order}")
                return True

        self.logger.warning(f"Order not found: {order_id}")
        return False

    def modify_order(self, order_id, price=None, quantity=None):
        cdef dict order = None
        cdef dict existing_order

        for existing_order in self.buy_orders:
            if existing_order["order_id"] == order_id:
                order = existing_order
                break

        if order is None:
            for existing_order in self.sell_orders:
                if existing_order["order_id"] == order_id:
                    order = existing_order
                    break

        if order is None:
            self.logger.warning(
                f"Order not found for modification: {order_id}"
            )
            return False

        if price is not None and price <= 0:
            raise ValueError("Price must be greater than 0")

        if quantity is not None and quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        if price is not None:
            order["price"] = price

        if quantity is not None:
            order["quantity"] = quantity

        # Modified order gets new time priority
        self.sequence += 1
        order["sequence"] = self.sequence

        self.logger.info(f"Order modified: {order}")

        return True

    def match_orders(self):
        cdef list trades = []
        cdef dict buy
        cdef dict sell
        cdef dict trade
        cdef int trade_quantity

        # Price-Time Priority
        self.buy_orders.sort(
            key=lambda x: (-x["price"], x["sequence"])
        )

        self.sell_orders.sort(
            key=lambda x: (x["price"], x["sequence"])
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
            order
            for order in self.buy_orders
            if order["quantity"] > 0
        ]

        self.sell_orders = [
            order
            for order in self.sell_orders
            if order["quantity"] > 0
        ]

        return trades