"""Длина волны плоской электромагнитной волны в вакууме."""
import math

C_M_PER_S = 299_792_458  # точное значение SI, BIPM SI Brochure, раздел 2.2.1


def wavelength_m(frequency_hz: float) -> float:
    """Вернуть длину волны в метрах; частота задаётся в герцах."""
    if isinstance(frequency_hz, bool) or not isinstance(frequency_hz, (int, float)):
        raise ValueError("frequency_hz must be a positive finite number")
    if not math.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("frequency_hz must be a positive finite number")
    result = C_M_PER_S / frequency_hz
    if not math.isfinite(result) or result == 0:
        raise ValueError("result is outside floating-point range")
    return result
