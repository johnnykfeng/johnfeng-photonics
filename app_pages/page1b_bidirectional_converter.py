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

with open("defaults.toml", "rb") as f:
    defaults = tomllib.load(f)

FREQ_UNITS = ["MHz", "GHz", "THz"]
WVL_UNITS = ["fm", "pm", "nm", "um"]


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
    pu = PhotonicUnit(
        wavelength=Wavelength(value_si=wvl_si, unit=wvl_unit_enum)
    )
    pu.frequency.unit = freq_unit_enum
    st.session_state.bidi_freq_hz = pu.frequency.value_si
    st.session_state.bidi_freq_input = pu.frequency.value_unit
    st.session_state.bidi_wavelength_input = pu.wavelength.value_unit


def _on_freq_unit_change() -> None:
    _refresh_from_hz()


def _on_wavelength_unit_change() -> None:
    _refresh_from_hz()


if "bidi_freq_hz" not in st.session_state:
    pu_init = PhotonicUnit(
        wavelength=Wavelength(
            value_si=defaults["wavelength"] * WavelengthUnit.NANOMETER.si_factor,
            unit=WavelengthUnit.NANOMETER,
        )
    )
    st.session_state.bidi_freq_hz = pu_init.frequency.value_si
    pu_init.frequency.unit = FrequencyUnit.GIGAHERTZ
    pu_init.wavelength.unit = WavelengthUnit.NANOMETER
    st.session_state.bidi_freq_input = pu_init.frequency.value_unit
    st.session_state.bidi_wavelength_input = pu_init.wavelength.value_unit

st.header("Bidirectional $f \\leftrightarrow \\lambda$ Converter")
st.caption(
    "Edit frequency or wavelength — the other field updates to stay in sync."
)
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

col1, col2 = st.columns(2)

with col1:
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
    )

with col2:
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

with col1:
    st.subheader(
        f"$\\lambda$ = {pu.wavelength.value_unit:.{decimal_places}f} {wavelength_unit}"
    )

with col2:
    st.subheader(
        f"$f$ = {pu.frequency.value_unit:.{decimal_places}f} {freq_unit}"
    )
    omega_sci = f"{pu.angular_frequency.value_unit:.{decimal_places}e}"
    st.subheader(f"$\\omega$ = {omega_sci} {pu.angular_frequency.unit.value}")
