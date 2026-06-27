import unittest

import numpy as np
from pydantic import ValidationError

from johnfeng_photonics.photonic_units import (
    AngularFrequency,
    AngularFrequencyUnit,
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    SPEED_OF_LIGHT,
    Wavelength,
    WavelengthUnit,
)


class TestWavelength(unittest.TestCase):
    def test_explicit_unit_case_insensitive(self):
        wl = Wavelength(value_si=532.0e-9, unit="nM")
        self.assertAlmostEqual(wl.value_si, 532.0e-9)
        self.assertEqual(wl.unit, WavelengthUnit.NANOMETER)
        self.assertAlmostEqual(wl.value_unit, 532.0)

    def test_default_unit_is_nanometer(self):
        wl = Wavelength(value_si=532.0e-9)
        self.assertEqual(wl.unit, WavelengthUnit.NANOMETER)
        self.assertAlmostEqual(wl.value_unit, 532.0)

    def test_micrometer_conversion(self):
        wl = Wavelength(value_si=532.0e-6, unit="um")
        self.assertEqual(wl.unit, WavelengthUnit.MICROMETER)
        self.assertAlmostEqual(wl.value_unit, 532.0)

    def test_invalid_unit_raises(self):
        with self.assertRaises(ValidationError):
            Wavelength(value_si=532.0e-9, unit="NotAUnit")

    def test_non_positive_value_raises(self):
        with self.assertRaises(ValidationError):
            Wavelength(value_si=0)

    def test_list_input(self):
        wl = Wavelength(value_si=[532.0e-9, 1550.0e-9])
        self.assertTrue(wl.is_array)
        np.testing.assert_allclose(wl.value_si, [532.0e-9, 1550.0e-9])
        np.testing.assert_allclose(wl.value_unit, [532.0, 1550.0])

    def test_ndarray_input(self):
        values = np.array([532.0e-9, 1550.0e-9])
        wl = Wavelength(value_si=values)
        self.assertTrue(wl.is_array)
        np.testing.assert_allclose(wl.value_unit, [532.0, 1550.0])

    def test_non_positive_array_element_raises(self):
        with self.assertRaises(ValidationError):
            Wavelength(value_si=[532.0e-9, 0.0])

    def test_scalar_is_not_array(self):
        wl = Wavelength(value_si=532.0e-9)
        self.assertFalse(wl.is_array)
        self.assertIsInstance(wl.value_si, float)

    def test_tuple_input(self):
        wl = Wavelength(value_si=(532.0e-9, 1550.0e-9))
        self.assertTrue(wl.is_array)
        np.testing.assert_allclose(wl.value_unit, [532.0, 1550.0])

    def test_array_with_non_default_unit(self):
        wl = Wavelength(value_si=[532.0e-6, 1550.0e-6], unit="um")
        np.testing.assert_allclose(wl.value_unit, [532.0, 1550.0])

    def test_empty_array_allowed(self):
        wl = Wavelength(value_si=[])
        self.assertTrue(wl.is_array)
        self.assertEqual(wl.value_si.size, 0)

    def test_negative_scalar_raises(self):
        with self.assertRaises(ValidationError):
            Wavelength(value_si=-1.0e-9)


class TestFrequency(unittest.TestCase):
    def test_explicit_unit_enum(self):
        freq = Frequency(value_si=193.1e12, unit=FrequencyUnit.TERAHERTZ)
        self.assertAlmostEqual(freq.value_si, 193.1e12)
        self.assertEqual(freq.unit, FrequencyUnit.TERAHERTZ)
        self.assertAlmostEqual(freq.value_unit, 193.1)

    def test_explicit_unit_case_insensitive(self):
        freq = Frequency(value_si=193.1e3, unit="khz")
        self.assertEqual(freq.unit, FrequencyUnit.KILOHERTZ)
        self.assertAlmostEqual(freq.value_unit, 193.1)

    def test_default_unit_is_gigahertz(self):
        freq = Frequency(value_si=193.1e9)
        self.assertEqual(freq.unit, FrequencyUnit.GIGAHERTZ)
        self.assertAlmostEqual(freq.value_unit, 193.1)

    def test_invalid_unit_raises(self):
        with self.assertRaises(ValidationError):
            Frequency(value_si=193.1e9, unit="NotAUnit")

    def test_non_positive_value_raises(self):
        with self.assertRaises(ValidationError):
            Frequency(value_si=0, unit=FrequencyUnit.GIGAHERTZ)

    def test_list_input(self):
        freq = Frequency(value_si=[193.1e9, 200.0e9])
        self.assertTrue(freq.is_array)
        np.testing.assert_allclose(freq.value_si, [193.1e9, 200.0e9])
        np.testing.assert_allclose(freq.value_unit, [193.1, 200.0])

    def test_ndarray_input(self):
        values = np.array([193.1e12, 200.0e12])
        freq = Frequency(value_si=values, unit=FrequencyUnit.TERAHERTZ)
        self.assertTrue(freq.is_array)
        np.testing.assert_allclose(freq.value_unit, [193.1, 200.0])

    def test_non_positive_array_element_raises(self):
        with self.assertRaises(ValidationError):
            Frequency(value_si=[193.1e9, -1.0])

    def test_scalar_is_not_array(self):
        freq = Frequency(value_si=193.1e9)
        self.assertFalse(freq.is_array)
        self.assertIsInstance(freq.value_si, float)

    def test_tuple_input(self):
        freq = Frequency(value_si=(193.1e9, 200.0e9))
        self.assertTrue(freq.is_array)
        np.testing.assert_allclose(freq.value_unit, [193.1, 200.0])

    def test_array_with_non_default_unit(self):
        freq = Frequency(value_si=[193.1e12, 200.0e12], unit=FrequencyUnit.TERAHERTZ)
        np.testing.assert_allclose(freq.value_unit, [193.1, 200.0])

    def test_empty_array_allowed(self):
        freq = Frequency(value_si=[])
        self.assertTrue(freq.is_array)
        self.assertEqual(freq.value_si.size, 0)


class TestAngularFrequency(unittest.TestCase):
    def test_explicit_unit_enum(self):
        omega = AngularFrequency(value_si=1215.0e12, unit=AngularFrequencyUnit.TERA_RAD_PER_SEC)
        self.assertAlmostEqual(omega.value_si, 1215.0e12)
        self.assertEqual(omega.unit, AngularFrequencyUnit.TERA_RAD_PER_SEC)
        self.assertAlmostEqual(omega.value_unit, 1215.0)

    def test_explicit_unit_case_insensitive(self):
        omega = AngularFrequency(value_si=2.0e12, unit="trad/s")
        self.assertEqual(omega.unit, AngularFrequencyUnit.TERA_RAD_PER_SEC)
        self.assertAlmostEqual(omega.value_unit, 2.0)

    def test_default_unit_is_rad_per_sec(self):
        omega = AngularFrequency(value_si=1.0)
        self.assertEqual(omega.unit, AngularFrequencyUnit.RAD_PER_SEC)
        self.assertAlmostEqual(omega.value_unit, 1.0)

    def test_invalid_unit_raises(self):
        with self.assertRaises(ValidationError):
            AngularFrequency(value_si=1215.0e12, unit="NotAUnit")

    def test_non_positive_value_raises(self):
        with self.assertRaises(ValidationError):
            AngularFrequency(value_si=0, unit=AngularFrequencyUnit.TERA_RAD_PER_SEC)

    def test_list_input(self):
        omega = AngularFrequency(value_si=[1.0e12, 2.0e12])
        self.assertTrue(omega.is_array)
        np.testing.assert_allclose(omega.value_si, [1.0e12, 2.0e12])
        np.testing.assert_allclose(omega.value_unit, [1.0e12, 2.0e12])

    def test_ndarray_input(self):
        values = np.array([1215.0e12, 1300.0e12])
        omega = AngularFrequency(value_si=values, unit=AngularFrequencyUnit.TERA_RAD_PER_SEC)
        self.assertTrue(omega.is_array)
        np.testing.assert_allclose(omega.value_unit, [1215.0, 1300.0])

    def test_non_positive_array_element_raises(self):
        with self.assertRaises(ValidationError):
            AngularFrequency(value_si=[1.0e12, 0.0])

    def test_scalar_is_not_array(self):
        omega = AngularFrequency(value_si=1.0e12)
        self.assertFalse(omega.is_array)
        self.assertIsInstance(omega.value_si, float)

    def test_tuple_input(self):
        omega = AngularFrequency(value_si=(1.0e12, 2.0e12), unit="Trad/s")
        self.assertTrue(omega.is_array)
        np.testing.assert_allclose(omega.value_unit, [1.0, 2.0])

    def test_array_with_non_default_unit(self):
        omega = AngularFrequency(
            value_si=[1.0e3, 2.0e3],
            unit=AngularFrequencyUnit.KILO_RAD_PER_SEC,
        )
        np.testing.assert_allclose(omega.value_unit, [1.0, 2.0])

    def test_empty_array_allowed(self):
        omega = AngularFrequency(value_si=[])
        self.assertTrue(omega.is_array)
        self.assertEqual(omega.value_si.size, 0)


class TestPhotonicUnit(unittest.TestCase):
    def test_scalar_from_wavelength(self):
        pu = PhotonicUnit(wavelength=1550e-9)
        self.assertFalse(pu.is_array)
        self.assertAlmostEqual(pu.wavelength.value_unit, 1550.0)
        self.assertAlmostEqual(pu.frequency.value_unit, 193419.3548387097, places=3)

    def test_scalar_from_frequency(self):
        pu = PhotonicUnit(frequency=193.1e9)
        self.assertFalse(pu.is_array)
        self.assertAlmostEqual(pu.frequency.value_unit, 193.1)
        self.assertAlmostEqual(pu.wavelength.value_unit, 1552563.43863283, places=3)

    def test_scalar_from_angular_frequency(self):
        pu = PhotonicUnit(angular_frequency=1.213e15)
        self.assertFalse(pu.is_array)
        self.assertAlmostEqual(pu.angular_frequency.value_si, 1.213e15)
        self.assertAlmostEqual(pu.frequency.value_si, 1.213e15 / (2 * np.pi))

    def test_array_from_wavelength_list(self):
        pu = PhotonicUnit(wavelength=[532e-9, 1550e-9])
        self.assertTrue(pu.is_array)
        self.assertTrue(pu.frequency.is_array)
        self.assertTrue(pu.angular_frequency.is_array)
        np.testing.assert_allclose(pu.wavelength.value_unit, [532.0, 1550.0])
        np.testing.assert_allclose(
            pu.frequency.value_si,
            np.array([SPEED_OF_LIGHT / 532e-9, SPEED_OF_LIGHT / 1550e-9]),
        )

    def test_array_from_wavelength_object(self):
        wl = Wavelength(value_si=np.linspace(1500e-9, 1600e-9, 4))
        pu = PhotonicUnit(wavelength=wl)
        self.assertTrue(pu.is_array)
        np.testing.assert_allclose(pu.wavelength.value_si, wl.value_si)
        np.testing.assert_allclose(pu.frequency.value_si, SPEED_OF_LIGHT / wl.value_si)

    def test_array_from_frequency_ndarray(self):
        freqs = np.array([193.1e9, 200.0e9])
        pu = PhotonicUnit(frequency=freqs)
        self.assertTrue(pu.is_array)
        np.testing.assert_allclose(pu.wavelength.value_unit, [1552563.43863283, 1499000.0])

    def test_array_from_frequency_object(self):
        freq = Frequency(value_si=[193.1e9, 200.0e9], unit=FrequencyUnit.GIGAHERTZ)
        pu = PhotonicUnit(frequency=freq)
        self.assertTrue(pu.is_array)
        np.testing.assert_allclose(pu.frequency.value_si, freq.value_si)
        np.testing.assert_allclose(pu.wavelength.value_si, SPEED_OF_LIGHT / freq.value_si)

    def test_array_from_angular_frequency(self):
        pu = PhotonicUnit(angular_frequency=[1.0e12, 2.0e12])
        self.assertTrue(pu.is_array)
        np.testing.assert_allclose(
            pu.frequency.value_si,
            np.array([1.0e12 / (2 * np.pi), 2.0e12 / (2 * np.pi)]),
        )

    def test_array_from_angular_frequency_object(self):
        omega = AngularFrequency(
            value_si=[1.0e12, 2.0e12],
            unit=AngularFrequencyUnit.TERA_RAD_PER_SEC,
        )
        pu = PhotonicUnit(angular_frequency=omega)
        self.assertTrue(pu.is_array)
        np.testing.assert_allclose(pu.angular_frequency.value_si, omega.value_si)
        np.testing.assert_allclose(
            pu.wavelength.value_si,
            2 * np.pi * SPEED_OF_LIGHT / omega.value_si,
        )

    def test_derived_units_for_scalar(self):
        pu = PhotonicUnit(wavelength=1550e-9)
        self.assertEqual(pu.frequency.unit, FrequencyUnit.GIGAHERTZ)
        self.assertEqual(
            pu.angular_frequency.unit,
            AngularFrequencyUnit.TERA_RAD_PER_SEC,
        )

    def test_derived_units_for_array(self):
        pu = PhotonicUnit(wavelength=[532e-9, 1550e-9])
        self.assertEqual(pu.frequency.unit, FrequencyUnit.GIGAHERTZ)
        self.assertEqual(
            pu.angular_frequency.unit,
            AngularFrequencyUnit.TERA_RAD_PER_SEC,
        )

    def test_round_trip_wavelength_frequency_consistency(self):
        wl_si = np.array([532e-9, 1550e-9, 1310e-9])
        pu = PhotonicUnit(wavelength=wl_si)
        np.testing.assert_allclose(pu.wavelength.value_si, wl_si)
        np.testing.assert_allclose(pu.frequency.value_si, SPEED_OF_LIGHT / wl_si)
        np.testing.assert_allclose(pu.angular_frequency.value_si, 2 * np.pi * SPEED_OF_LIGHT / wl_si)

    def test_round_trip_frequency_angular_frequency_consistency(self):
        freq_hz = np.array([193.1e9, 200.0e9])
        pu = PhotonicUnit(frequency=freq_hz)
        np.testing.assert_allclose(pu.frequency.value_si, freq_hz)
        np.testing.assert_allclose(pu.angular_frequency.value_si, 2 * np.pi * freq_hz)
        np.testing.assert_allclose(pu.wavelength.value_si, SPEED_OF_LIGHT / freq_hz)

    def test_all_quantities_share_array_shape(self):
        pu = PhotonicUnit(wavelength=np.linspace(1500e-9, 1600e-9, 5))
        self.assertEqual(pu.wavelength.value_si.shape, (5,))
        self.assertEqual(pu.frequency.value_si.shape, (5,))
        self.assertEqual(pu.angular_frequency.value_si.shape, (5,))

    def test_model_validate_from_existing_instance(self):
        original = PhotonicUnit(wavelength=[532e-9, 1550e-9])
        copied = PhotonicUnit.model_validate(original)
        self.assertTrue(copied.is_array)
        np.testing.assert_allclose(copied.wavelength.value_si, original.wavelength.value_si)
        np.testing.assert_allclose(copied.frequency.value_si, original.frequency.value_si)

    def test_model_copy_preserves_array_data(self):
        original = PhotonicUnit(frequency=[193.1e9, 200.0e9])
        copied = original.model_copy()
        self.assertTrue(copied.is_array)
        np.testing.assert_allclose(copied.frequency.value_si, original.frequency.value_si)
        np.testing.assert_allclose(copied.wavelength.value_si, original.wavelength.value_si)

    def test_exactly_one_quantity_required(self):
        with self.assertRaises(ValueError):
            PhotonicUnit(wavelength=1550e-9, frequency=193.1e9)

    def test_no_quantity_raises(self):
        with self.assertRaises(ValueError):
            PhotonicUnit()

    def test_all_three_quantities_raises(self):
        with self.assertRaises(ValueError):
            PhotonicUnit(
                wavelength=1550e-9,
                frequency=193.1e9,
                angular_frequency=1.213e15,
            )

    def test_non_dict_input_raises(self):
        with self.assertRaises(TypeError):
            PhotonicUnit("not-a-dict")

    def test_empty_array_input(self):
        pu = PhotonicUnit(wavelength=[])
        self.assertTrue(pu.is_array)
        self.assertEqual(pu.wavelength.value_si.size, 0)
        self.assertEqual(pu.frequency.value_si.size, 0)
        self.assertEqual(pu.angular_frequency.value_si.size, 0)

    def test_non_positive_array_input_raises(self):
        with self.assertRaises(ValidationError):
            PhotonicUnit(wavelength=[532e-9, 0.0])

    def test_unit_change_on_derived_array(self):
        pu = PhotonicUnit(wavelength=np.linspace(1500e-9, 1600e-9, 3))
        pu.frequency.unit = FrequencyUnit.TERAHERTZ
        pu.wavelength.unit = WavelengthUnit.MICROMETER
        np.testing.assert_allclose(pu.wavelength.value_unit, [1.5, 1.55, 1.6])
        self.assertEqual(pu.frequency.value_unit.shape, (3,))
        self.assertTrue(np.all(pu.frequency.value_unit > 0))


if __name__ == "__main__":
    unittest.main()

# command to run tests: python -m unittest discover -s unit_tests -p 'test_*.py'