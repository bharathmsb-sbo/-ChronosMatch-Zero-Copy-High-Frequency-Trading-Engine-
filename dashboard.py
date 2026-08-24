"""
Terminal Dashboard - Real-time Order Book Display
Week 2: Curses-based UI for monitoring the matching engine
"""
import curses
import time
import threading
from ring_buffer import RingBuffer
from typing import Optional


class Dashboard:
    """
    Curses-based terminal dashboard for real-time order book visualization.
    Displays bid/ask spread, top of book, and latency metrics.
    """
    
    def __init__(self, refresh_rate: float = 0.05):
        self.refresh_rate = refresh_rate
        self.running = False
        self.ring_buffer: Optional[RingBuffer] = None
        self.stats = {
            'orders_processed': 0,
            'trades_matched': 0,
            'last_latency_us': 0.0,
            'avg_latency_us': 0.0,
            'latency_samples': []
        }
        self.lock = threading.Lock()
    
    def connect_ipc(self, filename: str = "chronos_mmap.bin") -> None:
        """Connect to the shared memory ring buffer, creating it if needed."""
        self.ring_buffer = RingBuffer(filename=filename)
        try:
            self.ring_buffer.connect()
        except FileNotFoundError:
            print("Creating new IPC ring buffer...")
            self.ring_buffer.create()
            self.ring_buffer.connect()
    
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
    
    def draw_header(self, stdscr, y: int) -> int:
        """Draw the dashboard header."""
        header = " CHRONOSMATCH - High-Frequency Trading Engine "
        stdscr.addstr(y, 0, "=" * (curses.COLS - 1))
        stdscr.addstr(y + 1, (curses.COLS - len(header)) // 2, header, curses.A_BOLD)
        stdscr.addstr(y + 2, 0, "=" * (curses.COLS - 1))
        return y + 3
    
    def draw_stats(self, stdscr, y: int) -> int:
        """Draw performance statistics."""
        with self.lock:
            stats = [
                f"Orders Processed: {self.stats['orders_processed']:,}",
                f"Trades Matched: {self.stats['trades_matched']:,}",
                f"Last Latency: {self.stats['last_latency_us']:.2f} μs",
                f"Avg Latency: {self.stats['avg_latency_us']:.2f} μs",
            ]
        
        stdscr.addstr(y, 0, "─" * (curses.COLS - 1))
        stdscr.addstr(y + 1, 2, "PERFORMANCE METRICS", curses.A_BOLD)
        stdscr.addstr(y + 2, 0, "─" * (curses.COLS - 1))
        
        for i, stat in enumerate(stats):
            stdscr.addstr(y + 3 + i, 4, stat)
        
        return y + 3 + len(stats)
    
    def draw_order_book(self, stdscr, y: int, bids: list, asks: list) -> int:
        """Draw the order book (bids and asks) with whale order highlighting."""
        stdscr.addstr(y, 0, "─" * (curses.COLS - 1))
        stdscr.addstr(y + 1, 2, "ORDER BOOK", curses.A_BOLD)
        stdscr.addstr(y + 2, 0, "─" * (curses.COLS - 1))
        
        # Header
        stdscr.addstr(y + 3, 2, "BIDS", curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(y + 3, curses.COLS // 2, "ASKS", curses.A_BOLD | curses.A_UNDERLINE)
        
        # Whale order threshold (orders > 5000 units)
        WHALE_THRESHOLD = 5000.0
        
        # Display bids (right-aligned, descending price)
        for i in range(min(10, len(bids))):
            bid = bids[i]
            line = f"{bid['price']:8.2f} | {bid['quantity']:10.2f}"
            pos = curses.COLS // 2 - len(line) - 2
            
            # Highlight whale orders in red/bold
            if bid['quantity'] >= WHALE_THRESHOLD:
                stdscr.addstr(y + 4 + i, pos, line, curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.addstr(y + 4 + i, pos, line)
        
        # Display asks (left-aligned, ascending price)
        for i in range(min(10, len(asks))):
            ask = asks[i]
            line = f"{ask['price']:8.2f} | {ask['quantity']:10.2f}"
            pos = curses.COLS // 2 + 2
            
            # Highlight whale orders in red/bold
            if ask['quantity'] >= WHALE_THRESHOLD:
                stdscr.addstr(y + 4 + i, pos, line, curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.addstr(y + 4 + i, pos, line)
        
        # Spread
        if bids and asks:
            spread = asks[0]['price'] - bids[0]['price']
            spread_pct = (spread / bids[0]['price']) * 100 if bids[0]['price'] > 0 else 0
            spread_line = f"Spread: {spread:.2f} ({spread_pct:.3f}%)"
            stdscr.addstr(y + 14, (curses.COLS - len(spread_line)) // 2, 
                         spread_line, curses.A_BOLD)
        
        # Whale alert
        whale_bids = [b for b in bids if b['quantity'] >= WHALE_THRESHOLD]
        whale_asks = [a for a in asks if a['quantity'] >= WHALE_THRESHOLD]
        if whale_bids or whale_asks:
            alert = "🐳 WHALE DETECTED! Large orders clearing multiple levels"
            stdscr.addstr(y + 15, (curses.COLS - len(alert)) // 2, 
                         alert, curses.A_BOLD | curses.A_BLINK)
            return y + 16
        
        return y + 15
    
    def draw_buffer_stats(self, stdscr, y: int) -> int:
        """Draw ring buffer statistics."""
        if self.ring_buffer:
            buffer_stats = self.ring_buffer.get_stats()
            buffer_lines = [
                f"Buffer Capacity: {buffer_stats['capacity']:,}",
                f"Orders in Buffer: {buffer_stats['count']:,}",
                f"Available Slots: {buffer_stats['available']:,}",
                f"Utilization: {(buffer_stats['count'] / buffer_stats['capacity'] * 100):.1f}%"
            ]
        else:
            buffer_lines = ["Buffer: Not connected"]
        
        stdscr.addstr(y, 0, "─" * (curses.COLS - 1))
        stdscr.addstr(y + 1, 2, "RING BUFFER STATUS", curses.A_BOLD)
        stdscr.addstr(y + 2, 0, "─" * (curses.COLS - 1))
        
        for i, line in enumerate(buffer_lines):
            stdscr.addstr(y + 3 + i, 4, line)
        
        return y + 3 + len(buffer_lines)
    
    def draw_footer(self, stdscr, y: int) -> int:
        """Draw the dashboard footer."""
        stdscr.addstr(y, 0, "─" * (curses.COLS - 1))
        stdscr.addstr(y + 1, 2, "Press 'q' to quit | Auto-refresh: {:.0f}ms".format(
            self.refresh_rate * 1000))
        stdscr.addstr(y + 2, 0, "=" * (curses.COLS - 1))
        return y + 3
    
    def run(self, order_book_callback):
        """
        Run the dashboard main loop.
        order_book_callback: function that returns (bids, asks)
        """
        def main_loop(stdscr):
            # Setup curses
            curses.curs_set(0)
            stdscr.nodelay(1)
            stdscr.timeout(int(self.refresh_rate * 1000))
            
            self.running = True
            
            while self.running:
                stdscr.clear()
                
                try:
                    # Get order book data
                    bids, asks = order_book_callback()
                    
                    # Draw all sections
                    y = 0
                    y = self.draw_header(stdscr, y)
                    y = self.draw_stats(stdscr, y)
                    y = self.draw_order_book(stdscr, y, bids, asks)
                    y = self.draw_buffer_stats(stdscr, y)
                    y = self.draw_footer(stdscr, y)
                    
                    # Handle input
                    key = stdscr.getch()
                    if key == ord('q') or key == ord('Q'):
                        self.running = False
                    
                except Exception as e:
                    stdscr.addstr(0, 0, f"Error: {str(e)}")
                    stdscr.refresh()
                    time.sleep(1)
                
                stdscr.refresh()
        
        curses.wrapper(main_loop)
    
    def stop(self) -> None:
        """Stop the dashboard."""
        self.running = False


if __name__ == "__main__":
    # Test the dashboard with mock data
    def mock_order_book():
        import random
        bids = [{'price': 100.0 - i * 0.01, 'quantity': random.uniform(100, 1000)} 
                for i in range(10)]
        asks = [{'price': 100.0 + i * 0.01, 'quantity': random.uniform(100, 1000)} 
                for i in range(10)]
        return bids, asks
    
    dashboard = Dashboard()
    dashboard.connect_ipc()
    dashboard.run(mock_order_book)
