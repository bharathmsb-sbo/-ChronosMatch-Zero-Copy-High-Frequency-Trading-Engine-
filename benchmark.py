import time

from engine.matching_engine import MatchingEngine


def benchmark_order_addition(number_of_orders, runs=5):
    results = []

    for _ in range(runs):
        engine = MatchingEngine()

        start_time = time.perf_counter()

        for i in range(number_of_orders):
            order = {
                "order_id": i,
                "side": "BUY",
                "price": 100 + (i % 10),
                "quantity": 10
            }

            engine.add_order(order)

        end_time = time.perf_counter()

        results.append(end_time - start_time)

    average = sum(results) / runs
    minimum = min(results)
    maximum = max(results)
    orders_per_second = number_of_orders / average

    print(f"\n--- Order Addition: {number_of_orders} orders ---")
    print(f"Average time: {average:.6f} seconds")
    print(f"Minimum time: {minimum:.6f} seconds")
    print(f"Maximum time: {maximum:.6f} seconds")
    print(f"Average per order: {(average / number_of_orders) * 1_000_000:.2f} microseconds")
    print(f"Orders per second: {orders_per_second:.2f}")


def benchmark_order_matching(number_of_orders, runs=5):
    results = []

    for _ in range(runs):
        engine = MatchingEngine()

        for i in range(number_of_orders):
            buy_order = {
                "order_id": i,
                "side": "BUY",
                "price": 100,
                "quantity": 10
            }

            sell_order = {
                "order_id": number_of_orders + i,
                "side": "SELL",
                "price": 100,
                "quantity": 10
            }

            engine.add_order(buy_order)
            engine.add_order(sell_order)

        start_time = time.perf_counter()

        engine.match_orders()

        end_time = time.perf_counter()

        results.append(end_time - start_time)

    average = sum(results) / runs
    minimum = min(results)
    maximum = max(results)

    total_orders = number_of_orders * 2
    orders_per_second = total_orders / average

    print(f"\n--- Order Matching: {number_of_orders} BUY + {number_of_orders} SELL ---")
    print(f"Average time: {average:.6f} seconds")
    print(f"Minimum time: {minimum:.6f} seconds")
    print(f"Maximum time: {maximum:.6f} seconds")
    print(f"Orders per second: {orders_per_second:.2f}")


if __name__ == "__main__":

    # Order Addition Benchmark
    benchmark_order_addition(100)
    benchmark_order_addition(1000)
    benchmark_order_addition(10000)

    # Order Matching Benchmark
    benchmark_order_matching(100)
    benchmark_order_matching(1000)