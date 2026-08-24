"""
Cython Limit Order Book - High-Performance Matching Engine
Week 2: Cython implementation with C-types and GIL bypass
"""
from libc.stdint cimport uint64_t, uint32_t, int64_t
from libc.stdlib cimport malloc, free
from libc.math cimport fabs
cimport cython

# C-struct for Order - uses only C types for zero Python object overhead
cdef struct Order:
    uint64_t order_id
    uint32_t side  # 0 = BUY, 1 = SELL
    double price
    double quantity
    uint64_t timestamp
    Order* next  # Linked list for same price level

# C-struct for Price Level
cdef struct PriceLevel:
    double price
    double total_quantity
    Order* head  # Head of order queue at this price
    Order* tail  # Tail of order queue at this price
    PriceLevel* next  # Next price level (lower for bids, higher for asks)
    PriceLevel* prev  # Previous price level

# Limit Order Book structure
cdef struct LimitOrderBook:
    PriceLevel* bids  # Best bid (highest price)
    PriceLevel* asks  # Best ask (lowest price)
    uint64_t order_count
    uint64_t trade_count


@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.cdivision(True)
cdef inline Order* create_order(uint64_t order_id, uint32_t side, double price, 
                                 double quantity, uint64_t timestamp) nogil:
    """Create a new order node - inline for maximum performance."""
    cdef Order* order = <Order*> malloc(sizeof(Order))
    if order != NULL:
        order.order_id = order_id
        order.side = side
        order.price = price
        order.quantity = quantity
        order.timestamp = timestamp
        order.next = NULL
    return order


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef inline void free_order(Order* order) nogil:
    """Free an order node - inline for performance."""
    if order != NULL:
        free(order)


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef inline PriceLevel* create_price_level(double price) nogil:
    """Create a new price level - inline for performance."""
    cdef PriceLevel* level = <PriceLevel*> malloc(sizeof(PriceLevel))
    if level != NULL:
        level.price = price
        level.total_quantity = 0.0
        level.head = NULL
        level.tail = NULL
        level.next = NULL
        level.prev = NULL
    return level


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef void free_price_level(PriceLevel* level) nogil:
    """Free a price level and all its orders."""
    cdef Order* order
    cdef Order* next_order
    
    if level != NULL:
        # Free all orders in this level
        order = level.head
        while order != NULL:
            next_order = order.next
            free_order(order)
            order = next_order
        free(level)


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef inline void add_order_to_price_level(PriceLevel* level, Order* order) nogil:
    """Add an order to a price level (FIFO queue) - inline for performance."""
    if level.head == NULL:
        level.head = order
        level.tail = order
    else:
        level.tail.next = order
        level.tail = order
    level.total_quantity += order.quantity


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef int add_bid(LimitOrderBook* lob, Order* order) nogil:
    """
    Add a bid order to the order book.
    Returns 1 on success, 0 on failure.
    """
    cdef PriceLevel* level
    cdef PriceLevel* new_level
    cdef PriceLevel* current
    
    # Find the correct price level or create it
    level = lob.bids
    current = NULL
    
    while level != NULL and level.price > order.price:
        current = level
        level = level.next
    
    if level != NULL and fabs(level.price - order.price) < 0.0001:
        # Price level exists, add order to it
        add_order_to_price_level(level, order)
    else:
        # Create new price level
        new_level = create_price_level(order.price)
        if new_level == NULL:
            return 0
        
        add_order_to_price_level(new_level, order)
        
        # Insert into linked list
        new_level.next = level
        new_level.prev = current
        
        if current != NULL:
            current.next = new_level
        else:
            lob.bids = new_level
        
        if level != NULL:
            level.prev = new_level
    
    lob.order_count += 1
    return 1


@cython.nonecheck(False)
@cython.boundscheck(False)
cdef int add_ask(LimitOrderBook* lob, Order* order) nogil:
    """
    Add an ask order to the order book.
    Returns 1 on success, 0 on failure.
    """
    cdef PriceLevel* level
    cdef PriceLevel* new_level
    cdef PriceLevel* current
    
    # Find the correct price level or create it
    level = lob.asks
    current = NULL
    
    while level != NULL and level.price < order.price:
        current = level
        level = level.next
    
    if level != NULL and fabs(level.price - order.price) < 0.0001:
        # Price level exists, add order to it
        add_order_to_price_level(level, order)
    else:
        # Create new price level
        new_level = create_price_level(order.price)
        if new_level == NULL:
            return 0
        
        add_order_to_price_level(new_level, order)
        
        # Insert into linked list
        new_level.next = level
        new_level.prev = current
        
        if current != NULL:
            current.next = new_level
        else:
            lob.asks = new_level
        
        if level != NULL:
            level.prev = new_level
    
    lob.order_count += 1
    return 1


@cython.nonecheck(False)
@cython.boundscheck(False)
@cython.cdivision(True)
cdef double match_order(LimitOrderBook* lob, Order* incoming_order, 
                        double* matched_prices, double* matched_quantities,
                        uint64_t* matched_order_ids, uint64_t max_matches) nogil:
    """
    Match an incoming order against the order book.
    Returns total matched quantity.
    Fills matched_prices, matched_quantities, matched_order_ids arrays.
    """
    cdef double total_matched = 0.0
    cdef double match_qty
    cdef uint64_t match_count = 0
    cdef PriceLevel* level
    cdef Order* order
    cdef Order* next_order
    cdef Order* prev_order
    cdef int is_buy = (incoming_order.side == 0)
    
    if is_buy:
        # Buy order matches against asks (lowest price first)
        level = lob.asks
        while level != NULL and match_count < max_matches and incoming_order.quantity > 0.0001:
            if level.price > incoming_order.price:
                break  # Ask price too high
            
            order = level.head
            while order != NULL and match_count < max_matches and incoming_order.quantity > 0.0001:
                next_order = order.next
                
                match_qty = min(incoming_order.quantity, order.quantity)
                
                if match_qty > 0.0001:
                    matched_prices[match_count] = level.price
                    matched_quantities[match_count] = match_qty
                    matched_order_ids[match_count] = order.order_id
                    match_count += 1
                    total_matched += match_qty
                    
                    incoming_order.quantity -= match_qty
                    order.quantity -= match_qty
                    level.total_quantity -= match_qty
                    lob.trade_count += 1
                
                if order.quantity < 0.0001:
                    # Order fully matched, remove it
                    if order == level.head:
                        level.head = order.next
                    if order == level.tail:
                        # Find the previous order in the queue
                        prev_order = level.head
                        if prev_order != NULL and prev_order != order:
                            while prev_order.next != order and prev_order.next != NULL:
                                prev_order = prev_order.next
                            if prev_order.next == order:
                                prev_order.next = NULL
                                level.tail = prev_order
                        else:
                            # Only one order in the level
                            level.head = NULL
                            level.tail = NULL
                    free_order(order)
                
                order = next_order
            
            # Remove empty price level
            if level.head == NULL:
                if level.prev != NULL:
                    level.prev.next = level.next
                else:
                    lob.asks = level.next
                if level.next != NULL:
                    level.next.prev = level.prev
                next_level = level.next
                free_price_level(level)
                level = next_level
            else:
                level = level.next
    else:
        # Sell order matches against bids (highest price first)
        level = lob.bids
        while level != NULL and match_count < max_matches and incoming_order.quantity > 0.0001:
            if level.price < incoming_order.price:
                break  # Bid price too low
            
            order = level.head
            while order != NULL and match_count < max_matches and incoming_order.quantity > 0.0001:
                next_order = order.next
                
                match_qty = min(incoming_order.quantity, order.quantity)
                
                if match_qty > 0.0001:
                    matched_prices[match_count] = level.price
                    matched_quantities[match_count] = match_qty
                    matched_order_ids[match_count] = order.order_id
                    match_count += 1
                    total_matched += match_qty
                    
                    incoming_order.quantity -= match_qty
                    order.quantity -= match_qty
                    level.total_quantity -= match_qty
                    lob.trade_count += 1
                
                if order.quantity < 0.0001:
                    # Order fully matched, remove it
                    if order == level.head:
                        level.head = order.next
                    if order == level.tail:
                        # Find the previous order in the queue
                        prev_order = level.head
                        if prev_order != NULL and prev_order != order:
                            while prev_order.next != order and prev_order.next != NULL:
                                prev_order = prev_order.next
                            if prev_order.next == order:
                                prev_order.next = NULL
                                level.tail = prev_order
                        else:
                            # Only one order in the level
                            level.head = NULL
                            level.tail = NULL
                    free_order(order)
                
                order = next_order
            
            # Remove empty price level
            if level.head == NULL:
                if level.prev != NULL:
                    level.prev.next = level.next
                else:
                    lob.bids = level.next
                if level.next != NULL:
                    level.next.prev = level.prev
                next_level = level.next
                free_price_level(level)
                level = next_level
            else:
                level = level.next
    
    return total_matched


# Python wrapper class
cdef class OrderBook:
    cdef LimitOrderBook* _lob
    cdef double[:] _matched_prices
    cdef double[:] _matched_quantities
    cdef uint64_t[:] _matched_order_ids
    cdef uint64_t _max_matches
    
    def __cinit__(self, max_matches=1000):
        """Initialize the order book."""
        self._lob = <LimitOrderBook*> malloc(sizeof(LimitOrderBook))
        if self._lob == NULL:
            raise MemoryError("Failed to allocate LimitOrderBook")
        
        self._lob.bids = NULL
        self._lob.asks = NULL
        self._lob.order_count = 0
        self._lob.trade_count = 0
        
        self._max_matches = max_matches
        # Pre-allocate arrays for match results
        import numpy as np
        self._matched_prices = np.zeros(max_matches, dtype=np.float64)
        self._matched_quantities = np.zeros(max_matches, dtype=np.float64)
        self._matched_order_ids = np.zeros(max_matches, dtype=np.uint64)
    
    def __dealloc__(self):
        """Clean up the order book."""
        if self._lob != NULL:
            # Free all price levels
            level = self._lob.bids
            while level != NULL:
                next_level = level.next
                free_price_level(level)
                level = next_level
            
            level = self._lob.asks
            while level != NULL:
                next_level = level.next
                free_price_level(level)
                level = next_level
            
            free(self._lob)
    
    @cython.nonecheck(False)
    @cython.boundscheck(False)
    def add_order(self, uint64_t order_id, uint32_t side, double price, 
                  double quantity, uint64_t timestamp):
        """
        Add an order to the book and attempt to match it.
        Returns (remaining_quantity, list_of_trades)
        """
        cdef Order* incoming_order = create_order(order_id, side, price, quantity, timestamp)
        if incoming_order == NULL:
            raise MemoryError("Failed to create order")
        
        # Try to match the order
        cdef double total_matched = match_order(
            self._lob, incoming_order,
            &self._matched_prices[0],
            &self._matched_quantities[0],
            &self._matched_order_ids[0],
            self._max_matches
        )
        
        # If order not fully matched, add to book
        cdef int added = 0
        if incoming_order.quantity > 0.0001:
            if side == 0:  # BUY
                added = add_bid(self._lob, incoming_order)
            else:  # SELL
                added = add_ask(self._lob, incoming_order)
        else:
            free_order(incoming_order)
        
        # Build trade list
        trades = []
        cdef uint64_t i
        cdef double safe_quantity = max(min(quantity, 1.0), 0.0001)  # Prevent division by zero
        for i in range(<uint64_t>(total_matched / safe_quantity + 1)):
            if i >= self._max_matches or self._matched_quantities[i] < 0.0001:
                break
            trades.append({
                'price': self._matched_prices[i],
                'quantity': self._matched_quantities[i],
                'order_id': self._matched_order_ids[i]
            })
        
        return (incoming_order.quantity, trades)
    
    @cython.nonecheck(False)
    @cython.boundscheck(False)
    def get_spread(self):
        """Get the current bid-ask spread."""
        cdef double best_bid = 0.0
        cdef double best_ask = 0.0
        
        if self._lob.bids != NULL:
            best_bid = self._lob.bids.price
        if self._lob.asks != NULL:
            best_ask = self._lob.asks.price
        
        return (best_bid, best_ask)
    
    @cython.nonecheck(False)
    @cython.boundscheck(False)
    def get_top_of_book(self, depth=5):
        """Get the top N levels of the order book."""
        cdef list bids = []
        cdef list asks = []
        cdef PriceLevel* level
        cdef int count = 0
        
        # Get bids
        level = self._lob.bids
        while level != NULL and count < depth:
            bids.append({
                'price': level.price,
                'quantity': level.total_quantity,
                'order_count': 0  # Would need to count orders
            })
            level = level.next
            count += 1
        
        # Get asks
        count = 0
        level = self._lob.asks
        while level != NULL and count < depth:
            asks.append({
                'price': level.price,
                'quantity': level.total_quantity,
                'order_count': 0
            })
            level = level.next
            count += 1
        
        return {'bids': bids, 'asks': asks}
    
    @cython.nonecheck(False)
    @cython.boundscheck(False)
    def get_stats(self):
        """Get order book statistics."""
        return {
            'order_count': self._lob.order_count,
            'trade_count': self._lob.trade_count
        }
