# Simple script to export trades into a CSV file

print("Starting Trade Export to CSV")

# 1. Sample list of matched trades
sample_trades = [
    {"trade_id": 1, "buyer_id": 101, "seller_id": 201, "price": 100, "quantity": 15},
    {"trade_id": 2, "buyer_id": 102, "seller_id": 202, "price": 99,  "quantity": 25},
    {"trade_id": 3, "buyer_id": 103, "seller_id": 203, "price": 101, "quantity": 10},
    {"trade_id": 4, "buyer_id": 104, "seller_id": 204, "price": 98,  "quantity": 30}
]

# 2. File path where we want to save
file_name = "trades.csv"

# 3. Open file in write mode ('w')
file = open(file_name, "w")

# 4. Write column headers
file.write("Trade_ID,Buyer_ID,Seller_ID,Price,Quantity\n")

# 5. Write each trade row
for trade in sample_trades:
    row = str(trade["trade_id"]) + "," + str(trade["buyer_id"]) + "," + str(trade["seller_id"]) + "," + str(trade["price"]) + "," + str(trade["quantity"]) + "\n"
    file.write(row)

# 6. Close the file
file.close()

print("Success! Trades saved to", file_name)
print("Export Finished")