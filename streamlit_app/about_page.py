import streamlit as st
from pathlib import Path

st.header("About Photonics Helper")
st.markdown("""
This Streamlit app provides common photonics calculations and visualizations.

### Default Units:
- **Wavelength**: nm (nanometers) or 1e-9 m
- **Angular Frequency (ω)**: Trad/s (tera-radians per second) or 1e12 rad/s
- **Frequency (f)**: GHz (gigahertz) or 1e9 Hz
- **Quality Factor (Q)**: M (millions)
- **Transmission/Loss**: dB (decibels)
- **Power**: mW (milliwatts) or dBm

### Features:
- Unit conversions between frequency, wavelength, and angular frequency
- Power conversions between mW and dBm
- Transmission conversions between dB and percentage
- Linewidth conversions between GHz and nm
- Interactive plotting tools for frequency-wavelength relationships
- Sample transmission plots

### Physics Constants:
- Speed of light: c = 2.998 × 10⁸ m/s
""")

with st.expander("Equations", expanded=False):
    st.markdown(
        """
        $\\omega = \\frac{2 \\pi c}{\\lambda}$\n
        $\\lambda = \\frac{2 \\pi c}{\\omega}$\n
        $\\nu = \\frac{c}{\\lambda}$\n
        $\\lambda = \\frac{c}{\\nu}$\n
        $T[dB] = 10 \\log_{10} \\left(\\frac{P_{out}}{P_{in}}\\right)$\n
        $T[\\%] = 100 \\left(\\frac{P_{out}}{P_{in}}\\right)$\n
        $P_{dBm} = 10 \\log_{10} (P_{mW})$\n
        $P_{mW} = 10^{\\frac{P_{dBm}}{10}}$\n
        $\\Delta \\lambda = \\frac{\\lambda_0^2}{c} \\Delta \\nu$\n
        $\\Delta \\nu = \\frac{c}{\\lambda_0^2} \\Delta \\lambda$\n
        """
    )


def read_py_file_pathlib(filename):
    """
    Reads the contents of a Python file into a string using pathlib.
    """
    try:
        # Create a Path object and use the read_text() method
        file_content = Path(filename).read_text(encoding="utf-8")
        return file_content
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


code_string = read_py_file_pathlib("equations.py")

with st.expander("Python Conversion functions", expanded=False):
    st.code(code_string)
