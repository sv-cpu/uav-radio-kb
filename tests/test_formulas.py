import math
import unittest

from calculations.wavelength import wavelength_m


class WavelengthTest(unittest.TestCase):
    def test_analytic_one_metre(self):
        # c / 299792458 Hz = 1 m exactly; c is the SI defining constant.
        self.assertEqual(wavelength_m(299_792_458), 1.0)

    def test_example(self):
        # Independent decimal long division, rounded to 10 decimal places.
        self.assertAlmostEqual(wavelength_m(300_000_000), 0.9993081933, delta=0.00000000005)

    def test_frequency_doubles(self):
        self.assertAlmostEqual(wavelength_m(200_000_000), wavelength_m(100_000_000) / 2)

    def test_invalid(self):
        for value in (0, -1, math.inf, -math.inf, math.nan, True, "300"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                wavelength_m(value)


if __name__ == "__main__":
    unittest.main()
