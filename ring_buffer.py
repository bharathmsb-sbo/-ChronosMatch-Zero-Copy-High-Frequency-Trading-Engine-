"""
Zero-Copy IPC Ring Buffer using mmap and struct
Week 1: Memory Mapping Implementation
"""
import mmap
import struct
import os
from typing import Optional
import time

# Order struct format: order_id (8 bytes), side (1 byte), price (8 bytes), quantity (8 bytes), timestamp (8 bytes)
ORDER_STRUCT_FORMAT = '=Q B d d Q'
ORDER_STRUCT_SIZE = struct.calcsize(ORDER_STRUCT_FORMAT)

# Ring buffer metadata: head (8 bytes), tail (8 bytes), capacity (8 bytes)
METADATA_FORMAT = '=Q Q Q'
METADATA_SIZE = struct.calcsize(METADATA_FORMAT)


class RingBuffer:
    """
    Memory-mapped ring buffer for zero-copy IPC between processes.
    Uses raw bytes for maximum performance - no serialization overhead.
    """
    
    def __init__(self, capacity: int = 1000000, filename: str = "chronos_mmap.bin"):
        self.capacity = capacity
        self.filename = filename
        self.buffer_size = METADATA_SIZE + (capacity * ORDER_STRUCT_SIZE)
        self._mmap: Optional[mmap.mmap] = None
        self._file = None
        
    def create(self) -> None:
        """Create and initialize the memory-mapped file."""
        # Create file with required size
        with open(self.filename, 'wb') as f:
            f.write(b'\x00' * self.buffer_size)
        
        # Initialize metadata
        with open(self.filename, 'r+b') as f:
            # head = 0, tail = 0, capacity = capacity
            metadata = struct.pack(METADATA_FORMAT, 0, 0, self.capacity)
            f.write(metadata)
    
    def connect(self) -> None:
        """Connect to existing memory-mapped file."""
        self._file = open(self.filename, 'r+b')
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_WRITE)
    
    def close(self) -> None:
        """Close the memory-mapped file."""
        if self._mmap:
            self._mmap.close()
        if self._file:
            self._file.close()
    
    def _read_metadata(self) -> tuple[int, int, int]:
        """Read head, tail, and capacity from metadata."""
        self._mmap.seek(0)
        data = self._mmap.read(METADATA_SIZE)
        return struct.unpack(METADATA_FORMAT, data)
    
    def _write_metadata(self, head: int, tail: int) -> None:
        """Write head and tail to metadata."""
        self._mmap.seek(0)
        metadata = struct.pack(METADATA_FORMAT, head, tail, self.capacity)
        self._mmap.write(metadata)
    
    def write_order(self, order_id: int, side: int, price: float, quantity: float) -> bool:
        """
        Write an order to the ring buffer.
        Returns True if successful, False if buffer is full.
        """
        head, tail, capacity = self._read_metadata()
        
        # Check if buffer is full
        if (head + 1) % capacity == tail:
            return False
        
        # Calculate position to write
        pos = METADATA_SIZE + (head * ORDER_STRUCT_SIZE)
        
        # Pack order data
        timestamp = time.time_ns()
        order_data = struct.pack(ORDER_STRUCT_FORMAT, order_id, side, price, quantity, timestamp)
        
        # Write to memory
        self._mmap.seek(pos)
        self._mmap.write(order_data)
        
        # Update head
        new_head = (head + 1) % capacity
        self._write_metadata(new_head, tail)
        
        return True
    
    def read_order(self) -> Optional[tuple[int, int, float, float, int]]:
        """
        Read an order from the ring buffer.
        Returns (order_id, side, price, quantity, timestamp) or None if buffer is empty.
        """
        head, tail, capacity = self._read_metadata()
        
        # Check if buffer is empty
        if head == tail:
            return None
        
        # Calculate position to read
        pos = METADATA_SIZE + (tail * ORDER_STRUCT_SIZE)
        
        # Read from memory
        self._mmap.seek(pos)
        order_data = self._mmap.read(ORDER_STRUCT_SIZE)
        
        # Unpack order data
        order_id, side, price, quantity, timestamp = struct.unpack(ORDER_STRUCT_FORMAT, order_data)
        
        # Update tail
        new_tail = (tail + 1) % capacity
        self._write_metadata(head, new_tail)
        
        return (order_id, side, price, quantity, timestamp)
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        head, tail, _ = self._read_metadata()
        return head == tail
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        head, tail, capacity = self._read_metadata()
        return (head + 1) % capacity == tail
    
    def get_stats(self) -> dict:
        """Get buffer statistics."""
        head, tail, capacity = self._read_metadata()
        if head >= tail:
            count = head - tail
        else:
            count = capacity - tail + head
        return {
            'head': head,
            'tail': tail,
            'capacity': capacity,
            'count': count,
            'available': capacity - count - 1
        }


if __name__ == "__main__":
    # Test the ring buffer
    print("Testing Ring Buffer...")
    
    rb = RingBuffer(capacity=100, filename="test_mmap.bin")
    rb.create()
    rb.connect()
    
    # Write some orders
    for i in range(50):
        success = rb.write_order(order_id=i, side=0 if i % 2 == 0 else 1, 
                                 price=100.0 + i * 0.01, quantity=10.0 + i)
        assert success, f"Failed to write order {i}"
    
    print(f"Stats after writing 50 orders: {rb.get_stats()}")
    
    # Read orders
    while not rb.is_empty():
        order = rb.read_order()
        if order:
            print(f"Read order: ID={order[0]}, Side={order[1]}, Price={order[2]}, Qty={order[3]}")
    
    print(f"Stats after reading all orders: {rb.get_stats()}")
    
    rb.close()
    
    # Cleanup
    os.remove("test_mmap.bin")
    print("Ring buffer test completed successfully!")
