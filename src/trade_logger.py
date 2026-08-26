# Simple Real-Time Trade Event Logger
from datetime import datetime

def log_trade_event(event_type, details):
    """
    Formats and prints trading engine events with exact timestamps.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_log = f"[{timestamp}] [{event_type.upper()}] {details}"
    print(formatted_log)
    return formatted_log

# Demo Test Run
if __name__ == "__main__":
    print("ChronosMatch Engine Event Logger")
    
    # Test logging different engine operations
    log_trade_event("SYSTEM", "Engine initialized successfully with Ring Buffer capacity 1024.")
    log_trade_event("ORDER_NEW", "Buy Limit Order received: ID=101, Price=102, Qty=15")
    log_trade_event("TRADE_EXEC", "Matched Order 101 with 201: Executed 15 units @ $102")
    log_trade_event("ORDER_CANCEL", "Order 102 cancelled by user.")