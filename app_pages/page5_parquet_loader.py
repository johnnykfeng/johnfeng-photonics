import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Parquet Loader", page_icon="📋", layout="wide")

st.header("Parquet Loader")
st.divider()

st.write("Load a parquet file")
uploaded_file = st.file_uploader("Upload a parquet file", type=["parquet"])
if uploaded_file:
    df = pd.read_parquet(uploaded_file)
else:
    st.warning("No file uploaded")
    st.stop()

with st.expander("View DataFrame", expanded=True):
    st.dataframe(df)

with st.expander("View Columns", expanded=False):
    st.write(df.columns)

with st.expander("View Data Types", expanded=False):
    st.write(df.dtypes)

with st.expander("View Summary", expanded=False):
    st.write(df.describe())

plot_toggle = st.toggle("Plot Transmission", value=True)

if plot_toggle and "wavelength" in df.columns and "transmission" in df.columns:
    cols = st.columns(2)
    fig, ax = plt.subplots()
    if "polarization" in df.columns:
        polarization = df["polarization"].unique()
        if len(polarization) > 1:
            # st.warning("Multiple polarizations found, please select one")
            with cols[0]:
                polarization = st.selectbox("Select polarization", polarization)
        else:
            polarization = polarization[0]
    sub_df = df[df["polarization"] == polarization]
    ax.plot(
        sub_df["wavelength"], 
        sub_df["transmission"], 
        label=polarization,
        linestyle="-",
        linewidth=0.5,
        alpha=0.7,
        )
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Transmission (dB)")
    x_tick_interval = 1 # nm
    ax.xaxis.set_major_locator(plt.MultipleLocator(x_tick_interval))
    ax.tick_params(axis='x', rotation=60)
    y_tick_interval = 2 # dB
    ax.yaxis.set_major_locator(plt.MultipleLocator(y_tick_interval))
    # ax.set_title("Wavelength vs Transmission")
    ax.grid(True, alpha=0.5, linestyle="--", which="both")
    ax.legend()
    st.pyplot(fig)