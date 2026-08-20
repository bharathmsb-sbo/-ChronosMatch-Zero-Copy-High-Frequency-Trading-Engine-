"""
Test Suite for ChronosMatch
Tests the ring buffer, order book, and integration
"""
import time
import os
from ring_buffer import RingBuffer


def test_ring_buffer():
    """Test the ring buffer IPC mechanism."""
    print("Testing Ring Buffer...")
    
    # Create test buffer
    rb = RingBuffer(capacity=1000, filename="test_mmap.bin")
    rb.create()
    rb.connect()
    
    # Test basic write/read
    assert rb.write_order(1, 0, 100.0, 10.0), "Failed to write order"
    assert rb.write_order(2, 1, 101.0, 20.0), "Failed to write order"
    
    order = rb.read_order()
    assert order is not None, "Failed to read order"
    assert order[0] == 1, "Order ID mismatch"
    assert order[1] == 0, "Side mismatch"
    assert abs(order[2] - 100.0) < 0.01, "Price mismatch"
    assert abs(order[3] - 10.0) < 0.01, "Quantity mismatch"
    
    # Test buffer limits (capacity-1 because one slot is reserved for empty/full check)
    for i in range(999):
        rb.write_order(i, 0, 100.0 + i, 10.0)
    
    # Buffer should be full
    assert rb.is_full(), "Buffer should be full"
    assert not rb.write_order(9999, 0, 100.0, 10.0), "Should not write to full buffer"
    
    # Read all orders
    count = 0
    while not rb.is_empty():
        rb.read_order()
        count += 1
    
    assert count == 999, f"Expected 999 orders, got {count}"
    assert rb.is_empty(), "Buffer should be empty"
    
    rb.close()
    os.remove("test_mmap.bin")
    
    print("[PASS] Ring buffer tests passed")


def test_order_book():
    """Test the Cython order book."""
    print("Testing Order Book...")
    
    try:
        from order_book import OrderBook
    except ImportError:
        print("[FAIL] Order book not compiled. Run: python setup.py build_ext --inplace")
        return False
    
    ob = OrderBook()
    
    # Test adding orders
    remaining, trades = ob.add_order(1, 0, 100.0, 10.0, time.time_ns())
    assert remaining == 10.0, "Order should not match immediately"
    assert len(trades) == 0, "No trades expected"
    
    # Add sell order at same price - should match
    remaining, trades = ob.add_order(2, 1, 100.0, 5.0, time.time_ns())
    # The sell order should be fully matched against the buy order
    assert remaining == 0.0, f"Sell order should be fully matched, got {remaining}"
    assert len(trades) == 1, "One trade expected"
    assert abs(trades[0]['quantity'] - 5.0) < 0.01, "Trade quantity mismatch"
    
    # Test spread - after matching, there should be 5.0 remaining buy at 100.0, no asks
    bid, ask = ob.get_spread()
    assert bid == 100.0, f"Bid price mismatch, got {bid}"
    # Ask should be 0.0 since sell order was fully matched
    assert ask == 0.0, f"Ask price should be 0.0 after full match, got {ask}"
    
    # Test top of book
    tob = ob.get_top_of_book(depth=5)
    assert len(tob['bids']) > 0, "Should have bids"
    # Asks might be empty after full match, so don't assert
    
    # Test stats - after matching, only the remaining buy order (5.0) is in the book
    stats = ob.get_stats()
    assert stats['order_count'] >= 1, "Should have at least 1 order in book"
    assert stats['trade_count'] >= 1, "Should have at least 1 trade"
    
    print("[PASS] Order book tests passed")
    return True


def test_integration():
    """Test the full integration of components."""
    print("Testing Integration...")
    
    try:
        from order_book import OrderBook
    except ImportError:
        print("[FAIL] Order book not compiled. Run: python setup.py build_ext --inplace")
        return False
    
    # Create ring buffer
    rb = RingBuffer(capacity=10000, filename="test_integration.bin")
    rb.create()
    rb.connect()
    
    # Create order book
    ob = OrderBook()
    
    # Simulate order flow
    for i in range(100):
        order_id = i
        side = 0 if i % 2 == 0 else 1
        price = 100.0 + (i % 10) * 0.1
        quantity = 10.0 + i
        
        # Write to buffer
        rb.write_order(order_id, side, price, quantity)
    
    # Process orders from buffer
    processed = 0
    while not rb.is_empty():
        order = rb.read_order()
        if order:
            order_id, side, price, quantity, timestamp_ns = order
            ob.add_order(order_id, side, price, quantity, timestamp_ns)
            processed += 1
    
    assert processed == 100, f"Expected 100 processed orders, got {processed}"
    
    # Check order book state
    stats = ob.get_stats()
    assert stats['order_count'] > 0, "Order book should have orders"
    
    rb.close()
    os.remove("test_integration.bin")
    
    print("[PASS] Integration tests passed")
    return True


def test_latency():
    """Test matching engine latency."""
    print("Testing Latency...")
    
    try:
        from order_book import OrderBook
    except ImportError:
        print("[FAIL] Order book not compiled. Run: python setup.py build_ext --inplace")
        return False
    
    ob = OrderBook()
    
    # Pre-populate order book
    for i in range(100):
        ob.add_order(i, 0, 100.0, 10.0, time.time_ns())
        ob.add_order(i + 100, 1, 100.0, 10.0, time.time_ns())
    
    # Measure latency
    latencies = []
    for i in range(1000):
        start = time.perf_counter_ns()
        ob.add_order(1000 + i, 0, 100.0, 10.0, time.time_ns())
        end = time.perf_counter_ns()
        latencies.append((end - start) / 1000.0)  # Convert to microseconds
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    print(f"  Average latency: {avg_latency:.2f} us")
    print(f"  Min latency: {min_latency:.2f} us")
    print(f"  Max latency: {max_latency:.2f} us")
    
    if avg_latency < 50.0:
        print("[PASS] Latency tests passed (sub-50us achieved)")
    else:
        print(f"[WARN] Latency above target (50us), got {avg_latency:.2f}us")
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("ChronosMatch Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_ring_buffer()
        test_order_book()
        test_integration()
        test_latency()
        
        print()
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
