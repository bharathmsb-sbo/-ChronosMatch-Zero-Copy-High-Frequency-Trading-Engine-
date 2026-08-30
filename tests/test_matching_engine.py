import pytest
from engine.matching_engine import MatchingEngine


def test_add_buy_order():
    engine = MatchingEngine()

    order = {
        "order_id": 1,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    }

    engine.add_order(order)

    assert len(engine.buy_orders) == 1
    assert engine.buy_orders[0]["price"] == 100


def test_add_sell_order():
    engine = MatchingEngine()

    order = {
        "order_id": 2,
        "side": "SELL",
        "price": 101,
        "quantity": 5
    }

    engine.add_order(order)

    assert len(engine.sell_orders) == 1
    assert engine.sell_orders[0]["price"] == 101


def test_buy_price_priority():
    engine = MatchingEngine()

    order1 = {
        "order_id": 1,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    }

    order2 = {
        "order_id": 2,
        "side": "BUY",
        "price": 105,
        "quantity": 5
    }

    engine.add_order(order1)
    engine.add_order(order2)

    engine.match_orders()

    assert engine.buy_orders[0]["price"] == 105
    assert engine.buy_orders[1]["price"] == 100


def test_buy_sell_matching():
    engine = MatchingEngine()

    buy_order = {
        "order_id": 1,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    }

    sell_order = {
        "order_id": 2,
        "side": "SELL",
        "price": 100,
        "quantity": 5
    }

    engine.add_order(buy_order)
    engine.add_order(sell_order)

    trades = engine.match_orders()

    assert len(trades) == 1
    assert trades[0]["buy_order"] == 1
    assert trades[0]["sell_order"] == 2
    assert trades[0]["price"] == 100
    assert trades[0]["quantity"] == 5


def test_invalid_order_side():
    engine = MatchingEngine()

    order = {
        "order_id": 3,
        "side": "INVALID",
        "price": 100,
        "quantity": 10
    }

    with pytest.raises(ValueError):
        engine.add_order(order)


def test_invalid_price():
    engine = MatchingEngine()

    order = {
        "order_id": 4,
        "side": "BUY",
        "price": 0,
        "quantity": 10
    }

    with pytest.raises(ValueError):
        engine.add_order(order)


def test_invalid_quantity():
    engine = MatchingEngine()

    order = {
        "order_id": 5,
        "side": "BUY",
        "price": 100,
        "quantity": 0
    }

    with pytest.raises(ValueError):
        engine.add_order(order)


def test_cancel_order():
    engine = MatchingEngine()

    order = {
        "order_id": 6,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    }

    engine.add_order(order)

    result = engine.cancel_order(6)

    assert result is True
    assert len(engine.buy_orders) == 0


def test_price_time_priority():
    engine = MatchingEngine()

    order1 = {
        "order_id": 7,
        "side": "BUY",
        "price": 100,
        "quantity": 5
    }

    order2 = {
        "order_id": 8,
        "side": "BUY",
        "price": 100,
        "quantity": 5
    }

    sell_order = {
        "order_id": 9,
        "side": "SELL",
        "price": 100,
        "quantity": 5
    }

    engine.add_order(order1)
    engine.add_order(order2)
    engine.add_order(sell_order)

    trades = engine.match_orders()

    assert trades[0]["buy_order"] == 7
    assert trades[0]["sell_order"] == 9
    assert trades[0]["quantity"] == 5


def test_modify_order():
    engine = MatchingEngine()

    order = {
        "order_id": 10,
        "side": "BUY",
        "price": 100,
        "quantity": 10
    }

    engine.add_order(order)

    result = engine.modify_order(
        10,
        price=105,
        quantity=20
    )

    assert result is True
    assert engine.buy_orders[0]["price"] == 105
    assert engine.buy_orders[0]["quantity"] == 20
