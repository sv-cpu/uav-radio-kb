"""Плотность потока в свободном пространстве, ITU-R P.525-5 (3)."""
import math


def free_space_flux_w_m2(eirp_w: float, distance_m: float) -> float:
    """s=p/(4*pi*d²), только вне ближнего поля при условиях свободного пространства.

    EIRP задаётся в направлении точки наблюдения, расстояние — в метрах.
    Функция проверяет числа, но не физическую применимость дальнего поля.
    """
    for value in (eirp_w, distance_m):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError('Inputs must be finite real numbers')
        if not math.isfinite(value):
            raise ValueError('Inputs must be finite real numbers')
    if eirp_w < 0 or distance_m <= 0:
        raise ValueError('EIRP must be nonnegative; distance must be positive')
    result = eirp_w / distance_m / distance_m / (4 * math.pi)
    if not math.isfinite(result) or (eirp_w > 0 and result == 0):
        raise ValueError('Result outside floating-point range')
    return result
