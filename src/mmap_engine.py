# Simple Zero-Copy Memory Mapped Order Processor
import mmap
import os


BUFFER_FILE = "orders_mmap.dat"
BUFFER_SIZE = 1024  # 1 KB pre-allocated memory

# 1. Create a dummy binary file of fixed size
with open(BUFFER_FILE, "wb") as f:
    f.write(b"\x00" * BUFFER_SIZE)

print("=== Memory-Mapped (mmap) Zero-Copy Engine ===")

# 2. Open file and map into RAM memory
with open(BUFFER_FILE, "r+b") as f:
    # Map the file to memory
    mmapped_memory = mmap.mmap(f.fileno(), 0)

    # 3. Fast Zero-Copy Write (Simulating Producer / Market Ingest)
    order_data = b"ORDER_ID:1001,SIDE:BUY,PRICE:150,QTY:25"
    mmapped_memory.seek(0)
    mmapped_memory.write(order_data)
    print("Written directly to memory address:", order_data.decode("utf-8"))

    # 4. Fast Zero-Copy Read (Simulating Matching Engine Consumer)
    mmapped_memory.seek(0)
    read_data = mmapped_memory.read(len(order_data))
    print("Read directly from memory address   :", read_data.decode("utf-8"))

    # Clean up
    mmapped_memory.close()

# Remove the temp binary file
if os.path.exists(BUFFER_FILE):
    os.remove(BUFFER_FILE)

print("=== mmap Engine Demo Complete ===")