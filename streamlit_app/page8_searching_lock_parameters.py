import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from johnfeng_photonics.pid_lock_module import animate_s_curve


def _fmt_value(value):
    if abs(value) >= 1000:
        return f"{value:,.1f}"
    if abs(value) >= 1:
        return f"{value:.3f}"
    return f"{value:.4f}"


def _build_sweep_values(start, stop, steps):
    if steps <= 1:
        return np.array([start], dtype=float)
    return np.linspace(start, stop, steps, dtype=float)


def _plot_scurve_sweep(base_params, sweep_param, sweep_values):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = plt.cm.viridis(np.linspace(0.1, 0.95, len(sweep_values)))

    for color, sweep_value in zip(colors, sweep_values):
        run_params = dict(base_params)
        run_params[sweep_param] = float(sweep_value)
        f_sweep, _, error_signal = animate_s_curve(run_params)
        label = f"{sweep_param}={_fmt_value(sweep_value)}"
        ax.plot(f_sweep, error_signal, color=color, lw=2, label=label)

    ax.axhline(0.0, color="gray", linestyle="--", linewidth=1, alpha=0.55)
    ax.axvline(base_params["cavity_center"], color="black", linestyle=":", linewidth=1.2, alpha=0.65)
    ax.set_title(f"S-curve sweep of `{sweep_param}`")
    ax.set_xlabel("Laser Frequency Detuning (MHz)")
    ax.set_ylabel("Demodulated Error Signal")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Sweep value", fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)
    fig.tight_layout()
    return fig


st.set_page_config(page_title="S-curve Parameter Sweep", layout="wide")
st.title("Search Lock Parameters (Static S-curves)")
st.write(
    "Sweep one parameter at a time and overlay all static S-curves from "
    "`animate_s_curve` for quick comparison."
)

with st.sidebar:
    st.header("Base cavity / demod settings")
    cavity_center = st.number_input("Cavity center (MHz)", value=0.0, step=1.0)
    cavity_fwhm = st.number_input("Cavity FWHM (MHz)", value=10.0, min_value=0.1, step=0.5)
    cavity_port = st.selectbox("Cavity port", options=["return", "through"], index=0)

    dither_freq = st.number_input("Base dither frequency (Hz)", value=5000.0, min_value=1.0, step=100.0)
    dither_amp = st.number_input("Base dither amplitude (MHz)", value=2.0, min_value=0.001, step=0.1)

    st.header("Sweep controls")
    sweep_param = st.selectbox(
        "Sweep parameter",
        options=["dither_amp", "cavity_fwhm", "dither_freq"],
        index=0,
        help="All non-swept parameters stay fixed to the base values above.",
    )

    default_ranges = {
        "dither_freq": (2000.0, 12000.0),
        "dither_amp": (0.2, 6.0),
        "cavity_fwhm": (2.0, 20.0),
    }
    default_start, default_stop = default_ranges[sweep_param]
    default_step_size = 6

    sweep_start = st.number_input("Sweep start", value=float(default_start))
    sweep_stop = st.number_input("Sweep stop", value=float(default_stop))
    sweep_steps = st.slider("Number of curves", min_value=2, max_value=20, value=default_step_size)

base_params = {
    "cavity_center": cavity_center,
    "cavity_fwhm": cavity_fwhm,
    "cavity_port": cavity_port,
    "dither_freq": dither_freq,
    "dither_amp": dither_amp,
}

if sweep_start == sweep_stop:
    st.warning("`Sweep start` and `Sweep stop` are equal. Increase the range to compare multiple curves.")
else:
    sweep_values = _build_sweep_values(sweep_start, sweep_stop, sweep_steps)
    fig = _plot_scurve_sweep(base_params, sweep_param, sweep_values)
    st.pyplot(fig, clear_figure=True, width='stretch')