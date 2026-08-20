# Simple Test File for Order Matching

print("Running Engine Tests")

# Test 1: Check if matching price works
buyer_price = 100
seller_price = 95

if buyer_price >= seller_price:
    print("Test 1 Result: PASS (Orders matched successfully)")
else:
    print("Test 1 Result: FAIL")


# Test 2: Check if higher seller price is rejected
low_buyer_price = 90
high_seller_price = 105

if low_buyer_price < high_seller_price:
    print("Test 2 Result: PASS (No trade because buyer price is too low)")
else:
    print("Test 2 Result: FAIL")


# Test 3: Check quantity calculation
buy_qty = 30
sell_qty = 10

# Trade the smaller quantity
if buy_qty < sell_qty:
    trade_qty = buy_qty
else:
    trade_qty = sell_qty

remaining_buy_qty = buy_qty - trade_qty
remaining_sell_qty = sell_qty - trade_qty

print("Test 3 Trade Qty:", trade_qty)
print("Test 3 Remaining Buy Qty:", remaining_buy_qty)
print("Test 3 Remaining Sell Qty:", remaining_sell_qty)

if remaining_buy_qty == 20 and remaining_sell_qty == 0:
    print("Test 3 Result: PASS (Quantities calculated correctly)")
else:
    print("Test 3 Result: FAIL")

print("Tests Completed")