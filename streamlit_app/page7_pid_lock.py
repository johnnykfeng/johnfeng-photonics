"""Streamlit app: interactive PID dither-lock simulation.

Run with:
    streamlit run streamlit_pid_lock.py

The animation is rendered directly in the browser via matplotlib's
JS-HTML embedding (``anim.to_jshtml``). GIF and MP4 downloads are
generated in memory on demand via ``anim.save(...)``.
"""

import tempfile
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from matplotlib.animation import FuncAnimation
import johnfeng_photonics.pid_lock_module as pid_lock_module
from johnfeng_photonics.pid_lock_module import cavity_transmission, create_simulation, animate_s_curve
import matplotlib

matplotlib.use("Agg")  # headless backend, no GUI window

# Allow large inline animations to be embedded as HTML/JS.
plt.rcParams["animation.embed_limit"] = 200  # MB

try:
    import imageio_ffmpeg

    plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass


def animation_to_gif_bytes(anim, fps):
    """Render a FuncAnimation to GIF bytes for st.download_button."""
    with tempfile.NamedTemporaryFile(suffix=".gif") as tmp:
        anim.save(tmp.name, writer="pillow", fps=fps)
        tmp.seek(0)
        return tmp.read()


def animation_to_mp4_bytes(anim, fps):
    """Render a FuncAnimation to MP4 bytes for st.download_button."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
        anim.save(tmp.name, writer="ffmpeg", fps=fps)
        tmp.seek(0)
        return tmp.read()


def build_s_curve_animation(p):
    f_sweep, t_fast, error_signal = animate_s_curve(p)
    transmission_curve = cavity_transmission(
        f_sweep, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
    )
    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 11))
    fig.suptitle("Animation of dither signal through a resonance.")
    # fig.subplots_adjust(hspace=0.45)

    # Top panel: cavity peak + current dithered laser
    ax_top.plot(
        f_sweep,
        transmission_curve,
        color="black",
        lw=2,
        label="Cavity Transmission (0 slope at peak)",
    )
    dither_span = ax_top.axvspan(
        0, 0, color="green", alpha=0.15, label="Dither excursion"
    )
    (laser_pt,) = ax_top.plot(
        [], [], "o", color="green", ms=10, label="Laser frequency"
    )
    laser_line = ax_top.axvline(p["cavity_center"], color="green", ls="--", alpha=0.6)
    ax_top.axvline(0, color="gray", linestyle="--", alpha=0.3)
    ax_top.axvline(p["cavity_center"], color="blue", linestyle="--", alpha=0.3)
    ax_top.set_ylabel("Transmission")
    ax_top.set_xlim(f_sweep[0], f_sweep[-1])
    ax_top.set_ylim(-0.05, 1.1)
    ax_top.legend(loc="upper right")
    ax_top.grid(True, alpha=0.3)

    # Middle panel: instantaneous PD signal and mixer output at each sweep step
    t_ms = t_fast * 1e3
    omega = 2 * np.pi * p["dither_freq"]
    dither_ref = np.sin(omega * t_fast)
    (dither_line,) = ax_mid.plot(
        [],
        [],
        color="gray",
        lw=1.5,
        ls="--",
        alpha=0.45,
        label="dither(t) reference",
    )
    error_signal_scale = 5
    (pd_line,) = ax_mid.plot([], [], color="blue", lw=1.8, label="pd_signal(t)")
    (mixed_line,) = ax_mid.plot([], [], color="purple", lw=1.8, label="mixed(t)")
    (error_signal_line,) = ax_mid.plot(
        [],
        [],
        color="red",
        lw=1.8,
        ls="--",
        label=f"error_signal (x{error_signal_scale})",
    )
    ax_mid.axhline(0, color="gray", linestyle="--", alpha=0.4)
    ax_mid.set_xlabel("Fast Time (ms)")
    ax_mid.set_ylabel("Amplitude")
    ax_mid.set_xlim(t_ms[0], t_ms[-1])
    ax_mid.set_ylim(-1.1, 1.1)
    ax_mid.legend(loc="upper right")
    ax_mid.grid(True, alpha=0.3)

    # Bottom panel: error signal S-curve building up
    (error_curve,) = ax_bot.plot(
        [], [], color="red", lw=2, label="error_signal (Demodulated S-Curve)"
    )
    (error_pt,) = ax_bot.plot([], [], "o", color="red", ms=8)
    ax_bot.axvline(p["cavity_center"], color="blue", linestyle="--", alpha=0.5)
    ax_bot.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax_bot.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax_bot.set_xlabel("Laser Frequency Detuning (MHz)")
    ax_bot.set_ylabel("Normalized Error Signal")
    ax_bot.set_xlim(f_sweep[0], f_sweep[-1])
    ax_bot.set_ylim(min(error_signal) * 1.1, max(error_signal) * 1.1)
    ax_bot.legend(loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    fig.tight_layout()

    # Animate by stepping through f_sweep (subsample for a snappier playback)
    frames = range(0, len(f_sweep), 4)

    def update(i):
        f = f_sweep[i]
        f_inst = f + p["dither_amp"] * dither_ref
        pd_signal = cavity_transmission(
            f_inst, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
        )
        mixed = pd_signal * dither_ref

        # Current dither excursion drawn as a shaded band around f
        lo, hi = f - p["dither_amp"], f + p["dither_amp"]
        dither_span.set_x(lo)
        dither_span.set_width(hi - lo)
        laser_line.set_xdata([f, f])
        laser_pt.set_data(
            [f],
            [
                cavity_transmission(
                    f, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
                )
            ],
        )

        # Time-domain signals for this frame
        dither_line.set_data(t_ms, dither_ref)
        pd_line.set_data(t_ms, pd_signal)
        mixed_line.set_data(t_ms, mixed)
        error_signal_line.set_data(
            t_ms, np.ones(len(t_ms)) * error_signal[i] * error_signal_scale
        )  # scale up the error signal for visibility
        # ax_mid.axhline(y=error_signal[i], color ='red', linestyle='--', label = "error_signal")
        ax_mid.set_title(f"Instantaneous Signals at Detuning f = {f:.2f} MHz")

        # Error signal accumulated up to the current frequency
        error_curve.set_data(f_sweep[: i + 1], error_signal[: i + 1])
        error_pt.set_data([f], [error_signal[i]])
        return (
            dither_span,
            laser_line,
            laser_pt,
            dither_line,
            pd_line,
            mixed_line,
            error_curve,
            error_pt,
        )

    # anim = FuncAnimation(fig, update, frames=frames, interval=30, blit=False)

    anim = FuncAnimation(
        fig, update, frames=frames, interval=1000 / p["fps"], blit=False
    )
    return fig, anim


def build_animation(p):
    """Build the matplotlib FuncAnimation for the given parameters."""
    t, f_free_running, f_locked, filtered_error_hist = create_simulation(p)
    t_ms = t * 1e3

    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 11))
    fig.suptitle("PID locking the laser to the cavity")
    fig.subplots_adjust(bottom=0.07, hspace=0.35)

    # Top panel: cavity peak + current laser position homing onto resonance.
    f_axis = np.linspace(-20, max(f_free_running.max(), f_locked.max()) + 5, 600)
    ax_top.plot(
        f_axis,
        cavity_transmission(
            f_axis, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
        ),
        color="black",
        lw=2,
        label="Cavity Transmission (lock target)",
    )
    dither_span = ax_top.axvspan(
        0, 0, color="green", alpha=0.15, label="Dither excursion"
    )
    (laser_pt,) = ax_top.plot(
        [], [], "o", color="green", ms=10, label="Laser frequency"
    )
    laser_line = ax_top.axvline(0, color="green", ls="--", alpha=0.6)
    ax_top.axvline(p["cavity_center"], color="gray", linestyle="--", alpha=0.3)
    ax_top.set_xlabel("Laser Frequency Detuning (MHz)")
    ax_top.set_ylabel("Transmission")
    ax_top.set_xlim(f_axis[0], f_axis[-1])
    ax_top.set_ylim(-0.05, 1.1)
    ax_top.legend(loc="upper right")
    ax_top.grid(True, alpha=0.3)

    # Middle panel: laser frequency vs time (unlocked vs locked).
    (free_curve,) = ax_mid.plot(
        [], [], color="gray", linestyle=":", lw=2, label="Unlocked Laser (Drifting)"
    )
    (locked_curve,) = ax_mid.plot([], [], color="green", lw=2, label="Laser Frequency")
    (locked_pt,) = ax_mid.plot([], [], "o", color="green", ms=8)
    ax_mid.axhline(
        p["cavity_center"],
        color="black",
        linestyle="-",
        lw=1,
        label="Target Cavity Peak",
    )
    # ax_mid.axvline(p["lock_on_time"] * 1e3, color="red", linestyle="--", label="PID ON")
    ax_mid.axvspan(
        xmin=p["lock_on_time"] * 1e3,
        xmax=t_ms[-1],
        color="gold",
        alpha=0.2,
        label="PID ON",
    )

    ax_mid.set_xlabel("Time (ms)")
    ax_mid.set_ylabel("Laser Frequency (MHz)")
    ax_mid.set_xlim(t_ms[0], t_ms[-1])
    f_lo = min(f_free_running.min(), f_locked.min()) - 2
    f_hi = max(f_free_running.max(), f_locked.max()) + 2
    ax_mid.set_ylim(f_lo, f_hi)
    ax_mid.legend(loc="upper right")
    ax_mid.grid(True, alpha=0.3)

    # Bottom panel: filtered (demodulated) error signal vs time.
    (error_curve,) = ax_bot.plot(
        [], [], color="red", lw=2, label="filtered_error (PID input)"
    )
    (error_pt,) = ax_bot.plot([], [], "o", color="red", ms=8)
    ax_bot.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax_bot.axvspan(
        xmin=p["lock_on_time"] * 1e3,
        xmax=max(t_ms),
        color="gold",
        alpha=0.2,
        label="PID ON",
    )
    ax_bot.set_xlabel("Time (ms)")
    ax_bot.set_ylabel("Filtered Error Signal")
    ax_bot.set_xlim(t_ms[0], t_ms[-1])
    err_pad = 0.1 * (np.max(np.abs(filtered_error_hist)) + 1e-9)
    ax_bot.set_ylim(
        filtered_error_hist.min() - err_pad, filtered_error_hist.max() + err_pad
    )
    ax_bot.legend(loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    frames = range(0, len(t), p["frame_step"])

    def update(i):
        f = f_locked[i]
        lo, hi = f - p["dither_amp"], f + p["dither_amp"]
        dither_span.set_x(lo)
        dither_span.set_width(hi - lo)
        laser_line.set_xdata([f, f])
        laser_pt.set_data(
            [f],
            [
                cavity_transmission(
                    f, p["cavity_center"], p["cavity_fwhm"], p["cavity_port"]
                )
            ],
        )

        free_curve.set_data(t_ms[: i + 1], f_free_running[: i + 1])
        locked_curve.set_data(t_ms[: i + 1], f_locked[: i + 1])
        locked_pt.set_data([t_ms[i]], [f_locked[i]])
        ax_mid.set_title(f"PID Response at t = {t_ms[i]:.2f} ms")

        error_curve.set_data(t_ms[: i + 1], filtered_error_hist[: i + 1])
        error_pt.set_data([t_ms[i]], [filtered_error_hist[i]])
        return (
            dither_span,
            laser_line,
            laser_pt,
            free_curve,
            locked_curve,
            locked_pt,
            error_curve,
            error_pt,
        )

    anim = FuncAnimation(
        fig, update, frames=frames, interval=1000 / p["fps"], blit=False
    )
    return fig, anim


# ==========================================
# Streamlit UI
# ==========================================
st.set_page_config(page_title="PID Dither-Lock Simulator", layout="wide")
st.title("PID Dither-Lock Simulator")
st.write(
    "Interactive simulation of a laser frequency locked to a reference cavity "
    "using dither modulation and a PID. Set the parameters and run."
)

with st.sidebar:
    st.header("Cavity")
    cavity_center = st.number_input("Cavity center (MHz)", value=0.0, step=1.0)
    cavity_fwhm = st.number_input(
        "Cavity FWHM (MHz)", value=10.0, min_value=0.1, step=0.5
    )
    cavity_port = st.selectbox(
        "Cavity port",
        options=["return", "through"],
        index=0,
        help="'return' = reflection dip (peak inverted); 'through' = transmission peak.",
    )

    st.header("Dither")
    dither_freq = st.number_input(
        "Dither frequency (Hz)", value=5000.0, min_value=1.0, step=100.0
    )
    dither_amp_frac = st.slider(
        "Dither amplitude (fraction of FWHM)",
        min_value=0.01,
        max_value=1.0,
        value=0.2,
        step=0.01,
    )

    st.header("PID")
    Kp = st.number_input("Kp (proportional gain)", value=0.5, step=0.1, format="%.3f")
    Ki = st.number_input("Ki (integral gain)", value=50.0, step=1.0, format="%.3f")
    lpf_alpha = st.slider(
        "LPF alpha (low-pass coeff.)",
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
    )
    lock_on_time_ms = st.number_input(
        "PID ON time (ms)", value=10.0, min_value=0.0, step=1.0
    )

    st.header("Laser drift")
    drift_on = st.checkbox("Noise Drift ON", value=True)
    drift_offset = st.number_input("Initial offset (MHz)", value=10.0, step=1.0)
    drift_slope = st.number_input("Drift slope (MHz/s)", value=50.0, step=5.0)
    noise_amp = st.number_input(
        "Random-walk noise amplitude",
        value=0.1,
        min_value=0.0,
        step=0.05,
        format="%.3f",
    )
    seed = st.number_input("Random seed", value=0, min_value=0, step=1)

    st.header("Simulation / playback")
    t_total_ms = st.number_input("Total time (ms)", value=30.0, min_value=1.0, step=5.0)
    dt_ms = st.number_input(
        "Time step dt (ms)", value=0.01, min_value=0.001, step=0.005, format="%.3f"
    )
    frame_step = st.number_input(
        "Frame step (subsample)",
        value=20,
        min_value=1,
        step=1,
        help="Plot every Nth simulation step as an animation frame.",
    )
    fps = st.number_input("Playback FPS", value=10, min_value=1, max_value=60, step=1)

    params = {
        "cavity_center": cavity_center,
        "cavity_fwhm": cavity_fwhm,
        "cavity_port": cavity_port,
        "dither_freq": dither_freq,
        "dither_amp": dither_amp_frac * cavity_fwhm,
        "Kp": Kp,
        "Ki": Ki,
        "lpf_alpha": lpf_alpha,
        "lock_on_time": lock_on_time_ms * 1e-3,
        "drift_on": drift_on,
        "drift_offset": drift_offset,
        "drift_slope": drift_slope,
        "noise_amp": noise_amp,
        "seed": int(seed),
        "t_total": t_total_ms * 1e-3,
        "dt": dt_ms * 1e-3,
        "frame_step": int(frame_step),
        "fps": int(fps),
    }


simulate_dither_lock_btn = st.button("Simulate dither-locking", type="primary")
create_s_curve_anim_btn = st.button("Animate signal s-curve", type="primary")
simulate_all_btn = st.button("Simulate all", type="primary")

if simulate_dither_lock_btn or simulate_all_btn:
    with st.spinner("Running simulation and rendering animation..."):
        fig, anim = build_animation(params)
        html = anim.to_jshtml()
        dither_lock_gif = animation_to_gif_bytes(anim, params["fps"])
        dither_lock_mp4 = animation_to_mp4_bytes(anim, params["fps"])
        plt.close(fig)

    components.html(
        f'<div style="background-color: white;">{html}</div>',
        height=1200,
        scrolling=True,
    )
    dl_col_gif, dl_col_mp4 = st.columns(2)
    with dl_col_gif:
        st.download_button(
            label="Download dither-lock animation (GIF)",
            data=dither_lock_gif,
            file_name="pid_dither_lock.gif",
            mime="image/gif",
        )
    with dl_col_mp4:
        st.download_button(
            label="Download dither-lock animation (MP4)",
            data=dither_lock_mp4,
            file_name="pid_dither_lock.mp4",
            mime="video/mp4",
        )
# else:
#     st.info("Adjust parameters in the sidebar, then click **Simulate dither-locking**.")


if create_s_curve_anim_btn or simulate_all_btn:
    with st.spinner("Running simulation and rendering animation..."):
        fig, anim = build_s_curve_animation(params)
        html = anim.to_jshtml()
        s_curve_gif = animation_to_gif_bytes(anim, params["fps"])
        s_curve_mp4 = animation_to_mp4_bytes(anim, params["fps"])
        plt.close(fig)

    components.html(
        f'<div style="background-color: white;">{html}</div>',
        height=1200,
        scrolling=True,
    )
    dl_col_gif, dl_col_mp4 = st.columns(2)
    with dl_col_gif:
        st.download_button(
            label="Download S-curve animation (GIF)",
            data=s_curve_gif,
            file_name="dither_s_curve.gif",
            mime="image/gif",
        )
    with dl_col_mp4:
        st.download_button(
            label="Download S-curve animation (MP4)",
            data=s_curve_mp4,
            file_name="dither_s_curve.mp4",
            mime="video/mp4",
        )

st.divider()

with open(pid_lock_module.__file__, encoding="utf-8") as f:
    code_display = f.read()
with st.expander(label="`pid_lock_module.py`", expanded=False):
    st.code(code_display, language="python")
