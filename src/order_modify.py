# Simple Order Modification Module

def modify_order(order_book, order_id, new_price=None, new_qty=None):
    """
    Updates the price or quantity of an existing active order by its ID.
    """
    # Search in Buy side (bids) and Sell side (asks)
    for side in ["bids", "asks"]:
        for order in order_book[side]:
            if order["id"] == order_id:
                old_price = order["price"]
                old_qty = order["qty"]

                if new_price is not None:
                    order["price"] = new_price
                if new_qty is not None:
                    order["qty"] = new_qty

                return (
                    f"Order {order_id} modified successfully: "
                    f"Price ({old_price} -> {order['price']}), "
                    f"Qty ({old_qty} -> {order['qty']})"
                )

    return f"Order {order_id} not found."

# Demo Test Run
if __name__ == "__main__":
    sample_book = {
        "bids": [{"id": 101, "price": 100, "qty": 10}],
        "asks": [{"id": 201, "price": 105, "qty": 15}]
    }

    print("Before Modification")
    print("Bids:", sample_book["bids"])

    print("\nModifying Order 101")
    result = modify_order(sample_book, order_id=101, new_price=102, new_qty=20)
    print(result)

    print("\nAfter Modification")
    print("Bids:", sample_book["bids"])