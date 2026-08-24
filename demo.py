"""
ChronosMatch Demo - Single-process demonstration
Shows the core functionality without complex multi-process setup
"""
import time
from ring_buffer import RingBuffer
from order_book import OrderBook


def main():
    print("=" * 60)
    print("ChronosMatch Demo - Zero-Copy HFT Engine")
    print("=" * 60)
    print()
    
    # Initialize ring buffer
    print("1. Initializing ring buffer...")
    rb = RingBuffer(capacity=10000, filename="demo_mmap.bin")
    rb.create()
    rb.connect()
    print("   [OK] Ring buffer ready")
    print()
    
    # Initialize order book
    print("2. Initializing Cython order book...")
    ob = OrderBook(max_matches=1000)
    print("   [OK] Order book ready")
    print()
    
    # Simulate market data
    print("3. Simulating market order flow...")
    print()
    
    orders_sent = 0
    trades_matched = 0
    
    # Generate some realistic orders
    for i in range(100):
        order_id = i
        side = 0 if i % 2 == 0 else 1  # Alternate buy/sell
        base_price = 100.0
        price = base_price + (i % 10) * 0.25  # Price variation
        quantity = 10.0 + (i % 5) * 5.0  # Quantity variation
        
        # Write to ring buffer
        success = rb.write_order(order_id, side, price, quantity)
        if success:
            orders_sent += 1
    
    print(f"   Sent {orders_sent} orders to ring buffer")
    print()
    
    # Process orders
    print("4. Processing orders through matching engine...")
    print()
    
    latencies = []
    processed = 0
    
    while not rb.is_empty():
        order = rb.read_order()
        if order:
            order_id, side, price, quantity, timestamp_ns = order
            
            # Measure latency
            start_ns = time.perf_counter_ns()
            remaining_qty, trades = ob.add_order(order_id, side, price, quantity, timestamp_ns)
            end_ns = time.perf_counter_ns()
            
            latency_us = (end_ns - start_ns) / 1000.0
            latencies.append(latency_us)
            
            processed += 1
            trades_matched += len(trades)
            
            if i % 20 == 0:
                print(f"   Processed order {order_id}: {side} {quantity} @ {price:.2f}")
                if trades:
                    for trade in trades:
                        print(f"      -> MATCHED: {trade['quantity']} @ {trade['price']:.2f}")
    
    print()
    print(f"   Processed {processed} orders")
    print(f"   Matched {trades_matched} trades")
    print()
    
    # Performance metrics
    print("5. Performance Metrics:")
    print()
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"   Average latency: {avg_latency:.2f} us")
        print(f"   Min latency:     {min_latency:.2f} us")
        print(f"   Max latency:     {max_latency:.2f} us")
        print()
        
        if avg_latency < 50.0:
            print("   [EXCELLENT] Sub-50us target achieved!")
        else:
            print(f"   [WARNING] Above 50us target")
    print()
    
    # Order book state
    print("6. Current Order Book State:")
    print()
    top_of_book = ob.get_top_of_book(depth=5)
    
    print("   BIDS (Buy Orders):")
    for bid in top_of_book['bids'][:5]:
        whale = " WHALE!" if bid['quantity'] > 5000 else ""
        print(f"      {bid['price']:8.2f} | {bid['quantity']:10.2f}{whale}")
    
    print()
    print("   ASKS (Sell Orders):")
    for ask in top_of_book['asks'][:5]:
        whale = " WHALE!" if ask['quantity'] > 5000 else ""
        print(f"      {ask['price']:8.2f} | {ask['quantity']:10.2f}{whale}")
    
    print()
    
    # Spread
    if top_of_book['bids'] and top_of_book['asks']:
        spread = top_of_book['asks'][0]['price'] - top_of_book['bids'][0]['price']
        spread_pct = (spread / top_of_book['bids'][0]['price']) * 100
        print(f"   Spread: {spread:.2f} ({spread_pct:.3f}%)")
    print()
    
    # Statistics
    print("7. Order Book Statistics:")
    print()
    stats = ob.get_stats()
    print(f"   Total orders: {stats['order_count']}")
    print(f"   Total trades: {stats['trade_count']}")
    print()
    
    # Cleanup
    print("8. Cleanup...")
    rb.close()
    import os
    os.remove("demo_mmap.bin")
    print("   [OK] Cleaned up")
    print()
    
    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()