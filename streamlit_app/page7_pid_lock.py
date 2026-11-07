"""Streamlit app: interactive PID dither-lock simulation.

Run with:
    streamlit run streamlit_pid_lock.py

The animation is rendered directly in the browser via matplotlib's
JS-HTML embedding (``anim.to_jshtml``). GIF and MP4 downloads are
generated in memory on demand via ``anim.save(...)``.
"""

import tempfile
import time
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from matplotlib.animation import FuncAnimation
import johnfeng_photonics.pid_lock_module as pid_lock_module
from johnfeng_photonics.pid_lock_module import (
    cavity_transmission,
    create_simulation,
    animate_s_curve,
)
import matplotlib

matplotlib.use("Agg")  # headless backend, no GUI window

# Allow large inline animations to be embedded as HTML/JS.
plt.rcParams["animation.embed_limit"] = 200  # MB

try:
    import imageio_ffmpeg

    plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass


def show_elapsed_time(started_at):
    """Show how long rendering has taken since a simulate button was clicked.

    Args:
        started_at: ``time.perf_counter`` value captured when the click was handled.
    """
    elapsed_s = time.perf_counter() - started_at
    st.markdown(f"**Elapsed time:** {elapsed_s:.2f} s")


def animation_to_gif_bytes(anim, fps, dpi):
    """Render a FuncAnimation to GIF bytes for st.download_button.

    Args:
        anim: Matplotlib animation to render.
        fps: Playback frame rate passed to ``anim.save``.
        dpi: Resolution passed to ``anim.save``. Lower values draw fewer pixels
            and finish faster.
    """
    with tempfile.NamedTemporaryFile(suffix=".gif") as tmp:
        anim.save(tmp.name, writer="pillow", fps=fps, dpi=dpi)
        tmp.seek(0)
        return tmp.read()


def animation_to_mp4_bytes(anim, fps, dpi):
    """Render a FuncAnimation to MP4 bytes for st.download_button.

    Args:
        anim: Matplotlib animation to render.
        fps: Playback frame rate passed to ``anim.save``.
        dpi: Resolution passed to ``anim.save``. Lower values draw fewer pixels
            and finish faster.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
        anim.save(tmp.name, writer="ffmpeg", fps=fps, dpi=dpi)
        tmp.seek(0)
        return tmp.read()


def _s_curve_figure(p):
    """Build the S-curve figure and the function that draws one sweep step.

    Args:
        p: Simulation parameter dictionary.

    Returns:
        fig: Matplotlib figure with the three S-curve panels.
        draw_frame: Callable that draws sweep index ``i``.
        last_index: Index of the final sweep sample.
        frames: Sweep indices played by the animation.
    """
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
    frames = range(0, len(f_sweep), p["s_curve_step"])

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

    return fig, update, len(f_sweep) - 1, frames


def build_s_curve_animation(p):
    """Build the matplotlib FuncAnimation of the dither S-curve.

    Args:
        p: Simulation parameter dictionary.
    """
    fig, draw_frame, _last_index, frames = _s_curve_figure(p)
    anim = FuncAnimation(
        fig, draw_frame, frames=frames, interval=1000 / p["fps"], blit=False
    )
    return fig, anim


def build_s_curve_final_plot(p):
    """Draw the finished S-curve figure without rendering animation frames.

    The curves include every sweep sample, and the markers sit on the final
    detuning. That is the state the animation reaches at the end of the sweep.

    Args:
        p: Simulation parameter dictionary.
    """
    fig, draw_frame, last_index, _frames = _s_curve_figure(p)
    draw_frame(last_index)
    return fig


def _lock_figure(p):
    """Build the dither-lock figure and the function that draws one time step.

    Args:
        p: Simulation parameter dictionary.

    Returns:
        fig: Matplotlib figure with the three dither-lock panels.
        draw_frame: Callable that draws time index ``i``.
        last_index: Index of the final time sample.
        frames: Time indices played by the animation.
    """
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

    return fig, update, len(t) - 1, frames


def build_animation(p):
    """Build the matplotlib FuncAnimation for the dither-lock response.

    Args:
        p: Simulation parameter dictionary.
    """
    fig, draw_frame, _last_index, frames = _lock_figure(p)
    anim = FuncAnimation(
        fig, draw_frame, frames=frames, interval=1000 / p["fps"], blit=False
    )
    return fig, anim


def build_lock_final_plot(p):
    """Draw the finished dither-lock figure without rendering animation frames.

    The curves include every time sample, and the markers sit on the final
    sample. That is the state the animation reaches at the end of the trace.

    Args:
        p: Simulation parameter dictionary.
    """
    fig, draw_frame, last_index, _frames = _lock_figure(p)
    draw_frame(last_index)
    return fig


# ==========================================
# Streamlit UI
# ==========================================
st.set_page_config(page_title="PID Dither-Lock Simulator", layout="wide")
st.title("PID Dither-Lock Simulator")
st.write(
    "Interactive simulation of a laser frequency locked to a reference cavity "
    "using dither modulation and a PID. Set the parameters and run."
)

with st.expander("Simulation / playback", expanded=False):
    t_total_ms = st.number_input(
        "Total time (ms)",
        value=30.0,
        min_value=1.0,
        step=5.0,
        help="A longer trace stores more dither-lock samples. With the same time step and frame step, that draws more frames and the dither-lock animation renders slower. The S-curve render is unchanged.",
    )
    dt_ms = st.number_input(
        "Time step dt (ms)",
        value=0.01,
        min_value=0.001,
        step=0.005,
        format="%.3f",
        help="A smaller step stores more dither-lock samples. With the same total time and frame step, that draws more frames and the dither-lock animation renders slower. The S-curve render is unchanged.",
    )
    frame_step = st.number_input(
        "Frame step (subsample)",
        value=40,
        min_value=1,
        step=1,
        help="Draws every Nth dither-lock sample. A larger step draws fewer frames, so the dither-lock animation renders faster. The S-curve render is unchanged.",
    )
    s_curve_step = st.number_input(
        "S-curve step size",
        value=8,
        min_value=1,
        step=1,
        help="Draws every Nth frequency point of the S-curve sweep. A larger step draws fewer frames, so the S-curve animation renders faster. The dither-lock render is unchanged.",
    )
    fps = st.number_input(
        "Playback FPS",
        value=10,
        min_value=1,
        max_value=60,
        step=1,
        help="Sets how fast the finished animation plays. The same frames are still drawn, so render time stays about the same.",
    )
    save_dpi = st.number_input(
        "Save DPI",
        value=80,
        min_value=40,
        max_value=200,
        step=10,
        help="Resolution of the GIF or MP4 download. A lower value draws fewer pixels per frame, so the download renders faster. The in-page player is unchanged.",
    )
    download_format = st.radio(
        "Download format",
        options=["None", "GIF", "MP4"],
        index=0,
        horizontal=True,
        help="None is fastest because no download file is encoded. MP4 adds a faster encode than GIF. The in-page player is rendered for every choice.",
    )

with st.sidebar:
    st.header("Cavity")
    cavity_center = st.number_input(
        "Cavity center (MHz)",
        value=0.0,
        step=1.0,
        help="Frequency of the resonance the lock holds. Laser frequency is detuning from 0 MHz, so a nonzero center moves the lock target off zero. Both animations use this center.",
    )
    cavity_fwhm = st.number_input(
        "Cavity FWHM (MHz)",
        value=10.0,
        min_value=0.1,
        step=0.5,
        help="Full width of the Lorentzian resonance. A wider cavity softens the error-signal slope. The dither excursion also grows with this width, because dither amplitude is a fraction of FWHM.",
    )
    cavity_port = st.selectbox(
        "Cavity port",
        options=["return", "through"],
        index=0,
        help="Return inverts the Lorentzian into a reflection dip and flips the sign of the PID correction. Through keeps a transmission peak and applies the correction with the opposite sign.",
    )

    st.header("Dither")
    dither_freq = st.number_input(
        "Dither frequency (Hz)",
        value=5000.0,
        min_value=1.0,
        step=100.0,
        help="Frequency of the sinusoidal frequency modulation. The photodetector signal is mixed with this same tone to make the error signal. A higher frequency packs more modulation cycles into each trace.",
    )
    dither_amp_frac = st.slider(
        "Dither amplitude (fraction of FWHM)",
        min_value=0.01,
        max_value=1.0,
        value=0.2,
        step=0.01,
        help="Peak dither excursion as a fraction of the cavity FWHM. A larger fraction samples more of the resonance and raises the error-signal amplitude until the sweep averages across the peak.",
    )

    st.header("PID")
    Kp = st.number_input(
        "Kp (proportional gain)",
        value=0.5,
        step=0.1,
        format="%.3f",
        help="Multiplies the filtered error and applies that correction as soon as the PID turns on. A larger gain pulls the laser to the cavity faster and can overshoot. The S-curve sweep does not use this gain.",
    )
    Ki = st.number_input(
        "Ki (integral gain)",
        value=50.0,
        step=1.0,
        format="%.3f",
        help="Accumulates the filtered error and removes a steady frequency offset after the PID turns on. A larger gain clears the offset faster and can make the lock oscillate. This simulation has no derivative term.",
    )
    lpf_alpha = st.slider(
        "LPF alpha (low-pass coeff.)",
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
        help="Smoothing on the mixed signal before the PID. A smaller alpha averages longer, so the error signal is quieter and slower. Alpha of 1 passes the mixer output with no filtering. The S-curve uses a full-period average instead of this filter.",
    )
    lock_on_time_ms = st.number_input(
        "PID ON time (ms)",
        value=10.0,
        min_value=0.0,
        step=1.0,
        help="Time when the servo starts correcting the laser. Before this, the laser follows the free-running drift. The gold band on the dither-lock plots marks this window. The S-curve sweep does not use this time.",
    )

    st.header("Laser drift")
    drift_on = st.checkbox(
        "Noise Drift ON",
        value=True,
        help="When checked, the unlocked laser includes the linear drift slope and random-walk noise. When unchecked, the laser stays at the initial offset. The S-curve sweep does not use this drift.",
    )
    drift_offset = st.number_input(
        "Initial offset (MHz)",
        value=10.0,
        step=1.0,
        help="Starting laser frequency detuning. The lock has to pull the laser from this offset to the cavity center. The S-curve sweep does not use this offset.",
    )
    drift_slope = st.number_input(
        "Drift slope (MHz/s)",
        value=50.0,
        step=5.0,
        help="Constant frequency ramp of the unlocked laser, used only while Noise Drift is on. After the PID turns on, the lock has to cancel this ramp. The S-curve sweep does not use this slope.",
    )
    noise_amp = st.number_input(
        "Random-walk noise amplitude",
        value=0.1,
        min_value=0.0,
        step=0.05,
        format="%.3f",
        help="Standard deviation of the frequency step added at each time step, used only while Noise Drift is on. A larger value makes the free-running trace wander more. The S-curve sweep does not use this noise.",
    )
    seed = st.number_input(
        "Random seed",
        value=0,
        min_value=0,
        step=1,
        help="Seed for the random-walk noise, so the same drift trace can be repeated. A different seed draws a different noise realization. It has no effect while Noise Drift is off.",
    )

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
        "s_curve_step": int(s_curve_step),
        "fps": int(fps),
        "save_dpi": int(save_dpi),
    }


lock_anim_col, lock_plot_col = st.columns(2)
with lock_anim_col:
    simulate_dither_lock_btn = st.button(
        "Animate PID dither-locking",
        type="primary",
        width="stretch",
        help="Renders the dither-lock response frame by frame.",
    )
with lock_plot_col:
    show_lock_plot = st.toggle(
        "Show final dither-lock plot",
        value=True,
        help="Shows the finished dither-lock figure and updates it when parameters change. Turn it off to hide the figure. No animation frames are rendered.",
    )

s_curve_anim_col, s_curve_plot_col = st.columns(2)
with s_curve_anim_col:
    create_s_curve_anim_btn = st.button(
        "Animate error signal s-curve",
        type="primary",
        width="stretch",
        help="Renders the error-signal sweep frame by frame.",
    )
with s_curve_plot_col:
    show_s_curve_plot = st.toggle(
        "Show final S-curve plot",
        value=True,
        help="Shows the finished S-curve figure and updates it when parameters change. Turn it off to hide the figure. No animation frames are rendered.",
    )

simulate_all_btn = st.button(
    "Simulate all",
    type="primary",
    help="Renders both animations.",
)

if simulate_dither_lock_btn or create_s_curve_anim_btn or simulate_all_btn:
    render_started = time.perf_counter()

if simulate_dither_lock_btn or simulate_all_btn:
    with st.spinner("Running simulation and rendering animation..."):
        fig, anim = build_animation(params)
        html = anim.to_jshtml()
        if download_format == "GIF":
            dither_lock_download = animation_to_gif_bytes(
                anim, params["fps"], params["save_dpi"]
            )
        elif download_format == "MP4":
            dither_lock_download = animation_to_mp4_bytes(
                anim, params["fps"], params["save_dpi"]
            )
        plt.close(fig)

    show_elapsed_time(render_started)
    components.html(
        f'<div style="background-color: white;">{html}</div>',
        height=1200,
        scrolling=True,
    )
    if download_format == "GIF":
        st.download_button(
            label="Download dither-lock animation (GIF)",
            data=dither_lock_download,
            file_name="pid_dither_lock.gif",
            mime="image/gif",
        )
    elif download_format == "MP4":
        st.download_button(
            label="Download dither-lock animation (MP4)",
            data=dither_lock_download,
            file_name="pid_dither_lock.mp4",
            mime="video/mp4",
        )
if show_lock_plot:
    lock_plot_started = time.perf_counter()
    with st.spinner("Running dither-lock simulation..."):
        lock_fig = build_lock_final_plot(params)
    show_elapsed_time(lock_plot_started)
    st.pyplot(lock_fig)
    plt.close(lock_fig)

if create_s_curve_anim_btn or simulate_all_btn:
    with st.spinner("Running simulation and rendering animation..."):
        fig, anim = build_s_curve_animation(params)
        html = anim.to_jshtml()
        if download_format == "GIF":
            s_curve_download = animation_to_gif_bytes(
                anim, params["fps"], params["save_dpi"]
            )
        elif download_format == "MP4":
            s_curve_download = animation_to_mp4_bytes(
                anim, params["fps"], params["save_dpi"]
            )
        plt.close(fig)

    show_elapsed_time(render_started)
    components.html(
        f'<div style="background-color: white;">{html}</div>',
        height=1200,
        scrolling=True,
    )
    if download_format == "GIF":
        st.download_button(
            label="Download S-curve animation (GIF)",
            data=s_curve_download,
            file_name="dither_s_curve.gif",
            mime="image/gif",
        )
    elif download_format == "MP4":
        st.download_button(
            label="Download S-curve animation (MP4)",
            data=s_curve_download,
            file_name="dither_s_curve.mp4",
            mime="video/mp4",
        )

if show_s_curve_plot:
    s_curve_plot_started = time.perf_counter()
    with st.spinner("Running S-curve simulation..."):
        s_curve_fig = build_s_curve_final_plot(params)
    show_elapsed_time(s_curve_plot_started)
    st.pyplot(s_curve_fig)
    plt.close(s_curve_fig)

st.divider()

with open(pid_lock_module.__file__, encoding="utf-8") as f:
    code_display = f.read()
with st.expander(label="`pid_lock_module.py`", expanded=False):
    st.code(code_display, language="python")
