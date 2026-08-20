buy_price = 100
buy_quantity = 50

sell_price = 100
sell_quantity = 30


print("Buy Order:")
print("Price:", buy_price)
print("Quantity:", buy_quantity)

print("\nSell Order:")
print("Price:", sell_price)
print("Quantity:", sell_quantity)


# Check whether the orders can match
if buy_price >= sell_price:

    matched_quantity = min(buy_quantity, sell_quantity)

    print("\nOrder Matched!")
    print("Price:", sell_price)
    print("Quantity:", matched_quantity)

else:

    print("\nOrders cannot be matched.")