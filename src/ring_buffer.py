# Simple Circular Ring Buffer for High-Speed Order Handling

class OrderRingBuffer:
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.write_idx = 0
        self.read_idx = 0
        self.count = 0

    def push(self, order):
        """Adds an order to the ring buffer (Zero re-allocation)."""
        if self.count == self.capacity:
            print("[Buffer Full] Overwriting oldest slot or waiting...")
            return False

        self.buffer[self.write_idx] = order
        print(f"[PUSH] Slot {self.write_idx} -> Order: {order}")
        self.write_idx = (self.write_idx + 1) % self.capacity
        self.count += 1
        return True

    def pop(self):
        """Reads and processes the next order."""
        if self.count == 0:
            print("[Buffer Empty] No orders to process.")
            return None

        order = self.buffer[self.read_idx]
        print(f"[POP]  Slot {self.read_idx} -> Order: {order}")
        self.read_idx = (self.read_idx + 1) % self.capacity
        self.count -= 1
        return order


# Quick Verification
if __name__ == "__main__":
    print("=== Testing Ring Buffer ===")
    rb = OrderRingBuffer(capacity=3)

    # Push 3 orders to fill the ring
    rb.push({"id": 101, "price": 100, "qty": 10})
    rb.push({"id": 102, "price": 101, "qty": 20})
    rb.push({"id": 103, "price": 102, "qty": 15})

    # Read one order to free up a slot
    rb.pop()

    # Push a 4th order (wraps around to slot 0)
    rb.push({"id": 104, "price": 105, "qty": 50})
    print("=== Ring Buffer Test Complete ===")