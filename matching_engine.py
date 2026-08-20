"""
Matching Engine - Main orchestration of the trading system
Integrates IPC, Cython order book, and persistence
"""
import time
import threading
import asyncio
from ring_buffer import RingBuffer
from order_book import OrderBook
from typing import Optional, Tuple, List
import sqlite3
from datetime import datetime
import queue


class MatchingEngine:
    """
    Main matching engine that reads orders from IPC,
    processes them through the Cython order book,
    and persists trades to SQLite.
    """
    
    def __init__(self, ipc_file: str = "chronos_mmap.bin", 
                 db_file: str = "chronos_trades.db"):
        self.ipc_file = ipc_file
        self.db_file = db_file
        self.ring_buffer: Optional[RingBuffer] = None
        self.order_book: Optional[OrderBook] = None
        self.running = False
        self.stats = {
            'orders_processed': 0,
            'trades_matched': 0,
            'latency_samples': [],
            'start_time': None
        }
        self.lock = threading.Lock()
        self.trade_queue = queue.Queue(maxsize=10000)
        self._init_database()
        self._start_persistence_thread()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for trade persistence."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                buy_order_id INTEGER NOT NULL,
                sell_order_id INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON trades(timestamp)
        ''')
        conn.commit()
        conn.close()
    
    def connect_ipc(self) -> None:
        """Connect to the shared memory ring buffer, creating it if needed."""
        self.ring_buffer = RingBuffer(filename=self.ipc_file)
        try:
            self.ring_buffer.connect()
        except FileNotFoundError:
            print("Creating new IPC ring buffer...")
            self.ring_buffer.create()
            self.ring_buffer.connect()
    
    def init_order_book(self) -> None:
        """Initialize the Cython order book."""
        self.order_book = OrderBook(max_matches=1000)
    
    def _start_persistence_thread(self) -> None:
        """Start a dedicated thread for persisting trades to database."""
        def _persistence_worker():
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            batch = []
            batch_size = 100
            
            while self.running or not self.trade_queue.empty():
                try:
                    # Get trade from queue with timeout
                    trade = self.trade_queue.get(timeout=0.1)
                    batch.append(trade)
                    
                    # Batch insert when batch is full
                    if len(batch) >= batch_size:
                        cursor.executemany('''
                            INSERT INTO trades (timestamp, price, quantity, buy_order_id, sell_order_id, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', batch)
                        conn.commit()
                        batch = []
                    
                    self.trade_queue.task_done()
                except queue.Empty:
                    # Flush any remaining trades
                    if batch:
                        cursor.executemany('''
                            INSERT INTO trades (timestamp, price, quantity, buy_order_id, sell_order_id, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', batch)
                        conn.commit()
                        batch = []
            
            # Final flush
            if batch:
                cursor.executemany('''
                    INSERT INTO trades (timestamp, price, quantity, buy_order_id, sell_order_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', batch)
                conn.commit()
            
            conn.close()
        
        self.persistence_thread = threading.Thread(target=_persistence_worker, daemon=True)
        self.persistence_thread.start()
    
    def persist_trade(self, price: float, quantity: float, 
                     buy_order_id: int, sell_order_id: int) -> None:
        """
        Queue a matched trade for persistence to SQLite database.
        Uses a single dedicated thread to avoid database locking.
        """
        try:
            self.trade_queue.put((time.time_ns(), price, quantity, buy_order_id, sell_order_id, 
                                datetime.now().isoformat()), block=False)
        except queue.Full:
            # Queue is full, skip this trade to avoid blocking
            pass
    
    def process_order(self, order_id: int, side: int, price: float, 
                     quantity: float, timestamp_ns: int) -> Tuple[float, List[dict], dict]:
        """
        Process a single order through the matching engine.
        Returns (remaining_quantity, list_of_trades, timing_info)
        timing_info includes nanosecond precision timestamps.
        """
        entry_time_ns = time.perf_counter_ns()
        
        remaining_qty, trades = self.order_book.add_order(
            order_id, side, price, quantity, timestamp_ns
        )
        
        exit_time_ns = time.perf_counter_ns()
        latency_ns = exit_time_ns - entry_time_ns
        latency_us = latency_ns / 1000.0  # Convert to microseconds
        
        timing_info = {
            'entry_time_ns': entry_time_ns,
            'exit_time_ns': exit_time_ns,
            'latency_ns': latency_ns,
            'latency_us': latency_us,
            'order_timestamp_ns': timestamp_ns
        }
        
        with self.lock:
            self.stats['orders_processed'] += 1
            self.stats['latency_samples'].append(latency_us)
            if len(self.stats['latency_samples']) > 10000:
                self.stats['latency_samples'].pop(0)
        
        # Persist trades
        for trade in trades:
            with self.lock:
                self.stats['trades_matched'] += 1
            
            # Determine buy/sell order IDs
            if side == 0:  # Incoming is BUY
                buy_order_id = order_id
                sell_order_id = trade['order_id']
            else:  # Incoming is SELL
                buy_order_id = trade['order_id']
                sell_order_id = order_id
            
            self.persist_trade(trade['price'], trade['quantity'], 
                             buy_order_id, sell_order_id)
        
        return (remaining_qty, trades, timing_info)
    
    def get_order_book_snapshot(self) -> Tuple[List[dict], List[dict]]:
        """Get current snapshot of the order book."""
        if self.order_book is None:
            return [], []
        
        top_of_book = self.order_book.get_top_of_book(depth=10)
        return top_of_book['bids'], top_of_book['asks']
    
    def get_stats(self) -> dict:
        """Get engine statistics."""
        with self.lock:
            latency_samples = self.stats['latency_samples'].copy()
        
        avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0
        max_latency = max(latency_samples) if latency_samples else 0
        min_latency = min(latency_samples) if latency_samples else 0
        
        return {
            'orders_processed': self.stats['orders_processed'],
            'trades_matched': self.stats['trades_matched'],
            'last_latency_us': latency_samples[-1] if latency_samples else 0,
            'avg_latency_us': avg_latency,
            'min_latency_us': min_latency,
            'max_latency_us': max_latency,
            'uptime_seconds': time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        }
    
    def run(self) -> None:
        """Main processing loop - reads from IPC and matches orders."""
        self.running = True
        self.stats['start_time'] = time.time()
        
        print("Starting Matching Engine...")
        print("Reading orders from IPC ring buffer...")
        
        last_stats_time = time.time()
        
        while self.running:
            # Read order from ring buffer
            order = self.ring_buffer.read_order()
            
            if order:
                order_id, side, price, quantity, timestamp_ns = order
                self.process_order(order_id, side, price, quantity, timestamp_ns)[0:2]
            else:
                # No orders available, sleep briefly
                time.sleep(0.0001)  # 100 microseconds
            
            # Report stats every second
            current_time = time.time()
            if current_time - last_stats_time >= 1.0:
                stats = self.get_stats()
                buffer_stats = self.ring_buffer.get_stats()
                print(f"\r[Matching Engine] Orders: {stats['orders_processed']:,} | "
                      f"Trades: {stats['trades_matched']:,} | "
                      f"Latency: {stats['last_latency_us']:.2f} us | "
                      f"Buffer: {buffer_stats['count']:,}/{buffer_stats['capacity']:,}", 
                      end='', flush=True)
                last_stats_time = current_time
    
    def stop(self) -> None:
        """Stop the matching engine."""
        self.running = False
    
    def close(self) -> None:
        """Clean up resources."""
        if self.ring_buffer:
            self.ring_buffer.close()


def main():
    """Main entry point for the matching engine."""
    engine = MatchingEngine()
    
    try:
        # Initialize IPC ring buffer (will create if needed)
        engine.connect_ipc()
        
        # Initialize order book
        engine.init_order_book()
        
        # Run the engine
        engine.run()
        
    except KeyboardInterrupt:
        print("\nStopping Matching Engine...")
        engine.stop()
        stats = engine.get_stats()
        print(f"\nFinal Statistics:")
        print(f"  Orders Processed: {stats['orders_processed']:,}")
        print(f"  Trades Matched: {stats['trades_matched']:,}")
        print(f"  Avg Latency: {stats['avg_latency_us']:.2f} μs")
        print(f"  Min Latency: {stats['min_latency_us']:.2f} μs")
        print(f"  Max Latency: {stats['max_latency_us']:.2f} μs")
        print(f"  Uptime: {stats['uptime_seconds']:.2f} seconds")
    finally:
        engine.close()


if __name__ == "__main__":
    main()
