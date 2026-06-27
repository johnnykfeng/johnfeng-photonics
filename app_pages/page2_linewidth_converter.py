import streamlit as st
import tomllib

from johnfeng_photonics.equations import linewidth_freq_to_wvl, linewidth_wvl_to_freq
from johnfeng_photonics.photonic_units import (
    Frequency,
    FrequencyUnit,
    Wavelength,
    WavelengthUnit,
)

with open("defaults.toml", "rb") as f:
    defaults = tomllib.load(f)

FREQ_UNITS = ["MHz", "GHz", "THz"]
WVL_UNITS = ["fm", "pm", "nm", "um"]

with st.sidebar:
    decimal_places = st.slider("Decimal Places", min_value=0, max_value=6, value=6, step=1)

    step_size = st.radio(
        "Step Size",
        ["10.0", "1.0", "0.1", "0.01"],
        index=2,
        key="step_size_2",
        horizontal=True,
    )
    step_size = float(step_size)

    st.subheader("$\\Delta \\nu \\rightarrow \\Delta \\lambda$")
    freq_unit = st.radio(
        "Frequency Unit",
        FREQ_UNITS,
        index=1,
        key="freq_unit_1",
        horizontal=True,
    )
    center_wavelength_unit_1 = st.radio(
        "Center Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="center_wavelength_unit_1",
        horizontal=True,
    )
    linewidth_wvl_unit_1 = st.radio(
        "Output Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="linewidth_wvl_unit_1",
        horizontal=True,
    )

    st.subheader("$\\Delta \\lambda \\rightarrow \\Delta \\nu$")
    linewidth_wvl_unit_2 = st.radio(
        "Linewidth Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="linewidth_wvl_unit_2",
        horizontal=True,
    )
    center_wavelength_unit_2 = st.radio(
        "Center Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="center_wavelength_unit_2",
        horizontal=True,
    )
    freq_unit_2 = st.radio(
        "Output Frequency Unit",
        FREQ_UNITS,
        index=1,
        key="freq_unit_2",
        horizontal=True,
    )

st.header("Linewidth Converter")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("$\\Delta \\lambda\\ = \\frac{\\lambda_0^2}{c} \\Delta \\nu$")
    linewidth_freq_input = st.number_input(
        f"Linewidth ({freq_unit})",
        value=defaults["linewidth_MHz"],
        step=step_size,
        key="linewidth_freq",
    )
    center_wavelength_input = st.number_input(
        f"Center Wavelength ({center_wavelength_unit_1})",
        value=defaults["wavelength"],
        step=step_size,
        key="center_wavelength_1",
    )

    freq_unit_enum = FrequencyUnit(freq_unit)
    center_wavelength_unit_enum = WavelengthUnit(center_wavelength_unit_1)
    linewidth_freq = Frequency(
        value_si=linewidth_freq_input * freq_unit_enum.si_factor,
        unit=freq_unit_enum,
    )
    center_wavelength = Wavelength(
        value_si=center_wavelength_input * center_wavelength_unit_enum.si_factor,
        unit=center_wavelength_unit_enum,
    )
    linewidth_wvl = linewidth_freq_to_wvl(linewidth_freq, center_wavelength)
    linewidth_wvl.unit = WavelengthUnit(linewidth_wvl_unit_1)
    st.subheader(
        f"$\\Delta \\lambda$ = {linewidth_wvl.value_unit:.{decimal_places}f} {linewidth_wvl.unit.value}"
    )

with col2:
    st.subheader("$\\Delta \\nu\\ = \\frac{c}{\\lambda_0^2} \\Delta \\lambda$")
    linewidth_wvl_input = st.number_input(
        f"Linewidth ({linewidth_wvl_unit_2})",
        value=defaults["linewidth_nm"],
        step=step_size,
        format=f"%.{decimal_places}f",
        key="linewidth_wvl",
    )
    center_wavelength_input = st.number_input(
        f"Center Wavelength ({center_wavelength_unit_2})",
        value=defaults["wavelength"],
        step=step_size,
        key="center_wavelength_2",
    )

    linewidth_wvl_unit_enum = WavelengthUnit(linewidth_wvl_unit_2)
    center_wavelength_unit_enum = WavelengthUnit(center_wavelength_unit_2)
    linewidth_wvl = Wavelength(
        value_si=linewidth_wvl_input * linewidth_wvl_unit_enum.si_factor,
        unit=linewidth_wvl_unit_enum,
    )
    center_wavelength = Wavelength(
        value_si=center_wavelength_input * center_wavelength_unit_enum.si_factor,
        unit=center_wavelength_unit_enum,
    )
    linewidth_freq = linewidth_wvl_to_freq(
        linewidth_wvl,
        center_wavelength,
        freq_unit=FrequencyUnit(freq_unit_2),
    )
    st.subheader(
        f"$\\Delta \\nu$ = {linewidth_freq.value_unit:.{decimal_places}f} {linewidth_freq.unit.value}"
    )
