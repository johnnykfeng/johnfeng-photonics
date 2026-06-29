import tomllib

import streamlit as st

from johnfeng_photonics.photonic_units import (
    AngularFrequencyUnit,
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)
from johnfeng_photonics.power_units import PowerUnit, TransmissionUnit

with open("defaults.toml", "rb") as f:
    defaults = tomllib.load(f)

FREQ_UNITS = ["MHz", "GHz", "THz"]
WVL_UNITS = ["fm", "pm", "nm", "um"]

st.caption("Last updated: 2026-06-28")


def _refresh_from_hz() -> PhotonicUnit:
    """Update both input fields from the canonical frequency in Hz."""
    freq_unit_enum = FrequencyUnit(st.session_state.bidi_freq_unit)
    wvl_unit_enum = WavelengthUnit(st.session_state.bidi_wavelength_unit)
    pu = PhotonicUnit(
        frequency=Frequency(
            value_si=st.session_state.bidi_freq_hz,
            unit=freq_unit_enum,
        )
    )
    pu.wavelength.unit = wvl_unit_enum
    st.session_state.bidi_freq_input = pu.frequency.value_unit
    st.session_state.bidi_wavelength_input = pu.wavelength.value_unit
    return pu


def _sync_from_freq() -> None:
    freq_unit_enum = FrequencyUnit(st.session_state.bidi_freq_unit)
    st.session_state.bidi_freq_hz = (
        st.session_state.bidi_freq_input * freq_unit_enum.si_factor
    )
    _refresh_from_hz()


def _sync_from_wavelength() -> None:
    wvl_unit_enum = WavelengthUnit(st.session_state.bidi_wavelength_unit)
    wvl_si = st.session_state.bidi_wavelength_input * wvl_unit_enum.si_factor
    freq_unit_enum = FrequencyUnit(st.session_state.bidi_freq_unit)
    pu = PhotonicUnit(wavelength=Wavelength(value_si=wvl_si, unit=wvl_unit_enum))
    pu.frequency.unit = freq_unit_enum
    st.session_state.bidi_freq_hz = pu.frequency.value_si
    st.session_state.bidi_freq_input = pu.frequency.value_unit
    st.session_state.bidi_wavelength_input = pu.wavelength.value_unit


def _on_freq_unit_change() -> None:
    _refresh_from_hz()


def _on_wavelength_unit_change() -> None:
    _refresh_from_hz()


def _refresh_from_transmission_db() -> TransmissionUnit:
    """Update both input fields from the canonical transmission in dB."""
    tu = TransmissionUnit(decibel=st.session_state.bidi_transmission_db)
    st.session_state.bidi_db_input = tu.decibel.value_unit
    st.session_state.bidi_percent_input = tu.percent.value_unit
    return tu


def _sync_from_transmission_db() -> None:
    st.session_state.bidi_transmission_db = st.session_state.bidi_db_input
    _refresh_from_transmission_db()


def _sync_from_transmission_percent() -> None:
    tu = TransmissionUnit(percent=st.session_state.bidi_percent_input)
    st.session_state.bidi_transmission_db = tu.decibel.value_si
    st.session_state.bidi_db_input = tu.decibel.value_unit
    st.session_state.bidi_percent_input = tu.percent.value_unit


def _refresh_from_power_dbm() -> PowerUnit:
    """Update both input fields from the canonical power in dBm."""
    pu = PowerUnit(decibel_milliwatt=st.session_state.bidi_power_dbm)
    st.session_state.bidi_mw_input = pu.milliwatt.value_unit
    st.session_state.bidi_dbm_input = pu.decibel_milliwatt.value_unit
    return pu


def _sync_from_milliwatt() -> None:
    pu = PowerUnit(milliwatt=st.session_state.bidi_mw_input)
    st.session_state.bidi_power_dbm = pu.decibel_milliwatt.value_si
    st.session_state.bidi_mw_input = pu.milliwatt.value_unit
    st.session_state.bidi_dbm_input = pu.decibel_milliwatt.value_unit


def _sync_from_dbm() -> None:
    st.session_state.bidi_power_dbm = st.session_state.bidi_dbm_input
    _refresh_from_power_dbm()


if "bidi_freq_unit" not in st.session_state:
    st.session_state.bidi_freq_unit = FREQ_UNITS[1]
if "bidi_wavelength_unit" not in st.session_state:
    st.session_state.bidi_wavelength_unit = WVL_UNITS[2]
if "bidi_freq_hz" not in st.session_state:
    pu_init = PhotonicUnit(
        wavelength=Wavelength(
            value_si=defaults["wavelength"] * WavelengthUnit.NANOMETER.si_factor,
            unit=WavelengthUnit.NANOMETER,
        )
    )
    st.session_state.bidi_freq_hz = pu_init.frequency.value_si
    pu_init.frequency.unit = FrequencyUnit(st.session_state.bidi_freq_unit)
    pu_init.wavelength.unit = WavelengthUnit(st.session_state.bidi_wavelength_unit)
    st.session_state.bidi_freq_input = pu_init.frequency.value_unit
    st.session_state.bidi_wavelength_input = pu_init.wavelength.value_unit

if "bidi_transmission_db" not in st.session_state:
    st.session_state.bidi_transmission_db = defaults["transmission"]
    tu_init = TransmissionUnit(decibel=defaults["transmission"])
    st.session_state.bidi_db_input = tu_init.decibel.value_unit
    st.session_state.bidi_percent_input = tu_init.percent.value_unit

if "bidi_power_dbm" not in st.session_state:
    st.session_state.bidi_power_dbm = defaults["power_dBm"]
    pu_init = PowerUnit(decibel_milliwatt=defaults["power_dBm"])
    st.session_state.bidi_mw_input = pu_init.milliwatt.value_unit
    st.session_state.bidi_dbm_input = pu_init.decibel_milliwatt.value_unit

st.header("$f \\leftrightarrow \\lambda$ Converter")
st.caption("Edit frequency or wavelength — the other field updates to stay in sync.")
st.divider()

with st.sidebar:
    decimal_places = st.slider(
        "Decimal Places",
        min_value=0,
        max_value=6,
        value=3,
        step=1,
        key="decimal_places_bidi",
    )
    step_size = st.radio(
        "Step Size",
        ["10.0", "1.0", "0.1", "0.01"],
        index=2,
        key="step_size_bidi",
        horizontal=True,
    )
    step_size = float(step_size)

wvl_col, freq_col = st.columns(2)

with freq_col:
    st.radio(
        "Frequency Unit",
        FREQ_UNITS,
        index=1,
        key="bidi_freq_unit",
        horizontal=True,
        on_change=_on_freq_unit_change,
    )
    st.number_input(
        f"Input Frequency ({st.session_state.bidi_freq_unit})",
        step=step_size,
        key="bidi_freq_input",
        on_change=_sync_from_freq,
        format=f"%.{decimal_places}f",
        min_value=0.0,
    )

with wvl_col:
    st.radio(
        "Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="bidi_wavelength_unit",
        horizontal=True,
        on_change=_on_wavelength_unit_change,
    )
    st.number_input(
        f"Input Wavelength ({st.session_state.bidi_wavelength_unit})",
        step=step_size,
        key="bidi_wavelength_input",
        on_change=_sync_from_wavelength,
        format=f"%.{decimal_places}f",
        min_value=0.0,
    )

freq_unit_enum = FrequencyUnit(st.session_state.bidi_freq_unit)
wvl_unit_enum = WavelengthUnit(st.session_state.bidi_wavelength_unit)
pu = PhotonicUnit(
    frequency=Frequency(
        value_si=st.session_state.bidi_freq_hz,
        unit=freq_unit_enum,
    )
)
pu.wavelength.unit = wvl_unit_enum
pu.angular_frequency.unit = AngularFrequencyUnit.RAD_PER_SEC

freq_unit = st.session_state.bidi_freq_unit
wavelength_unit = st.session_state.bidi_wavelength_unit

with wvl_col:
    st.subheader(
        f"$\\lambda$ = {pu.wavelength.value_unit:.{decimal_places}f} {wavelength_unit}"
    )

with freq_col:
    st.subheader(f"$f$ = {pu.frequency.value_unit:.{decimal_places}f} {freq_unit}")
    omega_sci = f"{pu.angular_frequency.value_unit:.{decimal_places}e}"
    st.subheader(f"$\\omega$ = {omega_sci} {pu.angular_frequency.unit.value}")

st.divider()
st.header("$T[dB] \\leftrightarrow T[\\%]$ Converter")
st.caption(
    "Edit transmission in dB or percent — the other field updates to stay in sync."
)

col_T_db, col_T_percent = st.columns(2)

with col_T_percent:
    st.number_input(
        "$T[\\%]$",
        step=step_size,
        key="bidi_percent_input",
        on_change=_sync_from_transmission_percent,
        min_value=0.0,
        format=f"%.{decimal_places}e" \
            if _refresh_from_transmission_db().percent.value_unit < 0.001 \
            else f"%.{decimal_places}f",
    )

with col_T_db:
    st.number_input(
        "$T[dB]$",
        step=step_size,
        key="bidi_db_input",
        on_change=_sync_from_transmission_db,
        format=f"%.{decimal_places}f",
    )

tu = TransmissionUnit(decibel=st.session_state.bidi_transmission_db)

with col_T_db:
    st.subheader(f"$T[dB]$ = {tu.decibel.value_unit:.{decimal_places}f} dB")

with col_T_percent:
    st.subheader(f"$T$ = {tu.percent.value_unit:.{decimal_places}f}%")

st.divider()
st.header("$P[dBm] \\leftrightarrow P[mW]$ Converter")
st.caption("Edit power in mW or dBm — the other field updates to stay in sync.")

col_P_dbm, col_P_mw = st.columns(2)

with col_P_mw:
    st.number_input(
        "Power (mW)",
        min_value=0.0,
        step=step_size,
        key="bidi_mw_input",
        on_change=_sync_from_milliwatt,
        format=f"%.{decimal_places}e" \
            if _refresh_from_power_dbm().milliwatt.value_unit < 0.001 \
            else f"%.{decimal_places}f",
    )

with col_P_dbm:
    st.number_input(
        "Power (dBm)",
        step=step_size,
        key="bidi_dbm_input",
        on_change=_sync_from_dbm,
        format=f"%.{decimal_places}f",
    )

pu_power = PowerUnit(decibel_milliwatt=st.session_state.bidi_power_dbm)

with col_P_dbm:
    st.subheader(
        f"$P[dBm]$ = {pu_power.decibel_milliwatt.value_unit:.{decimal_places}f} dBm"
    )

with col_P_mw:
    st.subheader(f"$P[mW]$ = {pu_power.milliwatt.value_unit:.{decimal_places}f} mW")
