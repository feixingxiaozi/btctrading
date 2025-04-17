
from BitgetAPI import BitgetAPI
import time
from datetime import datetime

def find_ab_timestamps(klines, price_A, price_B, tolerance=0.1):
    timestamp_B = 0
    timestamp_A = 0

    for i, kline in enumerate(klines):
        high, low = float(kline["high"]), float(kline["low"])
        ts = int(kline["timestamp"])

        if timestamp_B == 0 and (low - tolerance <= price_B <= high + tolerance):
            timestamp_B = ts
            # 找到B后，向前找A
            for j in range(i + 1, len(klines)):
                high_a, low_a = float(klines[j]["high"]), float(klines[j]["low"])
                ts_a = int(klines[j]["timestamp"])
                if low_a - tolerance <= price_A <= high_a + tolerance:
                    timestamp_A = ts_a
                    break
            break

    return timestamp_A, timestamp_B

def calculate_retrace_levels(price_A, price_B, direction):
    diff = abs(price_B - price_A)
    offset = 5
    if direction == 1:
        retrace_0_5 = price_B - diff * 0.5 + offset
        retrace_0_618 = price_B - diff * 0.618 + offset
    else:
        retrace_0_5 = price_B + diff * 0.5 - offset
        retrace_0_618 = price_B + diff * 0.618 - offset
    return retrace_0_5, retrace_0_618

def calculate_stop_loss(price_B, direction):
    return price_B - 2 if direction == 1 else price_B + 2

def calculate_position_size(entry_price, stop_loss_price, capital):
    risk_amount = capital * 0.025
    risk_per_unit = abs(entry_price - stop_loss_price) / entry_price
    return round(risk_amount / risk_per_unit, 3) if risk_per_unit else 0

def find_ab_timestamps(klines, price_A, price_B, tolerance=0.1):
    timestamp_B = 0
    timestamp_A = 0

    for i, kline in enumerate(klines):
        high, low = float(kline["high"]), float(kline["low"])
        ts = int(kline["timestamp"])

        if timestamp_B == 0 and (low - tolerance <= price_B <= high + tolerance):
            timestamp_B = ts
            # 找到B后，向后找A
            for j in range(i + 1, len(klines)):
                high_a, low_a = float(klines[j]["high"]), float(klines[j]["low"])
                ts_a = int(klines[j]["timestamp"])
                if low_a - tolerance <= price_A <= high_a + tolerance:
                    timestamp_A = ts_a
                    break
            break

    return timestamp_A, timestamp_B

def place_strategy_orders(api, a, b, capital):
    from datetime import datetime

    klines = api.get_contract_kline_v2()
    latest_price = klines[-1]["close"] if klines else 0

    direction = "short" if b < a else "long"
    ab_range = abs(a - b)
    buffer = 30

    # 计算两个挂单点位（entry 和止损）
    if direction == "short":
        entry_50 = round(b + ab_range * 0.5 - 5, 1)
        entry_618 = round(b + ab_range * 0.618 - 5, 1)
        stop_50 = stop_618 = round(a + 2, 1)
        pos_side = "short"
        side = "open_short"
    else:
        entry_50 = round(b + ab_range * 0.5 + 5, 1)
        entry_618 = round(b + ab_range * 0.618 + 5, 1)
        stop_50 = stop_618 = round(a - 2, 1)
        pos_side = "long"
        side = "open_long"


    # 每张单子用本金一半，计算仓位
    risk_each = (capital * 0.025) / 2
    qty_50 = round(risk_each / abs(entry_50 - stop_50), 3)
    qty_618 = round(risk_each / abs(entry_618 - stop_618), 3)

    # 发两个订单
    result_50 = api.place_limit_order(
        side=side,
        qty=qty_50,
        price=entry_50,
        stop_loss=stop_50,
        take_profit=None,
        pos_side=pos_side
    )

    result_618 = api.place_limit_order(
        side=side,
        qty=qty_618,
        price=entry_618,
        stop_loss=stop_618,
        take_profit=None,
        pos_side=pos_side
    )

    return {
        "timestamp_A": datetime.fromtimestamp(a // 1000).strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_B": datetime.fromtimestamp(b // 1000).strftime("%Y-%m-%d %H:%M:%S"),
        "ts_A_raw": a,
        "ts_B_raw": b,
        "direction": direction,
        "entry_prices": [entry_50, entry_618],
        "qtys": [qty_50, qty_618],
        "stop_loss": [stop_50, stop_618],
        "current_price": latest_price,
        "order_result": [result_50, result_618]
    }

