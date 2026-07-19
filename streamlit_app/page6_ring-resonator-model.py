import streamlit as st
import numpy as np
import plotly.graph_objects as go

from johnfeng_photonics.photonic_units import (
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)

st.set_page_config(page_title="Ring Resonator Model", page_icon="🔄", layout="wide")

st.title("Ring Resonator Model")
# st.divider()

cols = st.columns(2)
with cols[0]:
    # Default resonance frequency for Q calculations (193 THz = telecom wavelength)
    RESONANCE_WAVELENGTH = st.number_input(
        "Resonance Wavelength (nm)", value=1550.0, step=0.1
    )
with cols[1]:
    # OMEGA_M_DEFAULT = 193e12 * 2 * np.pi  # rad/s
    OMEGA_M_DEFAULT = 2 * np.pi * 2.998e8 / (RESONANCE_WAVELENGTH * 1e-9)
    st.write(f"OMEGA_M_DEFAULT: {OMEGA_M_DEFAULT:.2e} rad/s")

# Sidebar for parameter sliders
with st.sidebar:
    st.subheader("Model Parameters")

    # Ring parameters
    st.markdown("### Ring Parameters")
    a = st.slider(
        "$a$ (Ring transmission magnitude)", 0.50, 1.00, 0.950, 0.001, format="%.3f"
    )
    sigma = st.slider(
        "$\\sigma$ (Coupler transmission coefficient)",
        0.50,
        1.00,
        0.900,
        0.001,
        format="%.3f",
    )

    # Frequency parameters
    st.markdown("### Frequency Parameters")
    number_of_points = st.number_input("Number of points", value=10000, step=1)
    f_offset_min_limit = st.number_input(
        "Frequency offset min limit (GHz)", value=-50.0, step=0.1
    )
    f_offset_max_limit = st.number_input(
        "Frequency offset max limit (GHz)", value=50.0, step=0.1
    )
    f_offset_min, f_offset_max = st.slider(
        "Frequency offset range (GHz)",
        f_offset_min_limit,
        f_offset_max_limit,
        (-5.0, 5.0),
        0.1,
        help="Frequency offset range (f - f₀) for plotting",
    )

    f_split = st.slider(
        "f_split (Δf, splitting distance) (GHz)",
        0.0,
        10.0,
        0.0,
        0.01,
        help="Splitting distance between Lorentzian peaks. Used to calculate phi_a = π * (f_split / FSR_ring)",
    )
    f_FSRring = st.slider(
        "FSR_ring (GHz)", 1.0, 100.0, 10.0, 0.1, help="Free spectral range of the ring"
    )
    f_FSRfp = st.slider(
        "FSR_fp (GHz)",
        1.0,
        100.0,
        10.0,
        0.1,
        help="Free spectral range of the Fabry-Pérot cavity",
    )

    # Facet parameters
    st.markdown("### Facet Parameters")
    r = st.slider("r (Facet reflectivity)", 0.01, 0.5, 0.01, 0.01)
    t_fp = st.slider("t_fp (Fabry-Pérot transmission)", 0.5, 1.0, 0.9, 0.01)

    # Phase parameters
    st.markdown("### Phase Parameters")
    delta = st.slider("δ (Phase difference)", 0.0, 2.0 * np.pi, 0.0, 0.1)

    # Insertion loss parameters
    st.markdown("### Insertion Loss")
    IL_t = st.slider("IL_t (Transmission insertion loss)", 0.5, 1.0, 1.0, 0.01)
    IL_r = st.slider("IL_r (Reflection insertion loss)", 0.5, 1.0, 1.0, 0.01)

    # Plot appearance
    st.markdown("### Plot Appearance")
    plot_bgcolor = st.color_picker("Plot background color", value="#0E1117")

# Generate frequency offset range for plotting
f_offset = np.linspace(f_offset_min, f_offset_max, number_of_points)  # GHz (f - f₀)

# Calculate intermediate parameters
# phi_a from user's clarification: phi_a = pi * (f_split / FSR_ring)
# where f_split is the splitting distance (Delta f)
phi_a = np.pi * (f_split / f_FSRring)

# Calculate tau and |rho| from a and phi_a
# From: a = sqrt(tau^2 + |rho|^2) and phi_a = arctan(|rho|/tau)
# tau = a * cos(phi_a), |rho| = a * sin(phi_a)
# phi_a is constant (from splitting distance), so tau and |rho| are constants
tau = a * np.cos(phi_a)
rho_mag = a * np.sin(phi_a)  # |rho|, assuming phi_e = 0 so rho is real

# Ring phase: phi_r = 2*pi * (f_offset / FSR_ring) - varies with frequency offset
phi_r = 2 * np.pi * (f_offset / f_FSRring)

# Calculate a_± = a * e^(±i*phi_a) * e^(i*phi_r)
a_plus = a * np.exp(1j * phi_a) * np.exp(1j * phi_r)
a_minus = a * np.exp(-1j * phi_a) * np.exp(1j * phi_r)

# Fabry-Pérot phase: phi_fp = phi_1 + phi_2
# From the doc: phi_1 + phi_2 = pi * (f - f_0) / FSR_fp + phi_s
# For simplicity, we use: phi_fp = pi * (f_offset / FSR_fp)
phi_fp = np.pi * (f_offset / f_FSRfp)

# Calculate transmission amplitude and effective reflectivity
A_t = IL_t * (1 - r**2) ** 2 * t_fp**4
A_r = IL_r * 1 / r**2
r_e = r * t_fp**2

# Calculate T_full using the simplified equation (line 57)
# T_full = (A_t/4) * |numerator/denominator|^2
# numerator = (1 - sigma*a_+)(sigma - a_-) + (1 - sigma*a_-)(sigma - a_+)
# denominator = (1 - sigma*a_+)(1 - sigma*a_-) + r_e^2*(sigma - a_+)(sigma - a_-)*e^(i*2*phi_fp)
#              - r_e*(1 - sigma^2)*|rho|*e^(i*(phi_r + phi_fp))*2*cos(delta)


def T_full_calculation(sigma, a_plus, a_minus, phi_fp, phi_r, delta, r_e, A_t, rho_mag):
    numerator = (1 - sigma * a_plus) * (sigma - a_minus) + (1 - sigma * a_minus) * (
        sigma - a_plus
    )
    denominator = (
        (1 - sigma * a_plus) * (1 - sigma * a_minus)
        + r_e**2 * (sigma - a_plus) * (sigma - a_minus) * np.exp(1j * 2 * phi_fp)
        - r_e
        * (1 - sigma**2)
        * rho_mag
        * np.exp(1j * (phi_r + phi_fp))
        * 2
        * np.cos(delta)
    )

    return (A_t / 4) * np.abs(numerator / denominator) ** 2


def T_fp_calculation(A_t, r_e, phi_fp):
    numerator = A_t
    denominator = (1 - r_e**2) ** 2 + 4 * r_e**2 * np.cos(phi_fp) ** 2
    return numerator / denominator


def T_minus_calculation(sigma, a_minus, A_t):
    numerator = sigma - a_minus
    denominator = 1 - sigma * a_minus
    return (A_t) * np.abs(numerator / denominator) ** 2


def T_plus_calculation(sigma, a_plus, A_t):
    numerator = sigma - a_plus
    denominator = 1 - sigma * a_plus
    return (A_t) * np.abs(numerator / denominator) ** 2


def R_full_calculation(
    sigma, a_plus, a_minus, phi_fp, phi_r, delta, r_e, A_r, rho_mag, r
):
    """
    Calculate full reflection R_full based on the ring resonator with back reflection model.

    R_full = A_r * |numerator / denominator|^2

    numerator = r^2(1-σa_+)(1-σa_-) + r_e^2(σ-a_+)(σ-a_-)e^{i2φ_fp}
                - r_e(1-σ^2)|ρ|e^{i(φ_r+φ_fp)}(e^{iδ} + r^2 e^{-iδ})
    denominator = (1-σa_+)(1-σa_-) + r_e^2(σ-a_+)(σ-a_-)e^{i2φ_fp}
                  - r_e(1-σ^2)|ρ|e^{i(φ_r+φ_fp)}2cos(δ)
    """
    numerator = (
        r**2 * (1 - sigma * a_plus) * (1 - sigma * a_minus)
        + r_e**2 * (sigma - a_plus) * (sigma - a_minus) * np.exp(1j * 2 * phi_fp)
        - r_e
        * (1 - sigma**2)
        * rho_mag
        * np.exp(1j * (phi_r + phi_fp))
        * (np.exp(1j * delta) + r**2 * np.exp(-1j * delta))
    )
    denominator = (
        (1 - sigma * a_plus) * (1 - sigma * a_minus)
        + r_e**2 * (sigma - a_plus) * (sigma - a_minus) * np.exp(1j * 2 * phi_fp)
        - r_e
        * (1 - sigma**2)
        * rho_mag
        * np.exp(1j * (phi_r + phi_fp))
        * 2
        * np.cos(delta)
    )

    return A_r * np.abs(numerator / denominator) ** 2


# Calculate quality factors
# Delta_omega_FSR = 2*pi*FSR_ring (convert GHz to rad/s)
Delta_omega_FSR = 2 * np.pi * f_FSRring * 1e9  # rad/s

# Use values at resonance (f_split = 0) for Q calculations
# At resonance: phi_a = 0, so tau = a, |rho| = 0
# But we need to use the actual a and sigma values
# Q calculations use natural log, need to handle edge cases
sigma_a = sigma * a
if sigma_a > 0 and sigma_a < 1:
    Q_load = -OMEGA_M_DEFAULT / Delta_omega_FSR * np.pi / np.log(sigma_a)
else:
    Q_load = np.nan

if sigma > 0 and sigma < 1:
    Q_ext = -OMEGA_M_DEFAULT / Delta_omega_FSR * np.pi / np.log(sigma)
else:
    Q_ext = np.nan

if a > 0 and a < 1:
    Q_int = -OMEGA_M_DEFAULT / Delta_omega_FSR * np.pi / np.log(a)
else:
    Q_int = np.nan

# Escape efficiency
if sigma_a > 0 and sigma_a < 1 and sigma > 0 and sigma < 1:
    eta_esc = np.log(sigma) / np.log(sigma_a)
else:
    eta_esc = np.nan


T_full = T_full_calculation(
    sigma, a_plus, a_minus, phi_fp, phi_r, delta, r_e, A_t, rho_mag
)
# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Transmission (T_full)")
    toggle_cols = st.columns(6)
    with toggle_cols[0]:
        dB_toggle = st.checkbox("Show in dB", value=True)
    with toggle_cols[1]:
        include_T_fp = st.checkbox("Include Fabry-Pérot", value=False)
    with toggle_cols[2]:
        include_T_minus = st.checkbox("Include T_minus", value=False)
    with toggle_cols[3]:
        include_T_plus = st.checkbox("Include T_plus", value=False)
    with toggle_cols[4]:
        include_R_full = st.checkbox("Include R_full", value=False)
    with toggle_cols[5]:
        wavelength_x_axis = st.checkbox(
            "X-axis: Wavelength",
            value=False,
            help="Plot against absolute wavelength (nm) instead of frequency offset (GHz)",
        )

    if wavelength_x_axis:
        resonance_pu = PhotonicUnit(
            wavelength=Wavelength(
                value_si=RESONANCE_WAVELENGTH * WavelengthUnit.NANOMETER.si_factor,
                unit=WavelengthUnit.NANOMETER,
            )
        )
        f_abs_hz = resonance_pu.frequency.value_si + f_offset * FrequencyUnit.GIGAHERTZ.si_factor
        x_values_pu = PhotonicUnit(
            frequency=Frequency(value_si=f_abs_hz, unit=FrequencyUnit.HERTZ)
        )
        x_values_pu.wavelength.unit = WavelengthUnit.NANOMETER
        x_values = x_values_pu.wavelength.value_unit
        xaxis_title = "Wavelength [nm]"
        plot_title = "Transmission vs Wavelength"
        hover_x_label = "Wavelength"
        hover_x_unit = "nm"
        hover_x_fmt = ".6f"
    else:
        x_values = f_offset
        xaxis_title = "Frequency Offset (f - f₀) [GHz]"
        plot_title = "Transmission vs Frequency Offset"
        hover_x_label = "Frequency offset"
        hover_x_unit = "GHz"
        hover_x_fmt = ".3f"

    if dB_toggle:
        T_full = 10 * np.log10(T_full)
        yaxis_title = "Transmission (dB)"
        T_min, T_max = st.slider(
            "Transmission range (dB)", -100.0, 0.0, (-10.0, 0.0), 0.1
        )
        if include_T_fp:
            T_fp = 10 * np.log10(T_fp_calculation(A_t, r_e, phi_fp))
        if include_T_minus:
            T_minus = 10 * np.log10(T_minus_calculation(sigma, a_minus, A_t))
        if include_T_plus:
            T_plus = 10 * np.log10(T_plus_calculation(sigma, a_plus, A_t))
        if include_R_full:
            R_full = 10 * np.log10(
                R_full_calculation(
                    sigma, a_plus, a_minus, phi_fp, phi_r, delta, r_e, A_r, rho_mag, r
                )
            )
    else:
        yaxis_title = "Transmission (linear)"
        T_min, T_max = st.slider("Transmission range", 0.0, 1.1, (0.0, 1.1), 0.01)
        if include_T_fp:
            T_fp = T_fp_calculation(A_t, r_e, phi_fp)
        if include_T_minus:
            T_minus = T_minus_calculation(sigma, a_minus, A_t)
        if include_T_plus:
            T_plus = T_plus_calculation(sigma, a_plus, A_t)
        if include_R_full:
            R_full = R_full_calculation(
                sigma, a_plus, a_minus, phi_fp, phi_r, delta, r_e, A_r, rho_mag, r
            )
    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=T_full,
            mode="lines",
            line=dict(color="blue", width=2),
            name="Ring + Fabry-Pérot",
        )
    )
    if include_T_fp:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=T_fp,
                mode="lines",
                line=dict(color="red", width=2),
                name="Fabry-Pérot",
            )
        )
    if include_T_minus:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=T_minus,
                mode="lines",
                line=dict(color="green", width=2, dash="dash"),
                name="T_minus",
            )
        )
    if include_T_plus:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=T_plus,
                mode="lines",
                line=dict(color="orange", width=2, dash="dash"),
                name="T_plus",
            )
        )
    if include_R_full:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=R_full,
                mode="lines",
                line=dict(color="purple", width=2),
                name="Back Reflection",
            )
        )
    fig.update_traces(
        hovertemplate=(
            f"{hover_x_label}: %{{x:{hover_x_fmt}}} {hover_x_unit}"
            "<br>Transmission: %{y:.6f}<extra></extra>"
        )
    )

    fig.update_layout(
        title=plot_title,
        xaxis_title=xaxis_title,
        yaxis_title="Transmission",
        template="plotly_white",
        height=500,
        paper_bgcolor=plot_bgcolor,
        plot_bgcolor=plot_bgcolor,
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
        yaxis_range=[T_min, T_max],
        # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Quality Factors")
    if not np.isnan(Q_load):
        st.metric(
            "Loaded Q",
            f"{Q_load / 1e6:.2f} M",
            help="Q_load = -ω_m/(Δω_FSR) * π/ln(σa)",
        )
    else:
        st.write("Loaded Q: Invalid (check parameters)")

    if not np.isnan(Q_ext):
        st.metric(
            "Extrinsic Q",
            f"{Q_ext / 1e6:.2f} M",
            help="Q_ext = -ω_m/(Δω_FSR) * π/ln(σ)",
        )
    else:
        st.write("Extrinsic Q: Invalid (check parameters)")

    if not np.isnan(Q_int):
        st.metric(
            "Intrinsic Q",
            f"{Q_int / 1e6:.2f} M",
            help="Q_int = -ω_m/(Δω_FSR) * π/ln(a)",
        )
    else:
        st.write("Intrinsic Q: Invalid (check parameters)")

    st.subheader("Escape Efficiency")
    if not np.isnan(eta_esc):
        st.metric(
            "$\\eta_{esc}$",
            f"{eta_esc:.4f}",
            help="$\\eta_{esc} = ln(\\sigma)/ln(\\sigma a)$",
        )
    else:
        st.write("Escape Efficiency: Invalid (check parameters)")
    # st.markdown("### Coupling Condition")
    if eta_esc >= 0.499 and eta_esc <= 0.501:
        st.metric("Coupling Condition", "Critical")
    elif eta_esc > 0.5:
        st.metric("Coupling Condition", "Overcoupled")
    else:
        st.metric("Coupling Condition", "Undercoupled")


st.subheader("Additional Parameters")
st.write(f"**$\\tau$:** {tau:.4f}")
st.write(f"**$|\\rho|$:** {rho_mag:.4f}")
st.write(f"**$\\phi_a$:** {phi_a:.4f} rad ({np.degrees(phi_a):.2f}°)")
st.write(f"**$A_t$:** {A_t:.6f}")
st.write(f"**$r_e$:** {r_e:.4f}")

# Additional information
with st.expander("Model Information", expanded=False):
    st.markdown("""
    This model implements the **Ring Resonator With Back Reflection** transmission model.

    **Key Equations:**
    - $T_{full} = \\frac{A_t}{4} \\left| \\frac{\\text{numerator}}{\\text{denominator}} \\right|^2$
    - $Q_{load, m} = \\frac{\\omega_m}{\\Delta\\omega_{FSR}} \\frac{\\pi}{\\ln(\\sigma a)}$
    - $Q_{ext, m} = \\frac{\\omega_m}{\\Delta\\omega_{FSR}} \\frac{\\pi}{\\ln(\\sigma)}$
    - $Q_{int, m} = \\frac{\\omega_m}{\\Delta\\omega_{FSR}} \\frac{\\pi}{\\ln(a)}$
    - $\\eta_{esc} = \\frac{\\ln(\\sigma)}{\\ln(\\sigma a)}$
    - $A_r = IL_r / r^2$
    - $A_t = IL_t (1-r^2)^2 t_fp^4$

    **Parameters:**
    - **$a$**: Ring transmission magnitude ($|a_{\\pm}| = \\sqrt{\\tau^2 + |\\rho|^2}$)
    - **$\\sigma$**: Coupler transmission coefficient
    - **$f_{split}$**: Splitting distance ($\\Delta f$) between Lorentzian peaks, used to calculate $\\phi_a = \\pi \\times (f_{split} / FSR_{ring})$
    - **$FSR_{ring}$**: Free spectral range of the ring
    - **$FSR_{fp}$**: Free spectral range of the Fabry-Pérot cavity
    - **$r$**: Facet reflectivity
    - **$t_{fp}$**: Fabry-Pérot transmission coefficient
    - **$\\delta$**: Phase difference ($\\phi_d + \\phi_e$)
    - **$IL_t$**: Transmission insertion loss
    - **$IL_r$**: Reflection insertion loss
    """)
