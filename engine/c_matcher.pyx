from .c_order cimport COrder


cdef inline int can_match(
    COrder buy,
    COrder sell
) noexcept nogil:
    return buy.price >= sell.price


cdef inline int get_trade_quantity(
    COrder buy,
    COrder sell
) noexcept nogil:
    if buy.quantity < sell.quantity:
        return buy.quantity

    return sell.quantity


cdef int match_two_orders(
    COrder buy,
    COrder sell
) noexcept nogil:

    if buy.quantity <= 0 or sell.quantity <= 0:
        return 0

    if not can_match(buy, sell):
        return 0

    return get_trade_quantity(buy, sell)