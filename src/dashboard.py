# Simple Order Book Dashboard Display

print("==========================================")
print("       LIVE MARKET ORDER BOOK            ")
print("==========================================")

# Current open buy orders (bids)
bids = [
    {"price": 102, "qty": 15},
    {"price": 101, "qty": 20},
    {"price": 100, "qty": 50}
]

# Current open sell orders (asks)
asks = [
    {"price": 103, "qty": 10},
    {"price": 104, "qty": 25},
    {"price": 106, "qty": 40}
]

print("   BUY ORDERS (BIDS)   |   SELL ORDERS (ASKS)  ")
print("------------------------------------------")
print(" Price   | Quantity    | Price   | Quantity   ")
print("------------------------------------------")

# Display top 3 levels
for i in range(3):
    bid_str = f" ${bids[i]['price']:<6} | {bids[i]['qty']:<11}"
    ask_str = f"| ${asks[i]['price']:<6} | {asks[i]['qty']:<10}"
    print(bid_str + ask_str)

print("------------------------------------------")
spread = asks[0]["price"] - bids[0]["price"]
print(f"Market Spread (Lowest Ask - Highest Bid): ${spread}")
print("==========================================")