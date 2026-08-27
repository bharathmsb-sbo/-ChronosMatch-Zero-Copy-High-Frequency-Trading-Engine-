# Simple Market Analytics Module

def calculate_market_metrics(trades_list):
    """
    Calculates basic trade statistics from a list of trades:
    - Total Trades
    - Total Volume
    - Average Trade Price (VWAP)
    """
    if len(trades_list) == 0:
        return "No trades available."

    total_volume = 0
    total_money = 0

    for trade in trades_list:
        price = trade["price"]
        qty = trade["qty"]

        total_volume = total_volume + qty
        total_money = total_money + (price * qty)

    total_trades = len(trades_list)
    average_price = round(total_money / total_volume, 2)

    return {
        "Total Trades": total_trades,
        "Total Volume": total_volume,
        "Average Price": average_price
    }

# Demo Run
if __name__ == "__main__":
    print("=== Simple Market Analytics ===")

    # Sample list of completed trades
    sample_trades = [
        {"id": 1, "price": 100, "qty": 10},
        {"id": 2, "price": 105, "qty": 20},
        {"id": 3, "price": 95, "qty": 10}
    ]

    print("Sample Trades:", sample_trades)
    
    result = calculate_market_metrics(sample_trades)
    print("\nCalculated Metrics:")
    for key, value in result.items():
        print(f"{key}: {value}")