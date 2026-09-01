import mmap
import struct


class RingBuffer:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        self.record_size = struct.calcsize("iiii")

        self.memory = mmap.mmap(
            -1,
            self.capacity * self.record_size
        )

        self.write_index = 0
        self.read_index = 0

    def write(self, order_id, side, price, quantity):
        side_value = 1 if side == "BUY" else 2

        position = self.write_index % self.capacity
        offset = position * self.record_size

        self.memory.seek(offset)

        self.memory.write(
            struct.pack(
                "iiii",
                order_id,
                side_value,
                price,
                quantity
            )
        )

        self.write_index += 1

    def read(self):
        if self.read_index >= self.write_index:
            return None

        position = self.read_index % self.capacity
        offset = position * self.record_size

        self.memory.seek(offset)

        data = self.memory.read(self.record_size)

        self.read_index += 1

        order_id, side_value, price, quantity = struct.unpack(
            "iiii", data
        )

        side = "BUY" if side_value == 1 else "SELL"

        return {
            "order_id": order_id,
            "side": side,
            "price": price,
            "quantity": quantity
        }