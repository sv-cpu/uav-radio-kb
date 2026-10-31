import math
import unittest
from calculations.antenna import (reflection_from_vswr, vswr_from_reflection,
                                  return_loss_db, reflection_from_return_loss, cable_loss_db)


class AntennaCalculationTest(unittest.TestCase):
    def test_published_mismatch_chart(self):
        # R&S RF Fundamentals Part 3, slide 18: VSWR 1.50 -> rho 0.2 -> RL 14.0 dB.
        self.assertAlmostEqual(reflection_from_vswr(1.5), 0.2, delta=1e-15)
        self.assertAlmostEqual(vswr_from_reflection(0.2), 1.5, delta=1e-15)
        self.assertAlmostEqual(return_loss_db(0.2), 14.0, delta=0.05)
        self.assertAlmostEqual(reflection_from_return_loss(14.0), 0.2, delta=0.0005)

    def test_published_10_db(self):
        # R&S slide 31: rounded |Γ| = 0.3162 at RL 10 dB.
        self.assertAlmostEqual(reflection_from_return_loss(10), 0.3162, delta=0.00005)
        self.assertAlmostEqual(vswr_from_reflection(reflection_from_return_loss(10)), 1.925, delta=0.0005)

    def test_boundaries(self):
        self.assertEqual(reflection_from_vswr(1), 0)
        self.assertEqual(vswr_from_reflection(0), 1)
        self.assertEqual(vswr_from_reflection(1), math.inf)
        self.assertEqual(return_loss_db(0), math.inf)
        self.assertEqual(return_loss_db(1), 0)
        self.assertEqual(reflection_from_return_loss(math.inf), 0)
        self.assertEqual(reflection_from_return_loss(0), 1)

    def test_extremes_do_not_silently_become_boundaries(self):
        with self.assertRaises(ValueError):
            reflection_from_vswr(1e308)
        with self.assertRaises(ValueError):
            reflection_from_return_loss(10000)

    def test_round_trips(self):
        for rho in (0.01, 0.2, 0.75, 0.99):
            self.assertAlmostEqual(reflection_from_vswr(vswr_from_reflection(rho)), rho, delta=1e-14)
            self.assertAlmostEqual(reflection_from_return_loss(return_loss_db(rho)), rho, delta=1e-14)

    def test_cable_reference_and_scaling(self):
        # LMR-195: 36.5 dB/100 m at 900 MHz; 2 m = 0.73 dB.
        self.assertAlmostEqual(cable_loss_db(36.5, 2), 0.73, delta=1e-12)
        self.assertAlmostEqual(cable_loss_db(36.5, 4), 1.46, delta=1e-12)
        self.assertEqual(cable_loss_db(36.5, 0), 0)

    def test_reject_invalid(self):
        for func, values in ((reflection_from_vswr, (0, -1, math.inf, math.nan, True, '1')),
                             (vswr_from_reflection, (-0.1, 1.1, math.nan, math.inf, True)),
                             (return_loss_db, (-1, 1.1, math.nan, math.inf, True)),
                             (reflection_from_return_loss, (-1, -math.inf, math.nan, True))):
            for v in values:
                with self.subTest(function=func.__name__, value=v), self.assertRaises(ValueError):
                    func(v)
        for pair in ((-1, 1), (1, -1), (math.inf, 1), (1, math.nan), (True, 1), (1e308, 1e308)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                cable_loss_db(*pair)
