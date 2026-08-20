import random
import time

print("Starting Simple Market Simulator")

orders = []

# Generate 5 sample orders step-by-step
for order_id in range(1, 6):
    # Random side: BUY or SELL
    side = random.choice(["BUY", "SELL"])
    
    # Random price and quantity
    price = random.randint(95, 105)
    quantity = random.randint(10, 50)
    
    # Create simple order dictionary
    order = {
        "id": order_id,
        "side": side,
        "price": price,
        "quantity": quantity
    }
    
    orders.append(order)
    
    print("New Order Created:", order)
    time.sleep(1)  # 1-second delay so you can see it printing live

print("\nAll Orders Created")
print(orders)