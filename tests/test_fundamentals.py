import math
import unittest
from calculations.fundamentals import resistive_power_w, power_level_db, bit_rate_bps


class FundamentalsTest(unittest.TestCase):
    def test_power_analytic(self):
        self.assertEqual(resistive_power_w(1, 50), 0.02)
        self.assertEqual(resistive_power_w(0, 50), 0)
        self.assertEqual(resistive_power_w(2, 50), 0.08)

    def test_logarithms(self):
        for p, ref, expected in ((1, 1, 0), (10, 1, 10), (0.001, 1, -30), (1, 0.001, 30)):
            self.assertAlmostEqual(power_level_db(p, ref), expected, delta=1e-12)
        self.assertAlmostEqual(power_level_db(1e300, 1e-300), 6000, delta=1e-10)

    def test_symbol_mapping(self):
        self.assertEqual(bit_rate_bps(100000, 2), 200000)
        self.assertEqual(bit_rate_bps(0, 2), 0)

    def test_domains(self):
        for bad in (-1, math.nan, math.inf, True, '1'):
            for function, args in ((resistive_power_w, (bad, 50)), (resistive_power_w, (1, bad)),
                                   (power_level_db, (bad, 1)), (power_level_db, (1, bad)),
                                   (bit_rate_bps, (bad, 2))):
                with self.subTest(function=function.__name__, bad=bad), self.assertRaises(ValueError):
                    function(*args)
        for function, args in ((resistive_power_w, (1, 0)), (power_level_db, (0, 1)),
                               (power_level_db, (1, 0)), (bit_rate_bps, (1, 0)), (bit_rate_bps, (1, 1.5))):
            with self.assertRaises(ValueError):
                function(*args)
