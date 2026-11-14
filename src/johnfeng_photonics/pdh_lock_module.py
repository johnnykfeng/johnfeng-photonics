"""Small-signal Pound–Drever–Hall (PDH) cavity-lock model.

Frequencies are in MHz and time is in seconds. The cavity is a critically
coupled, single-ended reflection dip. The carrier and first phase-modulation
sidebands are retained; higher-order sidebands and detector noise are omitted.
The RF beat is averaged analytically, so the modulation tone does not need
to be sampled by the slower servo simulation.
"""

import numpy as np


def reflection_coefficient(frequency, cavity_center, cavity_fwhm):
    """Complex reflected field for a critically coupled Lorentzian cavity."""
    detuning = np.asarray(frequency) - cavity_center
    half_width = cavity_fwhm / 2
    return detuning / (detuning + 1j * half_width)


def reflected_power(frequency, p):
    """Normalized reflected power of an unmodulated laser."""
    reflected_field = reflection_coefficient(
        frequency, p["cavity_center"], p["cavity_fwhm"]
    )
    return np.abs(reflected_field) ** 2


def _sideband_amplitudes(modulation_index):
    """J0 and J1 of the phase-modulated field, via a short Taylor series."""
    beta = modulation_index
    carrier = 1 - beta**2 / 4 + beta**4 / 64 - beta**6 / 2304
    sideband = beta / 2 - beta**3 / 16 + beta**5 / 384 - beta**7 / 18432
    return carrier, sideband


def reflected_components(frequency, p):
    """Carrier and +/-1 sideband fields after reflection from the cavity."""
    carrier_amp, sideband_amp = _sideband_amplitudes(p["modulation_index"])
    center = p["cavity_center"]
    width = p["cavity_fwhm"]
    offset = p["modulation_frequency"]
    carrier = carrier_amp * reflection_coefficient(frequency, center, width)
    upper = sideband_amp * reflection_coefficient(frequency + offset, center, width)
    lower = -sideband_amp * reflection_coefficient(frequency - offset, center, width)
    return carrier, upper, lower


def pdh_error(frequency, p):
    """DC mixer output from the reflected power at the RF fundamental.

    The in-phase setting uses a negative sine reference, yielding a positive
    error for a carrier above resonance when the sidebands are well outside it.
    """
    carrier, upper, lower = reflected_components(frequency, p)
    beat = upper * np.conj(carrier) + carrier * np.conj(lower)
    phase = np.deg2rad(p["demod_phase_deg"])
    return np.imag(beat) * np.cos(phase) - np.real(beat) * np.sin(phase)


def rf_signals(frequency, p, cycles=5, samples=500):
    """Return RF-cycle traces of detector power, mixer reference, and product."""
    carrier, upper, lower = reflected_components(frequency, p)
    theta = np.linspace(0, 2 * np.pi * cycles, samples, endpoint=False)
    field = carrier + upper * np.exp(1j * theta) + lower * np.exp(-1j * theta)
    detector = np.abs(field) ** 2
    reference = -np.sin(theta + np.deg2rad(p["demod_phase_deg"]))
    mixed = detector * reference
    return theta / (2 * np.pi), detector, reference, mixed


def create_simulation(p):
    """Simulate a PI servo driven by the averaged PDH error signal."""
    rng = np.random.default_rng(p["seed"])
    dt = p["dt"]
    t = np.arange(0, p["t_total"], dt)
    if p["drift_on"]:
        free_running = (
            p["drift_offset"]
            + p["drift_slope"] * t
            + np.cumsum(rng.normal(0, p["noise_amp"], len(t)))
        )
    else:
        free_running = np.full_like(t, p["drift_offset"])

    locked = np.empty_like(t)
    filtered_error_history = np.empty_like(t)
    frequency = float(free_running[0])
    filtered_error = 0.0
    integrated_error = 0.0
    alpha = 1 - np.exp(-dt / p["filter_time"])

    for i, instant in enumerate(t):
        if i:
            frequency += free_running[i] - free_running[i - 1]

        measured_error = float(pdh_error(frequency, p))
        filtered_error += alpha * (measured_error - filtered_error)
        if instant >= p["lock_on_time"]:
            integrated_error += filtered_error * dt
            correction_rate = (
                p["Kp"] * filtered_error + p["Ki"] * integrated_error
            )
            frequency -= correction_rate * dt

        locked[i] = frequency
        filtered_error_history[i] = filtered_error

    return t, free_running, locked, filtered_error_history
