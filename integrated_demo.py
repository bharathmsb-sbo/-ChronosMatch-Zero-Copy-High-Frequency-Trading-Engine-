"""
Integrated ChronosMatch Demo - Full System Running Together
Demonstrates the complete HFT pipeline: Simulator → Ring Buffer → Matching Engine → Dashboard
"""
import time
import threading
from ring_buffer import RingBuffer
from order_book import OrderBook
from market_simulator import MarketSimulator
import random


class IntegratedSystem:
    """Complete ChronosMatch system running in a single process for demonstration."""
    
    def __init__(self):
        self.ring_buffer = RingBuffer(capacity=100000, filename="integrated_mmap.bin")
        self.order_book = OrderBook(max_matches=1000)
        self.running = False
        self.stats = {
            'orders_sent': 0,
            'orders_processed': 0,
            'trades_matched': 0,
            'latency_samples': []
        }
        self.lock = threading.Lock()
    
    def initialize(self):
        """Initialize all components."""
        print("Initializing ChronosMatch System...")
        print("-" * 60)
        
        # Create ring buffer
        self.ring_buffer.create()
        self.ring_buffer.connect()
        print("[OK] Ring buffer initialized (100K capacity)")
        
        # Order book is already initialized
        print("[OK] Cython order book ready")
        
        print()
        print("System Ready!")
        print("=" * 60)
        print()
    
    def market_simulator_thread(self, orders_per_second=10000):
        """Simulate market order flow."""
        print(f"Market Simulator: Generating {orders_per_second:,} orders/second")
        
        interval = 1.0 / orders_per_second
        
        while self.running:
            # Generate order
            order_id = self.stats['orders_sent'] + 1
            side = random.choice([0, 1])  # 0 = BUY, 1 = SELL
            base_price = 100.0
            price = base_price + random.uniform(-2.0, 2.0)
            price = max(95.0, min(105.0, price))
            
            # Generate quantity (occasional whale orders)
            if random.random() < 0.02:  # 2% whale orders
                quantity = random.uniform(5000.0, 20000.0)
            else:
                quantity = random.uniform(10.0, 500.0)
            
            # Write to ring buffer
            success = self.ring_buffer.write_order(order_id, side, round(price, 2), round(quantity, 2))
            
            if success:
                with self.lock:
                    self.stats['orders_sent'] += 1
            
            # Control rate
            time.sleep(interval)
    
    def matching_engine_thread(self):
        """Process orders from ring buffer through matching engine."""
        print("Matching Engine: Processing orders from IPC bus")
        
        while self.running:
            # Read order from ring buffer
            order = self.ring_buffer.read_order()
            
            if order:
                order_id, side, price, quantity, timestamp_ns = order
                
                # Measure latency
                start_ns = time.perf_counter_ns()
                remaining_qty, trades = self.order_book.add_order(
                    order_id, side, price, quantity, timestamp_ns
                )
                end_ns = time.perf_counter_ns()
                
                latency_us = (end_ns - start_ns) / 1000.0
                
                # Update stats
                with self.lock:
                    self.stats['orders_processed'] += 1
                    self.stats['trades_matched'] += len(trades)
                    self.stats['latency_samples'].append(latency_us)
                    if len(self.stats['latency_samples']) > 1000:
                        self.stats['latency_samples'].pop(0)
            else:
                # No orders, brief sleep
                time.sleep(0.0001)
    
    def dashboard_thread(self):
        """Display real-time dashboard."""
        print("Dashboard: Starting real-time display")
        print()
        
        while self.running:
            # Clear screen
            print("\033[H\033[J", end="")
            
            # Get current stats
            with self.lock:
                stats = self.stats.copy()
                latency_samples = stats['latency_samples'].copy()
            
            # Calculate metrics
            avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0
            min_latency = min(latency_samples) if latency_samples else 0
            max_latency = max(latency_samples) if latency_samples else 0
            
            # Get order book state
            top_of_book = self.order_book.get_top_of_book(depth=5)
            buffer_stats = self.ring_buffer.get_stats()
            
            # Display
            print("=" * 70)
            print(" " * 18 + "CHRONOSMATCH - LIVE SYSTEM")
            print("=" * 70)
            print()
            
            print("PERFORMANCE METRICS:")
            print("-" * 70)
            print(f"  Orders Sent:       {stats['orders_sent']:,}")
            print(f"  Orders Processed:  {stats['orders_processed']:,}")
            print(f"  Trades Matched:    {stats['trades_matched']:,}")
            print(f"  Last Latency:      {latency_samples[-1]:.2f} us" if latency_samples else "  Last Latency:      0.00 us")
            print(f"  Avg Latency:       {avg_latency:.2f} us")
            print(f"  Min Latency:       {min_latency:.2f} us")
            print(f"  Max Latency:       {max_latency:.2f} us")
            print()
            
            print("RING BUFFER STATUS:")
            print("-" * 70)
            print(f"  Capacity:          {buffer_stats['capacity']:,}")
            print(f"  Orders in Buffer:  {buffer_stats['count']:,}")
            print(f"  Available:         {buffer_stats['available']:,}")
            print(f"  Utilization:       {(buffer_stats['count'] / buffer_stats['capacity'] * 100):.1f}%")
            print()
            
            print("ORDER BOOK:")
            print("-" * 70)
            print("  BIDS (Buy Orders):")
            for bid in top_of_book['bids'][:5]:
                whale = " [WHALE!]" if bid['quantity'] > 5000 else ""
                print(f"    {bid['price']:8.2f} | {bid['quantity']:10.2f}{whale}")
            
            print()
            print("  ASKS (Sell Orders):")
            for ask in top_of_book['asks'][:5]:
                whale = " [WHALE!]" if ask['quantity'] > 5000 else ""
                print(f"    {ask['price']:8.2f} | {ask['quantity']:10.2f}{whale}")
            
            print()
            
            # Spread
            if top_of_book['bids'] and top_of_book['asks']:
                spread = top_of_book['asks'][0]['price'] - top_of_book['bids'][0]['price']
                spread_pct = (spread / top_of_book['bids'][0]['price']) * 100
                print(f"  Spread: {spread:.2f} ({spread_pct:.3f}%)")
            
            # Whale detection
            whale_bids = [b for b in top_of_book['bids'] if b['quantity'] >= 5000]
            whale_asks = [a for a in top_of_book['asks'] if a['quantity'] >= 5000]
            if whale_bids or whale_asks:
                print()
                print("  " + "!" * 70)
                print("  WHALE DETECTED! Large orders clearing multiple levels")
                print("  " + "!" * 70)
            
            print()
            
            # Order book stats
            ob_stats = self.order_book.get_stats()
            print("ORDER BOOK STATISTICS:")
            print("-" * 70)
            print(f"  Total Orders:      {ob_stats['order_count']}")
            print(f"  Total Trades:      {ob_stats['trade_count']}")
            
            print()
            print("=" * 70)
            print("Press Ctrl+C to stop | Refresh: 500ms")
            print("=" * 70)
            
            # Sleep for refresh
            time.sleep(0.5)
    
    def run(self, duration=30):
        """Run the complete integrated system."""
        self.running = True
        
        print("Starting ChronosMatch Integrated System")
        print("=" * 60)
        print()
        
        # Start threads
        simulator_thread = threading.Thread(target=self.market_simulator_thread, args=(10000,))
        engine_thread = threading.Thread(target=self.matching_engine_thread)
        dashboard_thread = threading.Thread(target=self.dashboard_thread)
        
        simulator_thread.start()
        engine_thread.start()
        dashboard_thread.start()
        
        try:
            # Run for specified duration
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n\nStopping system...")
        finally:
            self.running = False
            simulator_thread.join()
            engine_thread.join()
            dashboard_thread.join()
            
            # Final stats
            print()
            print("=" * 60)
            print("FINAL STATISTICS")
            print("=" * 60)
            with self.lock:
                stats = self.stats.copy()
                latency_samples = stats['latency_samples'].copy()
            
            avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0
            
            print(f"Total Orders Sent:      {stats['orders_sent']:,}")
            print(f"Total Orders Processed: {stats['orders_processed']:,}")
            print(f"Total Trades Matched:   {stats['trades_matched']:,}")
            print(f"Average Latency:        {avg_latency:.2f} us")
            print()
            
            # Cleanup
            self.ring_buffer.close()
            import os
            os.remove("integrated_mmap.bin")
            print("System stopped and cleaned up.")


def main():
    """Main entry point."""
    system = IntegratedSystem()
    
    try:
        system.initialize()
        system.run(duration=30)  # Run for 30 seconds
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()