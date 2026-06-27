import numpy as np

from .photonic_units import (
    AngularFrequency,
    AngularFrequencyUnit,
    Frequency,
    FrequencyUnit,
    Wavelength,
)

speed_of_light = 2.998e8  # Speed of light in m/s

_FREQ_UNIT_FACTORS = {
    FrequencyUnit.HERTZ: 1,
    FrequencyUnit.KILOHERTZ: 1e3,
    FrequencyUnit.MEGAHERTZ: 1e6,
    FrequencyUnit.GIGAHERTZ: 1e9,
    FrequencyUnit.TERAHERTZ: 1e12,
}


def _parse_frequency_unit(freq_unit):
    if isinstance(freq_unit, FrequencyUnit):
        return freq_unit
    return FrequencyUnit(freq_unit)


def frequency_to_wavelength(freq):
    """Convert frequency to wavelength.

    Accepts a Frequency object or a float in GHz. Returns Wavelength or nm respectively.
    """
    return_scalar = not isinstance(freq, Frequency)
    if return_scalar:
        freq = Frequency(value_si=freq * 1e9)
    wavelength_m = speed_of_light / freq.value_si
    result = Wavelength(value_si=wavelength_m)
    return result.value_unit if return_scalar else result


def wavelength_to_frequency(wavelength):
    """Convert wavelength to frequency.

    Accepts a Wavelength object or a float in nm. Returns Frequency or GHz respectively.
    """
    return_scalar = not isinstance(wavelength, Wavelength)
    if return_scalar:
        wavelength = Wavelength(value_si=wavelength * 1e-9)
    freq_hz = speed_of_light / wavelength.value_si
    result = Frequency(value_si=freq_hz)
    return result.value_unit if return_scalar else result


def omega_to_wavelength(omega):
    """Convert angular frequency to wavelength.

    Accepts an AngularFrequency object or a float in Trad/s. Returns Wavelength.
    """
    if not isinstance(omega, AngularFrequency):
        omega = AngularFrequency(
            value_si=omega * 1e12, unit=AngularFrequencyUnit.TERA_RAD_PER_SEC
        )
    wavelength_m = 2 * np.pi * speed_of_light / omega.value_si
    return Wavelength(value_si=wavelength_m)


def wavelength_to_omega(wavelength):
    """Convert wavelength to angular frequency.

    Accepts a Wavelength object or a float in nm.
    Returns AngularFrequency or Trad/s respectively.
    """
    return_scalar = not isinstance(wavelength, Wavelength)
    if return_scalar:
        wavelength = Wavelength(value_si=wavelength * 1e-9)
    omega_rad_s = 2 * np.pi * speed_of_light / wavelength.value_si
    result = AngularFrequency(
        value_si=omega_rad_s, unit=AngularFrequencyUnit.TERA_RAD_PER_SEC
    )
    return result.value_unit if return_scalar else result


def dB_to_percent(dB):
    """Convert dB to percentage"""
    return 100 * (10 ** (dB / 10))


def percent_to_dB(percent):
    """Convert percentage to dB"""
    return 10 * np.log10(percent / 100)


def mW_to_dBm(mW):
    """Convert mW to dBm"""
    return 10 * np.log10(mW)


def dBm_to_mW(dBm):
    """Convert dBm to mW"""
    return 10 ** (dBm / 10)


def linewidth_GHz_to_nm(linewidth_ghz, center_wavelength):
    """Convert linewidth from GHz to nm."""
    if not isinstance(center_wavelength, Wavelength):
        center_wavelength = Wavelength(value_si=center_wavelength * 1e-9)
    center_freq = wavelength_to_frequency(center_wavelength)
    half_linewidth_hz = linewidth_ghz * 1e9 / 2
    wavelength_high = frequency_to_wavelength(
        Frequency(value_si=center_freq.value_si + half_linewidth_hz)
    )
    wavelength_low = frequency_to_wavelength(
        Frequency(value_si=center_freq.value_si - half_linewidth_hz)
    )
    return abs(wavelength_high.value_unit - wavelength_low.value_unit)


def linewidth_nm_to_GHz(linewidth_nm, center_wavelength):
    """Convert linewidth from nm to GHz."""
    if not isinstance(center_wavelength, Wavelength):
        center_wavelength = Wavelength(value_si=center_wavelength * 1e-9)
    half_linewidth_si = linewidth_nm * 1e-9 / 2
    freq_high = wavelength_to_frequency(
        Wavelength(value_si=center_wavelength.value_si + half_linewidth_si)
    )
    freq_low = wavelength_to_frequency(
        Wavelength(value_si=center_wavelength.value_si - half_linewidth_si)
    )
    return abs(freq_high.value_unit - freq_low.value_unit)


def linewidth_wvl_to_freq(
    linewidth_wvl, center_wavelength, freq_unit=FrequencyUnit.MEGAHERTZ
):
    """Convert linewidth from wavelength to frequency."""
    return_scalar = not isinstance(linewidth_wvl, Wavelength)
    if return_scalar:
        linewidth_wvl = Wavelength(value_si=linewidth_wvl * 1e-9)
    if not isinstance(center_wavelength, Wavelength):
        center_wavelength = Wavelength(value_si=center_wavelength * 1e-9)
    freq_unit = _parse_frequency_unit(freq_unit)

    freq_hz = linewidth_wvl.value_si * speed_of_light / (center_wavelength.value_si**2)
    result = Frequency(value_si=freq_hz, unit=freq_unit)
    return result.value_unit if return_scalar else result


def linewidth_freq_to_wvl(
    linewidth_freq, center_wavelength, freq_unit=FrequencyUnit.MEGAHERTZ
):
    """Convert linewidth from frequency to wavelength."""
    return_scalar = not isinstance(linewidth_freq, Frequency)
    freq_unit = _parse_frequency_unit(freq_unit)
    if return_scalar:
        linewidth_freq = Frequency(
            value_si=linewidth_freq * _FREQ_UNIT_FACTORS[freq_unit],
            unit=freq_unit,
        )
    if not isinstance(center_wavelength, Wavelength):
        center_wavelength = Wavelength(value_si=center_wavelength * 1e-9)

    linewidth_wvl_m = (
        linewidth_freq.value_si * (center_wavelength.value_si**2) / speed_of_light
    )
    result = Wavelength(value_si=linewidth_wvl_m)
    return result.value_unit if return_scalar else result
