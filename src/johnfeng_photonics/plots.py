import plotly.graph_objects as go
from .equations import (
    dBm_to_mW,
    frequency_to_wavelength,
    mW_to_dBm,
    wavelength_to_frequency,
)


def frequency_vs_wavelength_plot(freq_range_ghz):
    """Plot frequency vs wavelength relationship (using Plotly)"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=freq_range_ghz,
            y=frequency_to_wavelength(freq_range_ghz),
            mode="lines",
            line=dict(color="blue", width=2),
        )
    )
    fig.update_traces(
        hovertemplate="Frequency: %{x:.3f} GHz<br>"
        + "Wavelength: %{y:.3f} nm<extra></extra>"
    )
    fig.update_layout(
        title="Frequency vs Wavelength",
        xaxis_title="Frequency (GHz)",
        yaxis_title="Wavelength (nm)",
        template="plotly_white",
    )
    return fig


def wavelength_vs_frequency_plot(wavelength_range_nm):
    """Plot wavelength vs frequency relationship (using Plotly)"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=wavelength_range_nm,
            y=wavelength_to_frequency(wavelength_range_nm),
            mode="lines",
            line=dict(color="red", width=2),
        )
    )
    fig.update_traces(
        hovertemplate="Wavelength: %{x:.3f} nm<br>"
        + "Frequency: %{y:.3f} GHz<extra></extra>"
    )
    fig.update_layout(
        title="Wavelength vs Frequency",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Frequency (GHz)",
        template="plotly_white",
    )
    return fig


def mW_vs_dBm_plot(mW_range):
    """Plot mW vs dBm relationship (using Plotly)"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=mW_range,
            y=mW_to_dBm(mW_range),
            mode="lines",
            line=dict(color="green", width=2),
        )
    )
    fig.update_traces(
        hovertemplate="mW: %{x:.3f} mW<br>" + "dBm: %{y:.3f} dBm<extra></extra>"
    )
    fig.update_layout(
        title="mW vs dBm", xaxis_title="mW", yaxis_title="dBm", template="plotly_white"
    )
    return fig


def dBm_vs_mW_plot(dBm_range):
    """Plot dBm vs mW relationship (using Plotly)"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dBm_range,
            y=dBm_to_mW(dBm_range),
            mode="lines",
            line=dict(color="purple", width=2),
        )
    )
    fig.update_traces(
        hovertemplate="dBm: %{x:.3f} dBm<br>" + "mW: %{y:.3f} mW<extra></extra>"
    )
    fig.update_layout(
        title="dBm vs mW", xaxis_title="dBm", yaxis_title="mW", template="plotly_white"
    )
    return fig
