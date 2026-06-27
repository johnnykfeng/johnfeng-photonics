import streamlit as st
import pandas as pd
import numpy as np

from johnfeng_photonics.equations import dBm_to_mW, mW_to_dBm
from johnfeng_photonics.photonic_units import (
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)

FREQ_UNITS = ["MHz", "GHz", "THz"]
WVL_UNITS = ["fm", "pm", "nm", "um"]

st.header("Tables")
st.divider()

with st.sidebar:
    freq_unit = st.radio(
        "Frequency Unit",
        FREQ_UNITS,
        index=2,
        key="table_freq_unit",
        horizontal=True,
    )
    wavelength_unit = st.radio(
        "Wavelength Unit",
        WVL_UNITS,
        index=2,
        key="table_wavelength_unit",
        horizontal=True,
    )

table_choice = st.radio(
    "Select a table",
    [
        "Frequency vs Wavelength",
        "Wavelength vs Frequency",
        "Power (mW) vs Power (dBm)",
        "Power (dBm) vs Power (mW)",
    ],
)
if table_choice == "Frequency vs Wavelength":
    min_value = st.number_input(f"Min Frequency ({freq_unit})", value=188.0)
    max_value = st.number_input(f"Max Frequency ({freq_unit})", value=200.0)
    step_value = st.number_input(f"Step ({freq_unit})", value=1.0)
    freq_range = np.arange(min_value, max_value, step_value)
    freq_unit_enum = FrequencyUnit(freq_unit)
    wavelength_unit_enum = WavelengthUnit(wavelength_unit)
    wavelength_range = []
    for freq_value in freq_range:
        pu = PhotonicUnit(
            frequency=Frequency(
                value_si=freq_value * freq_unit_enum.si_factor,
                unit=freq_unit_enum,
            )
        )
        pu.wavelength.unit = wavelength_unit_enum
        wavelength_range.append(pu.wavelength.value_unit)
    df = pd.DataFrame(
        {
            f"Frequency ({freq_unit})": freq_range,
            f"Wavelength ({wavelength_unit})": wavelength_range,
        }
    )
    st.dataframe(df)
elif table_choice == "Wavelength vs Frequency":
    min_value = st.number_input(f"Min Wavelength ({wavelength_unit})", value=1500.0)
    max_value = st.number_input(f"Max Wavelength ({wavelength_unit})", value=1600.0)
    step_value = st.number_input(f"Step ({wavelength_unit})", value=1.0)
    wavelength_range = np.arange(min_value, max_value, step_value)
    wavelength_unit_enum = WavelengthUnit(wavelength_unit)
    freq_unit_enum = FrequencyUnit(freq_unit)
    freq_range = []
    for wavelength_value in wavelength_range:
        pu = PhotonicUnit(
            wavelength=Wavelength(
                value_si=wavelength_value * wavelength_unit_enum.si_factor,
                unit=wavelength_unit_enum,
            )
        )
        pu.frequency.unit = freq_unit_enum
        freq_range.append(pu.frequency.value_unit)
    df = pd.DataFrame(
        {
            f"Wavelength ({wavelength_unit})": wavelength_range,
            f"Frequency ({freq_unit})": freq_range,
        }
    )
    st.dataframe(df)
elif table_choice == "Power (mW) vs Power (dBm)":
    min_value = st.number_input("Min Power (mW)", value=1.0)
    max_value = st.number_input("Max Power (mW)", value=100.0)
    step_value = st.number_input("Step (mW)", value=1.0)
    mW_range = np.arange(min_value, max_value, step_value)
    dBm_range = [mW_to_dBm(mW) for mW in mW_range]
    df = pd.DataFrame({"Power (mW)": mW_range, "Power (dBm)": dBm_range})
    st.dataframe(df)
elif table_choice == "Power (dBm) vs Power (mW)":
    min_value = st.number_input("Min Power (dBm)", value=0.0)
    max_value = st.number_input("Max Power (dBm)", value=20.0)
    step_value = st.number_input("Step (dBm)", value=1.0)
    dBm_range = np.arange(min_value, max_value, step_value)
    mW_range = [dBm_to_mW(dBm) for dBm in dBm_range]
    df = pd.DataFrame({"Power (dBm)": dBm_range, "Power (mW)": mW_range})
    st.dataframe(df)
