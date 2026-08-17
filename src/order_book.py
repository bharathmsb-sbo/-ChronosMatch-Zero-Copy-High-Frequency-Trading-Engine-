# Buy Orders

buy_orders = [
    {"id": 1, "price": 100, "quantity": 50},
    {"id": 2, "price": 99, "quantity": 40},
    {"id": 3, "price": 98, "quantity": 20}
]


# Sell Orders

sell_orders = [
    {"id": 4, "price": 100, "quantity": 30},
    {"id": 5, "price": 101, "quantity": 50},
    {"id": 6, "price": 102, "quantity": 20}
]


# Keep checking while Buy and Sell orders are available

while len(buy_orders) > 0 and len(sell_orders) > 0:

    # Take the first Buy and Sell orders

    buy_order = buy_orders[0]
    sell_order = sell_orders[0]


    # Find the best Buy order
    # Higher price gets priority

    best_buy = buy_order

    for order in buy_orders:
        if order["price"] > best_buy["price"]:
            best_buy = order


    # Find the best Sell order
    # Lower price gets priority

    best_sell = sell_order

    for order in sell_orders:
        if order["price"] < best_sell["price"]:
            best_sell = order


    # Display the best orders

    print("\nBest Buy:")
    print(best_buy)

    print("\nBest Sell:")
    print(best_sell)


    # Check whether orders can match

    if best_buy["price"] >= best_sell["price"]:

        # Find the smaller quantity

        if best_buy["quantity"] < best_sell["quantity"]:
            matched_quantity = best_buy["quantity"]
        else:
            matched_quantity = best_sell["quantity"]


        # Trade result

        print("\nOrder Matched!")
        print("Price:", best_sell["price"])
        print("Quantity:", matched_quantity)


        # Update remaining quantity

        best_buy["quantity"] = (
            best_buy["quantity"] - matched_quantity
        )

        best_sell["quantity"] = (
            best_sell["quantity"] - matched_quantity
        )


        # Remove completed Buy order

        if best_buy["quantity"] == 0:
            buy_orders.remove(best_buy)


        # Remove completed Sell order

        if best_sell["quantity"] == 0:
            sell_orders.remove(best_sell)


        # Show remaining orders

        print("\nRemaining Buy Orders:")
        print(buy_orders)

        print("\nRemaining Sell Orders:")
        print(sell_orders)


    else:

        print("\nNo Match")
        break