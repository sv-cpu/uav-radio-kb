"""Формулы первой части; единицы указаны в именах и документации."""
import math


def _number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected finite real number')
    if value < 0 or (positive and value == 0):
        raise ValueError('Value outside domain')
    return value


def resistive_power_w(voltage_rms_v, resistance_ohm):
    """Средняя мощность только на постоянной чисто активной нагрузке."""
    v = _number(voltage_rms_v)
    r = _number(resistance_ohm, positive=True)
    try:
        result = v * (v / r)
    except OverflowError as exc:
        raise ValueError('Result outside float range') from exc
    if not math.isfinite(result) or (v > 0 and result == 0):
        raise ValueError('Result outside float range')
    return result


def power_level_db(power, reference):
    """Мощности должны иметь одинаковые единицы; результат в dB."""
    p = _number(power, positive=True)
    p0 = _number(reference, positive=True)
    return 10 * (math.log10(p) - math.log10(p0))


def bit_rate_bps(symbol_rate_per_s, bits_per_symbol):
    """Фиксированное отображение бит в символы, без служебных символов."""
    rate = _number(symbol_rate_per_s)
    if isinstance(bits_per_symbol, bool) or not isinstance(bits_per_symbol, int) or bits_per_symbol <= 0:
        raise ValueError('bits_per_symbol must be a positive integer')
    result = rate * bits_per_symbol
    if not math.isfinite(result):
        raise ValueError('Result outside float range')
    return result
