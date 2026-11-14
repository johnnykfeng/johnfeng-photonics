"""Interactive Pound–Drever–Hall cavity-lock demonstration."""

import tempfile
import time

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from matplotlib.animation import FuncAnimation

import johnfeng_photonics.pdh_lock_module as pdh_lock_module
from johnfeng_photonics.pdh_lock_module import (
    create_simulation,
    pdh_error,
    reflected_power,
    rf_signals,
)

plt.rcParams["animation.embed_limit"] = 200

try:
    import imageio_ffmpeg

    plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass


def show_elapsed_time(started_at):
    st.markdown(f"**Elapsed time:** {time.perf_counter() - started_at:.2f} s")


def animation_to_bytes(animation, file_format, fps, dpi):
    with tempfile.NamedTemporaryFile(suffix=f".{file_format}") as output:
        writer = "pillow" if file_format == "gif" else "ffmpeg"
        animation.save(output.name, writer=writer, fps=fps, dpi=dpi)
        output.seek(0)
        return output.read()


def _s_curve_figure(p):
    center = p["cavity_center"]
    width = p["cavity_fwhm"]
    offset = p["modulation_frequency"]
    top_half_span = offset + 2 * width
    frequency_axis = np.linspace(center - top_half_span, center + top_half_span, 600)
    sweep_axis = np.linspace(center - 2 * width, center + 2 * width, 500)
    error_signal = pdh_error(sweep_axis, p)
    rf_cycles, _, _, _ = rf_signals(center, p)

    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 11))
    fig.suptitle("PDH error signal through a cavity resonance")
    fig.subplots_adjust(bottom=0.07, hspace=0.4)

    ax_top.plot(
        frequency_axis,
        reflected_power(frequency_axis, p),
        color="black",
        lw=2,
        label="Cavity reflected power",
    )
    (carrier_point,) = ax_top.plot(
        [], [], "o", color="green", ms=10, label="Carrier"
    )
    (lower_point,) = ax_top.plot(
        [], [], "o", color="purple", ms=7, label="Lower sideband"
    )
    (upper_point,) = ax_top.plot(
        [], [], "o", color="blue", ms=7, label="Upper sideband"
    )
    ax_top.axvline(center, color="gray", ls="--", alpha=0.5)
    ax_top.set_xlim(frequency_axis[0], frequency_axis[-1])
    ax_top.set_ylim(-0.05, 1.1)
    ax_top.set_xlabel("Optical frequency detuning (MHz)")
    ax_top.set_ylabel("Reflected power")
    ax_top.legend(loc="upper right")
    ax_top.grid(True, alpha=0.3)

    (detector_line,) = ax_mid.plot(
        [], [], color="blue", lw=1.7, label="Reflected detector power"
    )
    (reference_line,) = ax_mid.plot(
        [], [], color="gray", ls="--", lw=1.5, label="Mixer reference"
    )
    (mixed_line,) = ax_mid.plot(
        [], [], color="purple", lw=1.4, label="Mixer product"
    )
    average_line = ax_mid.axhline(
        0, color="red", ls="--", lw=2, label="Averaged PDH error"
    )
    ax_mid.axhline(0, color="gray", lw=1, alpha=0.4)
    ax_mid.set_xlim(rf_cycles[0], rf_cycles[-1])
    ax_mid.set_ylim(-1.8, 1.8)
    ax_mid.set_xlabel("RF cycles")
    ax_mid.set_ylabel("Normalized signal")
    ax_mid.legend(loc="upper right")
    ax_mid.grid(True, alpha=0.3)

    (error_curve,) = ax_bot.plot(
        [], [], color="red", lw=2, label="PDH error S-curve"
    )
    (error_point,) = ax_bot.plot([], [], "o", color="red", ms=8)
    ax_bot.axvline(center, color="blue", ls="--", alpha=0.5, label="Resonance")
    ax_bot.axhline(0, color="gray", ls="--", alpha=0.5)
    error_scale = max(0.01, 1.1 * np.max(np.abs(error_signal)))
    ax_bot.set_xlim(sweep_axis[0], sweep_axis[-1])
    ax_bot.set_ylim(-error_scale, error_scale)
    ax_bot.set_xlabel("Carrier frequency detuning (MHz)")
    ax_bot.set_ylabel("Demodulated error")
    ax_bot.legend(loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    def update(index):
        frequency = sweep_axis[index]
        for point, sideband_offset in (
            (carrier_point, 0),
            (lower_point, -offset),
            (upper_point, offset),
        ):
            component_frequency = frequency + sideband_offset
            point.set_data(
                [component_frequency],
                [reflected_power(component_frequency, p)],
            )

        cycles, detector, reference, mixed = rf_signals(frequency, p)
        detector_line.set_data(cycles, detector)
        reference_line.set_data(cycles, reference)
        mixed_line.set_data(cycles, mixed)
        average_line.set_ydata([error_signal[index], error_signal[index]])
        ax_mid.set_title(f"Reflected RF signal at {frequency - center:+.2f} MHz")

        error_curve.set_data(sweep_axis[: index + 1], error_signal[: index + 1])
        error_point.set_data([frequency], [error_signal[index]])
        return (
            carrier_point,
            lower_point,
            upper_point,
            detector_line,
            reference_line,
            mixed_line,
            average_line,
            error_curve,
            error_point,
        )

    frames = range(0, len(sweep_axis), p["s_curve_step"])
    return fig, update, len(sweep_axis) - 1, frames


def _lock_figure(p):
    t, free_running, locked, filtered_error = create_simulation(p)
    t_ms = t * 1e3
    center = p["cavity_center"]
    width = p["cavity_fwhm"]
    offset = p["modulation_frequency"]
    frequency_half_span = offset + max(
        width,
        np.max(np.abs(free_running - center)),
        np.max(np.abs(locked - center)),
    ) + width
    frequency_axis = np.linspace(
        center - frequency_half_span, center + frequency_half_span, 600
    )

    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 11))
    fig.suptitle("PI locking the laser to a cavity with PDH")
    fig.subplots_adjust(bottom=0.07, hspace=0.4)

    ax_top.plot(
        frequency_axis,
        reflected_power(frequency_axis, p),
        color="black",
        lw=2,
        label="Cavity reflected power",
    )
    (carrier_point,) = ax_top.plot(
        [], [], "o", color="green", ms=10, label="Carrier"
    )
    (lower_point,) = ax_top.plot(
        [], [], "o", color="purple", ms=7, label="Lower sideband"
    )
    (upper_point,) = ax_top.plot(
        [], [], "o", color="blue", ms=7, label="Upper sideband"
    )
    ax_top.axvline(center, color="gray", ls="--", alpha=0.5)
    ax_top.set_xlim(frequency_axis[0], frequency_axis[-1])
    ax_top.set_ylim(-0.05, 1.1)
    ax_top.set_xlabel("Optical frequency detuning (MHz)")
    ax_top.set_ylabel("Reflected power")
    ax_top.legend(loc="upper right")
    ax_top.grid(True, alpha=0.3)

    (free_curve,) = ax_mid.plot(
        [], [], color="gray", ls=":", lw=2, label="Unlocked laser"
    )
    (locked_curve,) = ax_mid.plot(
        [], [], color="green", lw=2, label="Laser frequency"
    )
    (locked_point,) = ax_mid.plot([], [], "o", color="green", ms=8)
    ax_mid.axhline(center, color="black", lw=1, label="Cavity resonance")
    ax_mid.axvspan(
        p["lock_on_time"] * 1e3,
        t_ms[-1],
        color="gold",
        alpha=0.2,
        label="PI ON",
    )
    freq_lo = min(free_running.min(), locked.min(), center)
    freq_hi = max(free_running.max(), locked.max(), center)
    freq_pad = max(0.5, 0.1 * (freq_hi - freq_lo))
    ax_mid.set_xlim(t_ms[0], t_ms[-1])
    ax_mid.set_ylim(freq_lo - freq_pad, freq_hi + freq_pad)
    ax_mid.set_xlabel("Time (ms)")
    ax_mid.set_ylabel("Laser frequency (MHz)")
    ax_mid.legend(loc="upper right")
    ax_mid.grid(True, alpha=0.3)

    (error_curve,) = ax_bot.plot(
        [], [], color="red", lw=2, label="Filtered PDH error"
    )
    (error_point,) = ax_bot.plot([], [], "o", color="red", ms=8)
    ax_bot.axhline(0, color="gray", ls="--", alpha=0.5)
    ax_bot.axvspan(
        p["lock_on_time"] * 1e3,
        t_ms[-1],
        color="gold",
        alpha=0.2,
        label="PI ON",
    )
    error_scale = max(0.01, 1.1 * np.max(np.abs(filtered_error)))
    ax_bot.set_xlim(t_ms[0], t_ms[-1])
    ax_bot.set_ylim(-error_scale, error_scale)
    ax_bot.set_xlabel("Time (ms)")
    ax_bot.set_ylabel("Filtered error")
    ax_bot.legend(loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    def update(index):
        frequency = locked[index]
        for point, sideband_offset in (
            (carrier_point, 0),
            (lower_point, -offset),
            (upper_point, offset),
        ):
            component_frequency = frequency + sideband_offset
            point.set_data(
                [component_frequency],
                [reflected_power(component_frequency, p)],
            )
        free_curve.set_data(t_ms[: index + 1], free_running[: index + 1])
        locked_curve.set_data(t_ms[: index + 1], locked[: index + 1])
        locked_point.set_data([t_ms[index]], [frequency])
        ax_mid.set_title(f"PI response at t = {t_ms[index]:.2f} ms")
        error_curve.set_data(t_ms[: index + 1], filtered_error[: index + 1])
        error_point.set_data([t_ms[index]], [filtered_error[index]])
        return (
            carrier_point,
            lower_point,
            upper_point,
            free_curve,
            locked_curve,
            locked_point,
            error_curve,
            error_point,
        )

    frames = range(0, len(t), p["frame_step"])
    return fig, update, len(t) - 1, frames


def build_animation(figure_builder, p):
    fig, draw_frame, _last_index, frames = figure_builder(p)
    animation = FuncAnimation(
        fig, draw_frame, frames=frames, interval=1000 / p["fps"], blit=False
    )
    return fig, animation


def build_final_plot(figure_builder, p):
    fig, draw_frame, last_index, _frames = figure_builder(p)
    draw_frame(last_index)
    return fig


def show_animation(figure_builder, p, name, download_format):
    started_at = time.perf_counter()
    with st.spinner(f"Rendering {name} animation..."):
        fig, animation = build_animation(figure_builder, p)
        html = animation.to_jshtml()
        if download_format != "None":
            extension = download_format.lower()
            download = animation_to_bytes(
                animation, extension, p["fps"], p["save_dpi"]
            )
        plt.close(fig)
    show_elapsed_time(started_at)
    components.html(
        f'<div style="background-color: white;">{html}</div>',
        height=1200,
        scrolling=True,
    )
    if download_format != "None":
        st.download_button(
            label=f"Download {name} animation ({download_format})",
            data=download,
            file_name=f"pdh_{name.replace(' ', '_')}.{extension}",
            mime="image/gif" if extension == "gif" else "video/mp4",
        )


def show_final_plot(figure_builder, p, name):
    started_at = time.perf_counter()
    with st.spinner(f"Running {name} simulation..."):
        fig = build_final_plot(figure_builder, p)
    show_elapsed_time(started_at)
    st.pyplot(fig)
    plt.close(fig)


st.set_page_config(page_title="Pound–Drever–Hall Lock Simulator", layout="wide")
st.title("Pound–Drever–Hall Lock Simulator")
st.write(
    "Phase-modulate a laser, reflect its carrier and sidebands from a cavity, "
    "demodulate the photodetector signal, and use the resulting error to lock "
    "the laser frequency."
)

with st.expander("Simulation / playback", expanded=False):
    t_total_ms = st.number_input(
        "Total time (ms)", value=30.0, min_value=1.0, step=5.0
    )
    dt_ms = st.number_input(
        "Time step dt (ms)",
        value=0.01,
        min_value=0.001,
        step=0.005,
        format="%.3f",
        help="The RF tone is averaged analytically; dt only samples the slower PI loop.",
    )
    frame_step = st.number_input(
        "Frame step (subsample)", value=40, min_value=1, step=1
    )
    s_curve_step = st.number_input(
        "S-curve step size", value=8, min_value=1, step=1
    )
    fps = st.number_input(
        "Playback FPS", value=10, min_value=1, max_value=60, step=1
    )
    save_dpi = st.number_input(
        "Save DPI", value=80, min_value=40, max_value=200, step=10
    )
    download_format = st.radio(
        "Download format", ["None", "GIF", "MP4"], horizontal=True
    )

with st.sidebar:
    st.header("Cavity")
    cavity_center = st.number_input(
        "Cavity center (MHz)", value=0.0, step=1.0
    )
    cavity_fwhm = st.number_input(
        "Cavity FWHM (MHz)",
        value=10.0,
        min_value=0.1,
        step=0.5,
        help="Full width of the reflected-power dip.",
    )

    st.header("PDH modulation")
    modulation_frequency = st.number_input(
        "Modulation frequency (MHz)",
        value=30.0,
        min_value=0.1,
        step=1.0,
        help="Optical frequency offset of each sideband from the carrier. "
        "A value above the cavity linewidth keeps the sidebands mostly reflected.",
    )
    modulation_index = st.slider(
        "Phase modulation index (rad)",
        min_value=0.05,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Sets the carrier and first-sideband amplitudes.",
    )
    demod_phase_deg = st.slider(
        "Demodulation phase (degrees)",
        min_value=-90,
        max_value=90,
        value=0,
        step=5,
        help="Rotates the mixer reference. Zero degrees selects the usual "
        "dispersive PDH error for this model.",
    )

    st.header("PI")
    Kp = st.number_input(
        "Kp (proportional gain)",
        value=6000.0,
        min_value=0.0,
        step=500.0,
        help="Proportional correction rate in MHz/s per unit filtered error.",
    )
    Ki = st.number_input(
        "Ki (integral gain)",
        value=50000.0,
        min_value=0.0,
        step=5000.0,
        help="Integral correction rate in MHz/s² per unit accumulated error.",
    )
    filter_time_ms = st.number_input(
        "Error filter time (ms)",
        value=0.3,
        min_value=0.001,
        step=0.1,
        format="%.3f",
        help="Low-pass time constant for the demodulated error envelope.",
    )
    lock_on_time_ms = st.number_input(
        "PI ON time (ms)", value=10.0, min_value=0.0, step=1.0
    )

    st.header("Laser drift")
    drift_on = st.checkbox("Noise Drift ON", value=True)
    drift_offset = st.number_input(
        "Initial offset (MHz)", value=10.0, step=1.0
    )
    drift_slope = st.number_input(
        "Drift slope (MHz/s)", value=50.0, step=5.0
    )
    noise_amp = st.number_input(
        "Random-walk noise amplitude",
        value=0.03,
        min_value=0.0,
        step=0.01,
        format="%.3f",
        help="Standard deviation of each frequency step in MHz.",
    )
    seed = st.number_input("Random seed", value=0, min_value=0, step=1)

params = {
    "cavity_center": cavity_center,
    "cavity_fwhm": cavity_fwhm,
    "modulation_frequency": modulation_frequency,
    "modulation_index": modulation_index,
    "demod_phase_deg": demod_phase_deg,
    "Kp": Kp,
    "Ki": Ki,
    "filter_time": filter_time_ms * 1e-3,
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

if params["dt"] >= params["t_total"]:
    st.error("Total time must be greater than the time step.")
    st.stop()

lock_anim_col, lock_plot_col = st.columns(2)
with lock_anim_col:
    animate_lock = st.button(
        "Animate PI PDH-locking", type="primary", width="stretch"
    )
with lock_plot_col:
    show_lock_plot = st.toggle(
        "Show final PDH-lock plot", value=True
    )

s_curve_anim_col, s_curve_plot_col = st.columns(2)
with s_curve_anim_col:
    animate_s_curve = st.button(
        "Animate error signal S-curve", type="primary", width="stretch"
    )
with s_curve_plot_col:
    show_s_curve_plot = st.toggle(
        "Show final S-curve plot", value=True
    )

simulate_all = st.button("Simulate all", type="primary")

if animate_lock or simulate_all:
    show_animation(_lock_figure, params, "PDH lock", download_format)
if show_lock_plot:
    show_final_plot(_lock_figure, params, "PDH lock")

if animate_s_curve or simulate_all:
    show_animation(_s_curve_figure, params, "S-curve", download_format)
if show_s_curve_plot:
    show_final_plot(_s_curve_figure, params, "S-curve")

st.divider()
with st.expander("PDH model and assumptions", expanded=False):
    st.write(
        "The cavity is modeled as a critically coupled reflection dip. "
        "The optical field contains the carrier and first phase-modulation "
        "sidebands. The photodetector RF beat is mixed and averaged to form "
        "the signed PDH error. The PI controller acts on that averaged signal; "
        "this demonstration omits higher-order sidebands and detector noise."
    )
with st.expander("`pdh_lock_module.py`", expanded=False):
    with open(pdh_lock_module.__file__, encoding="utf-8") as source:
        st.code(source.read(), language="python")
