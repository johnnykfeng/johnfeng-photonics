import numpy as np


def cavity_transmission(f, cavity_center, cavity_fwhm, cavity_port):
    """Models the reference cavity as a Lorentzian resonance peak."""
    lorentzian = 1.0 / (1.0 + (2.0 * (f - cavity_center) / cavity_fwhm) ** 2)
    if cavity_port == "return":
        return 1.0 - lorentzian
    return lorentzian


def animate_s_curve(p):

    f_sweep = np.linspace(-20, 20, 600)

    t_fast = np.linspace(0, 5 / p['dither_freq'], 500)

    error_signal = np.zeros_like(f_sweep)
    for i, f in enumerate(f_sweep):
        omega = 2 * np.pi * p["dither_freq"]
        dither = np.sin(omega * t_fast)
        f_inst = f + p['dither_amp'] * dither
        pd_signal = cavity_transmission(
            f_inst, p['cavity_center'], p['cavity_fwhm'], p['cavity_port']
        )
        mixed = pd_signal * dither
        error_signal[i] = np.mean(mixed)

    # error_signal = error_signal / np.max(np.abs(error_signal))

    return f_sweep, t_fast, error_signal


def create_simulation(p):
    """Run the dither-lock servo simulation, returning the time traces."""
    np.random.seed(p["seed"])

    dt = p["dt"]
    t = np.arange(0, p["t_total"], dt)

    omega = 2 * np.pi * p["dither_freq"]

    # Simulate an unlocked drifting laser (random walk + linear drift).
    # If the "drift_on" parameter is True, simulate the free-running (unlocked) laser frequency over time as follows:
    # - Start at the provided offset ("drift_offset"),
    # - Add a linear drift with slope "drift_slope",
    # - Add a random-walk (Brownian motion) noise with standard deviation "noise_amp" at each time step.
    # - np.cumsum(np.random...) is array with size len(t)
    # The cumulative sum of random values represents the accumulation of small random deviations over time.
    if p['drift_on']:
        f_free_running = (
            p["drift_offset"]
            + p["drift_slope"] * t
            + np.cumsum(np.random.normal(0, p["noise_amp"], len(t)))
        )

    else:
        f_free_running = (
            p['drift_offset']
            # + p["drift_slope"]*t
            + np.zeros_like(t)
        )

    f_locked = np.zeros_like(t)
    filtered_error_hist = np.zeros_like(t)
    f_current = f_free_running[0]
    integral_error = 0.0
    filtered_error = 0.0

    for i in range(len(t)):
        if i > 0:
            f_current += f_free_running[i] - f_free_running[i - 1]

        # Apply physical dither.
        dither_val = p["dither_amp"] * np.sin(omega * t[i])
        f_inst = f_current + dither_val

        # Photodetector and demodulation (mixer).
        pd_signal = cavity_transmission(
            f_inst, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
        )
        mixed_signal = pd_signal * np.sin(omega * t[i])

        # Low-pass filter (RC filter simulation).
        filtered_error = (1 - p["lpf_alpha"]) * filtered_error + p["lpf_alpha"] * mixed_signal

        # PID controller.
        if t[i] >= p["lock_on_time"]:
            integral_error += filtered_error * dt
            correction = (p["Kp"] * filtered_error) + (p["Ki"] * integral_error)
            if p["cavity_port"] == "return":
                f_current -= correction
            else:
                f_current += correction

        f_locked[i] = f_current
        filtered_error_hist[i] = filtered_error

    return t, f_free_running, f_locked, filtered_error_hist
