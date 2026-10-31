import math
import unittest
from calculations.propagation import free_space_flux_w_m2


class FluxTest(unittest.TestCase):
    def test_reference(self):
        # Независимое десятичное значение 1/(4*pi), округлённое до 15 знаков.
        self.assertAlmostEqual(free_space_flux_w_m2(1, 1), 0.079577471545948,
                               delta=5e-16)

    def test_sphere_conservation(self):
        # Аналитически: 4*pi W распределены по сфере площади 4*pi m² -> 1 W/m².
        self.assertAlmostEqual(free_space_flux_w_m2(4 * math.pi, 1), 1, delta=1e-15)

    def test_distance_doubling(self):
        self.assertAlmostEqual(free_space_flux_w_m2(1, 200),
                               free_space_flux_w_m2(1, 100) / 4, delta=1e-21)

    def test_power_scaling(self):
        self.assertAlmostEqual(free_space_flux_w_m2(2, 100),
                               2 * free_space_flux_w_m2(1, 100), delta=1e-21)

    def test_zero_power(self):
        self.assertEqual(free_space_flux_w_m2(0, 1), 0)

    def test_invalid_inputs(self):
        for args in ((-1, 1), (1, 0), (1, -1), (True, 1), (1, True), ('1', 1),
                     (math.nan, 1), (1, math.nan), (math.inf, 1), (1, math.inf)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                free_space_flux_w_m2(*args)

    def test_numeric_range(self):
        for args in ((1e308, 1e-308), (1e-308, 1e308)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                free_space_flux_w_m2(*args)
