import streamlit as st
import tomllib

from johnfeng_photonics.photonic_units import (
    AngularFrequencyUnit,
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)
from johnfeng_photonics.power_units import PowerUnit, TransmissionUnit

st.set_page_config(page_title="Unit Converter", page_icon="🔢", layout="centered")

with open("defaults.toml", "rb") as f:
    defaults = tomllib.load(f)

st.caption("Last updated: 2026-06-27")

st.header("Unit Converter")
st.divider()
st.subheader("$f \\leftrightarrow \\lambda$")

with st.sidebar:
    decimal_places = st.slider("Decimal Places", min_value=0, max_value=6, value=3, step=1)

    step_size = st.radio("Step Size", ["10.0", "1.0", "0.1", "0.01"], index=2, key="step_size_1", horizontal=True)
    step_size = float(step_size)

col1, col2 = st.columns(2)


with col1:
    freq_unit = st.radio("Frequency Unit", ["MHz", "GHz", "THz"], index=1, key="freq_unit_1", horizontal=True)
    freq_input = st.number_input(f"Input Frequency ({freq_unit})", value=defaults["frequency"], step=step_size)

with col2:
    wavelength_unit = st.radio("Wavelength Unit", ["fm", "pm", "nm", "um"], index=2, key="wavelength_unit_1", horizontal=True)
    wavelength_input = st.number_input(f"Input Wavelength ({wavelength_unit})", value=defaults["wavelength"], step=step_size)

with col1:
    freq_unit_enum = FrequencyUnit(freq_unit)
    pu = PhotonicUnit(
        frequency=Frequency(
            value_si=freq_input * freq_unit_enum.si_factor,
            unit=freq_unit_enum,
        )
    )
    pu.wavelength.unit = WavelengthUnit(wavelength_unit)
    st.subheader(f"$\\lambda$ = {pu.wavelength.value_unit:.{decimal_places}f} {pu.wavelength.unit.value}")

with col2:
    wavelength_unit_enum = WavelengthUnit(wavelength_unit)
    pu = PhotonicUnit(
        wavelength=Wavelength(
            value_si=wavelength_input * wavelength_unit_enum.si_factor,
            unit=wavelength_unit_enum,
        )
    )
    pu.frequency.unit = FrequencyUnit(freq_unit)
    pu.angular_frequency.unit = AngularFrequencyUnit.RAD_PER_SEC
    st.subheader(f"$f$ = {pu.frequency.value_unit:.{decimal_places}f} {pu.frequency.unit.value}")
    omega_sci = f"{pu.angular_frequency.value_unit:.{decimal_places}e}"
    st.subheader(f"$\\omega$ = {omega_sci} {pu.angular_frequency.unit.value}")

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("$T[dB] \\leftrightarrow T[\\%]$")
    db_input = st.number_input("$T[dB]$", value=0.0, step=0.1)
    tu = TransmissionUnit(decibel=db_input)
    st.subheader(f"$T$ = {tu.percent.value_unit:.{decimal_places}f}%")

    percent_input = st.number_input("$T[\\%]$", value=100.0, step=0.1)
    tu = TransmissionUnit(percent=percent_input)
    st.subheader(f"$T[dB]$ = {tu.decibel.value_unit:.{decimal_places}f} dB")

with col4:
    st.subheader("$P[mW] \\leftrightarrow P[dBm]$")
    mw_input = st.number_input("Power (mW)", value=1.0, step=0.1)
    pu = PowerUnit(milliwatt=mw_input)
    st.subheader(f"$P[dBm]$ = {pu.decibel_milliwatt.value_unit:.{decimal_places}f} dBm")

    dbm_input = st.number_input("Power (dBm)", value=0.0, step=0.1)
    pu = PowerUnit(decibel_milliwatt=dbm_input)
    st.subheader(f"$P[mW]$ = {pu.milliwatt.value_unit:.{decimal_places}f} mW")
