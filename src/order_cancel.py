# Simple Order Cancellation Module

def cancel_order(order_book, order_id_to_cancel):
    """
    Finds and removes an active resting order by ID.
    """
    # Check buy side
    for i, order in enumerate(order_book["bids"]):
        if order["id"] == order_id_to_cancel:
            cancelled = order_book["bids"].pop(i)
            return f"Order {cancelled['id']} (BUY {cancelled['qty']} @ ${cancelled['price']}) CANCELLED."

    # Check sell side
    for i, order in enumerate(order_book["asks"]):
        if order["id"] == order_id_to_cancel:
            cancelled = order_book["asks"].pop(i)
            return f"Order {cancelled['id']} (SELL {cancelled['qty']} @ ${cancelled['price']}) CANCELLED."

    return f"Order {order_id_to_cancel} not found."

# Demo Test Run
if __name__ == "__main__":
    sample_book = {
        "bids": [{"id": 1, "price": 100, "qty": 10}, {"id": 2, "price": 99, "qty": 5}],
        "asks": [{"id": 3, "price": 105, "qty": 15}]
    }
    
    print("Initial Bids:", sample_book["bids"])
    print(cancel_order(sample_book, 1))
    print("Updated Bids:", sample_book["bids"])