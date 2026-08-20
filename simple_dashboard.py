"""
Simple Dashboard - Non-curses version for monitoring
Works in any terminal environment without curses dependency
"""
import time
import threading
from ring_buffer import RingBuffer
from order_book import OrderBook
from typing import Optional


class SimpleDashboard:
    """
    Simple text-based dashboard for monitoring the matching engine.
    Updates the terminal display without using curses.
    """
    
    def __init__(self, refresh_rate: float = 1.0):
        self.refresh_rate = refresh_rate
        self.running = False
        self.ring_buffer: Optional[RingBuffer] = None
        self.order_book: Optional[OrderBook] = None
        self.stats = {
            'orders_processed': 0,
            'trades_matched': 0,
            'last_latency_us': 0.0,
            'avg_latency_us': 0.0,
            'latency_samples': []
        }
        self.lock = threading.Lock()
    
    def connect_ipc(self, filename: str = "chronos_mmap.bin") -> None:
        """Connect to the shared memory ring buffer."""
        self.ring_buffer = RingBuffer(filename=filename)
        self.ring_buffer.connect()
    
    def init_order_book(self) -> None:
        """Initialize the order book."""
        self.order_book = OrderBook(max_matches=1000)
    
    def update_stats(self, orders_processed: int, trades_matched: int, 
                     latency_us: float) -> None:
        """Update dashboard statistics."""
        with self.lock:
            self.stats['orders_processed'] = orders_processed
            self.stats['trades_matched'] = trades_matched
            self.stats['last_latency_us'] = latency_us
            self.stats['latency_samples'].append(latency_us)
            if len(self.stats['latency_samples']) > 1000:
                self.stats['latency_samples'].pop(0)
            self.stats['avg_latency_us'] = sum(self.stats['latency_samples']) / len(self.stats['latency_samples'])
    
    def display(self) -> None:
        """Display the current dashboard state."""
        # Clear screen (works on most terminals)
        print("\033[H\033[J", end="")
        
        print("=" * 70)
        print(" " * 15 + "CHRONOSMATCH - HFT ENGINE")
        print("=" * 70)
        print()
        
        # Performance metrics
        with self.lock:
            stats = self.stats.copy()
        
        print("PERFORMANCE METRICS:")
        print("-" * 70)
        print(f"  Orders Processed: {stats['orders_processed']:,}")
        print(f"  Trades Matched:   {stats['trades_matched']:,}")
        print(f"  Last Latency:     {stats['last_latency_us']:.2f} us")
        print(f"  Avg Latency:      {stats['avg_latency_us']:.2f} us")
        print()
        
        # Ring buffer status
        if self.ring_buffer:
            buffer_stats = self.ring_buffer.get_stats()
            print("RING BUFFER STATUS:")
            print("-" * 70)
            print(f"  Buffer Capacity:   {buffer_stats['capacity']:,}")
            print(f"  Orders in Buffer:  {buffer_stats['count']:,}")
            print(f"  Available Slots:   {buffer_stats['available']:,}")
            print(f"  Utilization:      {(buffer_stats['count'] / buffer_stats['capacity'] * 100):.1f}%")
            print()
        
        # Order book state
        if self.order_book:
            top_of_book = self.order_book.get_top_of_book(depth=5)
            
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
                spread_pct = (spread / top_of_book['bids'][0]['price']) * 100 if top_of_book['bids'][0]['price'] > 0 else 0
                print(f"  Spread: {spread:.2f} ({spread_pct:.3f}%)")
            
            print()
            
            # Whale detection
            whale_bids = [b for b in top_of_book['bids'] if b['quantity'] >= 5000]
            whale_asks = [a for a in top_of_book['asks'] if a['quantity'] >= 5000]
            if whale_bids or whale_asks:
                print("  " + "!" * 70)
                print("  WHALE DETECTED! Large orders clearing multiple levels")
                print("  " + "!" * 70)
        
        print()
        
        # Order book statistics
        if self.order_book:
            ob_stats = self.order_book.get_stats()
            print("ORDER BOOK STATISTICS:")
            print("-" * 70)
            print(f"  Total Orders: {ob_stats['order_count']}")
            print(f"  Total Trades: {ob_stats['trade_count']}")
        
        print()
        print("=" * 70)
        print("Press Ctrl+C to stop | Auto-refresh: {:.0f}ms".format(self.refresh_rate * 1000))
        print("=" * 70)
    
    def run(self) -> None:
        """Run the dashboard main loop."""
        self.running = True
        
        try:
            while self.running:
                self.display()
                time.sleep(self.refresh_rate)
        except KeyboardInterrupt:
            print("\n\nStopping Dashboard...")
            self.running = False
    
    def stop(self) -> None:
        """Stop the dashboard."""
        self.running = False


def main():
    """Main entry point for the simple dashboard."""
    dashboard = SimpleDashboard(refresh_rate=1.0)
    
    try:
        # Connect to IPC
        dashboard.connect_ipc()
        dashboard.init_order_book()
        
        print("Starting Simple Dashboard...")
        print("Press Ctrl+C to stop")
        print()
        
        # Run the dashboard
        dashboard.run()
        
    except FileNotFoundError:
        print("Error: IPC ring buffer not found.")
        print("Please run the matching engine first to create the ring buffer.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if dashboard.ring_buffer:
            dashboard.ring_buffer.close()


if __name__ == "__main__":
    main()