"""Простые модели согласования и потерь однородного кабеля."""
import math


def _finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('expected a finite real number')
    return value


def reflection_from_vswr(vswr):
    """Модуль Γ для конечного КСВН >= 1; коэффициент безразмерный."""
    v = _finite(vswr)
    if v < 1:
        raise ValueError('VSWR must be >= 1')
    # Избегаем переполнения v+1 для больших значений.
    result = (1 - 1 / v) / (1 + 1 / v)
    if result == 1:
        raise ValueError('result rounds to the full-reflection boundary')
    return result


def vswr_from_reflection(magnitude):
    """Модуль Γ от 0 до 1; Γ=1 означает бесконечный КСВН."""
    rho = _finite(magnitude)
    if not 0 <= rho <= 1:
        raise ValueError('reflection magnitude must be in [0, 1]')
    return math.inf if rho == 1 else (1 + rho) / (1 - rho)


def return_loss_db(magnitude):
    """Положительный return loss; Γ=0 соответствует бесконечности."""
    rho = _finite(magnitude)
    if not 0 <= rho <= 1:
        raise ValueError('reflection magnitude must be in [0, 1]')
    return math.inf if rho == 0 else -20 * math.log10(rho)


def reflection_from_return_loss(return_loss):
    """Положительный return loss в dB; +inf соответствует идеальному согласованию."""
    if isinstance(return_loss, bool) or not isinstance(return_loss, (int, float)) or math.isnan(return_loss) or return_loss < 0:
        raise ValueError('return loss must be >= 0 dB')
    if return_loss == math.inf:
        return 0.0
    result = 10 ** (-return_loss / 20)
    if result == 0:
        raise ValueError('result outside floating-point range')
    return result


def cable_loss_db(attenuation_db_per_100m, length_m):
    """Оценка потерь однородного кабеля без разъёмов, в dB."""
    a, length = _finite(attenuation_db_per_100m), _finite(length_m)
    if a < 0 or length < 0:
        raise ValueError('attenuation and length must be nonnegative')
    result = a * (length / 100)
    if not math.isfinite(result) or (a > 0 and length > 0 and result == 0):
        raise ValueError('result outside floating-point range')
    return result
