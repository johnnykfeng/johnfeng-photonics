import streamlit as st
import numpy as np
import plotly.graph_objects as go

from johnfeng_photonics.plots import dBm_vs_mW_plot, mW_vs_dBm_plot
from johnfeng_photonics.photonic_units import (
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)

FREQ_UNITS = ["MHz", "GHz", "THz"]
WVL_UNITS = ["fm", "pm", "nm", "um"]

with st.sidebar:
    freq_unit = st.radio(
        "Frequency Unit",
        FREQ_UNITS,
        index=1,
        key="plot_freq_unit",
        horizontal=True,
    )
    wavelength_unit = st.radio(
        "Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="plot_wavelength_unit",
        horizontal=True,
    )

with st.expander("mW vs dBm", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        mW_min = st.number_input("Min mW", value=1.0)
    with col2:
        mW_max = st.number_input("Max mW", value=100.0)

    mW_range = np.linspace(mW_min, mW_max, 1000)
    fig = mW_vs_dBm_plot(mW_range)
    st.plotly_chart(fig)

with st.expander("dBm vs mW", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        dBm_min = st.number_input("Min dBm", value=0.0)
    with col2:
        dBm_max = st.number_input("Max dBm", value=20.0)

    dBm_range = np.linspace(dBm_min, dBm_max, 1000)
    fig = dBm_vs_mW_plot(dBm_range)
    st.plotly_chart(fig)

with st.expander("Wavelength vs Frequency", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        wavelength_min = st.number_input(
            f"Min Wavelength ({wavelength_unit})",
            value=1500.0,
        )
    with col2:
        wavelength_max = st.number_input(
            f"Max Wavelength ({wavelength_unit})",
            value=1600.0,
        )

    wavelength_range = np.linspace(wavelength_min, wavelength_max, 1000)
    wavelength_unit_enum = WavelengthUnit(wavelength_unit)
    freq_unit_enum = FrequencyUnit(freq_unit)
    freq_values = []
    for wavelength_value in wavelength_range:
        pu = PhotonicUnit(
            wavelength=Wavelength(
                value_si=wavelength_value * wavelength_unit_enum.si_factor,
                unit=wavelength_unit_enum,
            )
        )
        pu.frequency.unit = freq_unit_enum
        freq_values.append(pu.frequency.value_unit)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=wavelength_range,
            y=freq_values,
            mode="lines",
            line=dict(color="red", width=2),
        )
    )
    fig.update_traces(
        hovertemplate=(
            f"Wavelength: %{{x:.3f}} {wavelength_unit}<br>"
            f"Frequency: %{{y:.3f}} {freq_unit}<extra></extra>"
        )
    )
    fig.update_layout(
        title="Wavelength vs Frequency",
        xaxis_title=f"Wavelength ({wavelength_unit})",
        yaxis_title=f"Frequency ({freq_unit})",
        template="plotly_white",
    )
    st.plotly_chart(fig)

with st.expander("Frequency vs Wavelength", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        freq_min = st.number_input(f"Min Frequency ({freq_unit})", value=1e5)
    with col2:
        freq_max = st.number_input(f"Max Frequency ({freq_unit})", value=5e5)

    freq_range = np.linspace(freq_min, freq_max, 1000)
    freq_unit_enum = FrequencyUnit(freq_unit)
    wavelength_unit_enum = WavelengthUnit(wavelength_unit)
    wavelength_values = []
    for freq_value in freq_range:
        pu = PhotonicUnit(
            frequency=Frequency(
                value_si=freq_value * freq_unit_enum.si_factor,
                unit=freq_unit_enum,
            )
        )
        pu.wavelength.unit = wavelength_unit_enum
        wavelength_values.append(pu.wavelength.value_unit)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=freq_range,
            y=wavelength_values,
            mode="lines",
            line=dict(color="blue", width=2),
        )
    )
    fig.update_traces(
        hovertemplate=(
            f"Frequency: %{{x:.3f}} {freq_unit}<br>"
            f"Wavelength: %{{y:.3f}} {wavelength_unit}<extra></extra>"
        )
    )
    fig.update_layout(
        title="Frequency vs Wavelength",
        xaxis_title=f"Frequency ({freq_unit})",
        yaxis_title=f"Wavelength ({wavelength_unit})",
        template="plotly_white",
    )
    st.plotly_chart(fig)
