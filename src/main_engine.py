import random
import time

# Lists to store remaining orders
buy_orders = []
sell_orders = []

print("Simple ChronosMatch Engine")

# Create and match 5 orders one by one
for order_id in range(1, 6):
    # Step 1: Make a random order
    side = random.choice(["BUY", "SELL"])
    price = random.randint(98, 102)
    quantity = random.randint(10, 30)

    new_order = {
        "id": order_id,
        "side": side,
        "price": price,
        "quantity": quantity
    }

    print("New Incoming Order:", new_order)

    # Step 2: Add order to the correct list
    if side == "BUY":
        buy_orders.append(new_order)
    else:
        sell_orders.append(new_order)

    # Step 3: Check and match orders
    while len(buy_orders) > 0 and len(sell_orders) > 0:
        
        # Find best Buy order (Highest price)
        best_buy = buy_orders[0]
        for order in buy_orders:
            if order["price"] > best_buy["price"]:
                best_buy = order

        # Find best Sell order (Lowest price)
        best_sell = sell_orders[0]
        for order in sell_orders:
            if order["price"] < best_sell["price"]:
                best_sell = order

        # If Buy price is equal or higher than Sell price, execute trade
        if best_buy["price"] >= best_sell["price"]:
            
            # Find trade quantity
            if best_buy["quantity"] < best_sell["quantity"]:
                trade_quantity = best_buy["quantity"]
            else:
                trade_quantity = best_sell["quantity"]

            print("\nMatch Success!")
            print("Trade Price   :", best_sell["price"])
            print("Trade Quantity:", trade_quantity)
            print("Matched Order ID", best_buy["id"], "with", best_sell["id"])

            # Deduct traded quantity
            best_buy["quantity"] = best_buy["quantity"] - trade_quantity
            best_sell["quantity"] = best_sell["quantity"] - trade_quantity

            # Remove finished orders
            if best_buy["quantity"] == 0:
                buy_orders.remove(best_buy)
            if best_sell["quantity"] == 0:
                sell_orders.remove(best_sell)
                
        else:
            # No matching price spread
            break

    # Show book status after each incoming order
    print("Open Buy Orders :", buy_orders)
    print("Open Sell Orders:", sell_orders)

    time.sleep(1)

print("\nSimulation Finished")