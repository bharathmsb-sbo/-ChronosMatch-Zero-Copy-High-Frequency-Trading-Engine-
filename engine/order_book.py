class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def add_order(self, order):
        if order["side"] == "BUY":
            self.buy_orders.append(order)
        elif order["side"] == "SELL":
            self.sell_orders.append(order)

    def show_orders(self):
        print("BUY Orders:", self.buy_orders)
        print("SELL Orders:", self.sell_orders)