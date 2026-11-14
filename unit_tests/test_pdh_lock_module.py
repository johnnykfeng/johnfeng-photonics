import unittest

import numpy as np

from johnfeng_photonics.pdh_lock_module import (
    create_simulation,
    pdh_error,
    reflected_power,
    rf_signals,
)


PARAMS = {
    "cavity_center": 0.0,
    "cavity_fwhm": 10.0,
    "modulation_frequency": 30.0,
    "modulation_index": 0.5,
    "demod_phase_deg": 0.0,
    "Kp": 6000.0,
    "Ki": 50000.0,
    "filter_time": 0.0003,
    "lock_on_time": 0.01,
    "drift_on": False,
    "drift_offset": 10.0,
    "drift_slope": 50.0,
    "noise_amp": 0.0,
    "seed": 0,
    "t_total": 0.03,
    "dt": 0.00001,
}


class TestPdhLockModule(unittest.TestCase):
    def test_reflection_dip_and_signed_error(self):
        frequencies = np.array([-1.0, 0.0, 1.0])
        np.testing.assert_allclose(reflected_power(frequencies, PARAMS), [1 / 26, 0, 1 / 26])
        error = pdh_error(frequencies, PARAMS)
        self.assertAlmostEqual(error[0], -error[2])
        self.assertAlmostEqual(error[1], 0.0)
        self.assertGreater(error[2], 0.0)

    def test_rf_mixer_average_matches_analytic_error(self):
        for phase in (0.0, 35.0):
            parameters = {**PARAMS, "demod_phase_deg": phase}
            for frequency in (-5.0, 0.0, 3.0):
                with self.subTest(phase=phase, frequency=frequency):
                    _, _, _, mixed = rf_signals(frequency, parameters)
                    self.assertAlmostEqual(
                        np.mean(mixed), pdh_error(frequency, parameters)
                    )

    def test_pi_loop_moves_laser_toward_resonance(self):
        t, free_running, locked, error = create_simulation(PARAMS)
        self.assertEqual(len(t), len(free_running))
        self.assertEqual(len(t), len(locked))
        self.assertEqual(len(t), len(error))
        self.assertAlmostEqual(locked[0], 10.0)
        self.assertAlmostEqual(locked[999], 10.0)
        self.assertLess(abs(locked[-1]), 1.0)
        self.assertLess(abs(locked[-1]), abs(free_running[-1]))


if __name__ == "__main__":
    unittest.main()
