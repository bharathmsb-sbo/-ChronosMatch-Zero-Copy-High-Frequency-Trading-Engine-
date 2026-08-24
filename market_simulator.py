"""
Market Simulator - High-throughput order generator
Week 1: Market Firehose generating 100K orders/second
"""
import asyncio
import random
import time
from ring_buffer import RingBuffer
from typing import Optional


class MarketSimulator:
    """
    Simulates a high-frequency trading market firehose.
    Generates buy/sell orders at configurable rates (default: 100K/sec).
    """
    
    def __init__(self, orders_per_second: int = 100000, 
                 price_range: tuple = (90.0, 110.0),
                 qty_range: tuple = (1.0, 1000.0)):
        self.orders_per_second = orders_per_second
        self.price_range = price_range
        self.qty_range = qty_range
        self.ring_buffer: Optional[RingBuffer] = None
        self.order_id_counter = 0
        self.running = False
        self.stats = {
            'orders_sent': 0,
            'orders_dropped': 0,
            'start_time': None,
            'last_update': None
        }
    
    def connect_ipc(self, filename: str = "chronos_mmap.bin") -> None:
        """Connect to the shared memory ring buffer, creating it if needed."""
        self.ring_buffer = RingBuffer(filename=filename)
        try:
            self.ring_buffer.connect()
        except FileNotFoundError:
            print("Creating new IPC ring buffer...")
            self.ring_buffer.create()
            self.ring_buffer.connect()
    
    def generate_order(self) -> tuple[int, int, float, float]:
        """
        Generate a random market order.
        Returns (order_id, side, price, quantity)
        Side: 0 = BUY, 1 = SELL
        """
        self.order_id_counter += 1
        side = random.choice([0, 1])  # 0 = BUY, 1 = SELL
        
        # Generate price with some randomness around a center
        base_price = (self.price_range[0] + self.price_range[1]) / 2
        price = base_price + random.uniform(-5.0, 5.0)
        price = max(self.price_range[0], min(self.price_range[1], price))
        
        # Generate quantity (occasionally generate whale orders)
        if random.random() < 0.01:  # 1% chance of whale order
            quantity = random.uniform(5000.0, 50000.0)
        else:
            quantity = random.uniform(*self.qty_range)
        
        return (self.order_id_counter, side, round(price, 2), round(quantity, 2))
    
    async def send_order(self, order: tuple) -> bool:
        """Send an order to the ring buffer."""
        order_id, side, price, quantity = order
        success = self.ring_buffer.write_order(order_id, side, price, quantity)
        
        if success:
            self.stats['orders_sent'] += 1
        else:
            self.stats['orders_dropped'] += 1
        
        return success
    
    async def order_generator(self) -> None:
        """Generate and send orders at the target rate."""
        interval = 1.0 / self.orders_per_second
        
        while self.running:
            order = self.generate_order()
            await self.send_order(order)
            
            # Control the rate
            await asyncio.sleep(interval)
    
    async def stats_reporter(self) -> None:
        """Periodically report statistics."""
        while self.running:
            await asyncio.sleep(1.0)  # Report every second
            
            if self.stats['start_time']:
                elapsed = time.time() - self.stats['start_time']
                rate = self.stats['orders_sent'] / elapsed if elapsed > 0 else 0
                
                buffer_stats = self.ring_buffer.get_stats()
                
                print(f"\r[Market Simulator] Orders: {self.stats['orders_sent']:,} | "
                      f"Dropped: {self.stats['orders_dropped']:,} | "
                      f"Rate: {rate:,.0f}/s | "
                      f"Buffer: {buffer_stats['count']:,}/{buffer_stats['capacity']:,}", end='', flush=True)
    
    async def run(self, duration: Optional[float] = None) -> None:
        """
        Run the market simulator.
        If duration is None, runs indefinitely.
        """
        self.running = True
        self.stats['start_time'] = time.time()
        
        print(f"Starting Market Simulator at {self.orders_per_second:,} orders/second...")
        print("Press Ctrl+C to stop")
        
        # Start generator and stats reporter
        generator_task = asyncio.create_task(self.order_generator())
        reporter_task = asyncio.create_task(self.stats_reporter())
        
        try:
            if duration:
                await asyncio.sleep(duration)
                self.running = False
            else:
                # Run indefinitely
                await generator_task
        except KeyboardInterrupt:
            print("\n\nStopping Market Simulator...")
            self.running = False
        finally:
            await generator_task
            await reporter_task
            
            # Final stats
            elapsed = time.time() - self.stats['start_time']
            rate = self.stats['orders_sent'] / elapsed if elapsed > 0 else 0
            print(f"\nFinal Statistics:")
            print(f"  Orders Sent: {self.stats['orders_sent']:,}")
            print(f"  Orders Dropped: {self.stats['orders_dropped']:,}")
            print(f"  Average Rate: {rate:,.0f} orders/second")
            print(f"  Duration: {elapsed:.2f} seconds")
    
    def close(self) -> None:
        """Clean up resources."""
        if self.ring_buffer:
            self.ring_buffer.close()


async def main():
    """Main entry point for the market simulator."""
    simulator = MarketSimulator(orders_per_second=100000)
    
    try:
        simulator.connect_ipc()
        await simulator.run()
    finally:
        simulator.close()


if __name__ == "__main__":
    asyncio.run(main())
