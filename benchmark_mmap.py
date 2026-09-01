import time

from engine.ring_buffer import RingBuffer


def benchmark_mmap(number_of_orders, runs=5):
    results = []

    for _ in range(runs):
        buffer = RingBuffer(capacity=number_of_orders)

        start_time = time.perf_counter()

        for i in range(number_of_orders):
            buffer.write(i, "BUY", 100, 10)

        end_time = time.perf_counter()

        results.append(end_time - start_time)

    average = sum(results) / runs
    minimum = min(results)
    maximum = max(results)

    orders_per_second = number_of_orders / average

    print(f"\n--- Memory Mapping Benchmark: {number_of_orders} orders ---")
    print(f"Average time: {average:.6f} seconds")
    print(f"Minimum time: {minimum:.6f} seconds")
    print(f"Maximum time: {maximum:.6f} seconds")
    print(f"Orders per second: {orders_per_second:.2f}")


if __name__ == "__main__":
    benchmark_mmap(1000)
    benchmark_mmap(10000)