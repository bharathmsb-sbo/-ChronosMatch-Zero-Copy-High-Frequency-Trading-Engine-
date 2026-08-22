class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

    def add_order(self, order):
        if order["side"] == "BUY":
            self.buy_orders.append(order)
            self.buy_orders.sort(
                key=lambda x: x["price"],
                reverse=True
            )

        elif order["side"] == "SELL":
            self.sell_orders.append(order)
            self.sell_orders.sort(
                key=lambda x: x["price"]
            )

    def show_orders(self):
        print("\n=== ORDER BOOK ===")

        print("BUY Orders:")
        for order in self.buy_orders:
            print(order)

        print("\nSELL Orders:")
        for order in self.sell_orders:
            print(order)