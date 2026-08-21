class MatchingEngine:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def add_order(self, order):
        if order["side"] == "BUY":
            self.buy_orders.append(order)
        elif order["side"] == "SELL":
            self.sell_orders.append(order)

    def match_orders(self):
        trades = []

        for buy in self.buy_orders:
            for sell in self.sell_orders:
                if buy["price"] >= sell["price"]:
                    trades.append({
                        "buy_order": buy["order_id"],
                        "sell_order": sell["order_id"],
                        "price": sell["price"],
                        "quantity": min(
                            buy["quantity"],
                            sell["quantity"]
                        )
                    })

        return trades