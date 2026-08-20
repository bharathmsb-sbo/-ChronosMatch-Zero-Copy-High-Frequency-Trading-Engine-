import random
import time

print("Starting Engine Performance Benchmark")

buy_orders = []
sell_orders = []
total_trades = 0

# Number of simulated orders to process
TOTAL_ORDERS = 100

# Start stopwatch
start_time = time.time()

for order_id in range(1, TOTAL_ORDERS + 1):
    side = random.choice(["BUY", "SELL"])
    
    price = random.randint(95, 105)
    quantity = random.randint(10, 50)

    order = {
        "id": order_id,
        "side": side,
        "price": price,
        "quantity": quantity
    }

    if side == "BUY":
        buy_orders.append(order)
    else:
        sell_orders.append(order)

    # Match orders
    while len(buy_orders) > 0 and len(sell_orders) > 0:
        best_buy = buy_orders[0]
        for b in buy_orders:
            if b["price"] > best_buy["price"]:
                best_buy = b

        best_sell = sell_orders[0]
        for s in sell_orders:
            if s["price"] < best_sell["price"]:
                best_sell = s

        if best_buy["price"] >= best_sell["price"]:
            if best_buy["quantity"] < best_sell["quantity"]:
                trade_qty = best_buy["quantity"]
            else:
                trade_qty = best_sell["quantity"]

            total_trades = total_trades + 1

            best_buy["quantity"] = best_buy["quantity"] - trade_qty
            best_sell["quantity"] = best_sell["quantity"] - trade_qty

            if best_buy["quantity"] == 0:
                buy_orders.remove(best_buy)
            if best_sell["quantity"] == 0:
                sell_orders.remove(best_sell)
        else:
            break

# Stop stopwatch
end_time = time.time()
total_time = end_time - start_time

print("BENCHMARK RESULTS")
print("Total Orders Processed :", TOTAL_ORDERS)
print("Total Matches Executed :", total_trades)
print("Remaining Buy Orders   :", len(buy_orders))
print("Remaining Sell Orders  :", len(sell_orders))
print("Total Execution Time   :", round(total_time, 4), "seconds")
