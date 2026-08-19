# Simple Interactive Terminal Trading

print("Manual Order Entry Engine")

# Existing orders in the market
existing_sell_orders = [
    {"id": 1, "price": 102, "quantity": 20},
    {"id": 2, "price": 100, "quantity": 10},
    {"id": 3, "price": 105, "quantity": 15}
]

print("\nCurrent Available Sell Orders")
for s in existing_sell_orders:
    print("Order ID:", s["id"], "| Price:", s["price"], "| Quantity:", s["quantity"])

print("\nEnter Your Buy Order")
user_price = int(input("Enter your Buy Price (e.g. 100): "))
user_qty = int(input("Enter your Buy Quantity (e.g. 10): "))

# Find best (lowest) sell price
best_seller = existing_sell_orders[0]
for s in existing_sell_orders:
    if s["price"] < best_seller["price"]:
        best_seller = s

print("\nMatching Result")
if user_price >= best_seller["price"]:
    if user_qty < best_seller["quantity"]:
        trade_qty = user_qty
    else:
        trade_qty = best_seller["quantity"]

    print("TRADE EXECUTED!")
    print("Matched with Seller Order ID:", best_seller["id"])
    print("Execution Price:", best_seller["price"])
    print("Traded Quantity:", trade_qty)
else:
    print("NO TRADE: Your price", user_price, "is too low for lowest seller at", best_seller["price"])

print("\nFinished")