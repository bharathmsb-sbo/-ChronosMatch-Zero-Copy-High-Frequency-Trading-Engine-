from engine.ring_buffer import RingBuffer


buffer = RingBuffer(capacity=10)

buffer.write(1, "BUY", 100, 10)

buffer.write(2, "BUY", 101, 5)

print("Order 1:", buffer.read())

print("Order 2:", buffer.read())

print("Empty:", buffer.read())