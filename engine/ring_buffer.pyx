import mmap
import struct


cdef class RingBuffer:
    cdef int capacity
    cdef int record_size
    cdef int write_index
    cdef int read_index
    cdef object memory

    def __init__(self, int capacity=1024):
        self.capacity = capacity
        self.record_size = struct.calcsize("iiii")

        self.memory = mmap.mmap(
            -1,
            self.capacity * self.record_size
        )

        self.write_index = 0
        self.read_index = 0

    def write(self, int order_id, str side, int price, int quantity):
        cdef int side_value
        cdef int position
        cdef int offset

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
        cdef int position
        cdef int offset
        cdef int order_id
        cdef int side_value
        cdef int price
        cdef int quantity
        cdef bytes data

        if self.read_index >= self.write_index:
            return None

        position = self.read_index % self.capacity
        offset = position * self.record_size

        self.memory.seek(offset)

        data = self.memory.read(self.record_size)

        self.read_index += 1

        order_id, side_value, price, quantity = struct.unpack(
            "iiii",
            data
        )

        return {
            "order_id": order_id,
            "side": "BUY" if side_value == 1 else "SELL",
            "price": price,
            "quantity": quantity
        }