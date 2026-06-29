from typing import Literal

from pydantic import BaseModel, Field


class PhotonicConvertRequest(BaseModel):
    value: float
    from_field: Literal["frequency", "wavelength"] = Field(alias="from")
    freq_unit: str = "GHz"
    wvl_unit: str = "nm"

    model_config = {"populate_by_name": True}


class PhotonicConvertResponse(BaseModel):
    frequency: float
    wavelength: float
    angular_frequency_rad_s: float
    freq_unit: str
    wvl_unit: str


class TransmissionConvertRequest(BaseModel):
    value: float
    from_field: Literal["dB", "percent"] = Field(alias="from")

    model_config = {"populate_by_name": True}


class TransmissionConvertResponse(BaseModel):
    dB: float
    percent: float


class PowerConvertRequest(BaseModel):
    value: float
    from_field: Literal["mW", "dBm"] = Field(alias="from")

    model_config = {"populate_by_name": True}


class PowerConvertResponse(BaseModel):
    mW: float
    dBm: float


class LinewidthConvertRequest(BaseModel):
    value: float
    from_field: Literal["frequency", "wavelength"] = Field(alias="from")
    freq_unit: str = "MHz"
    wvl_unit: str = "nm"
    center_wavelength: float
    center_unit: str = "nm"

    model_config = {"populate_by_name": True}


class LinewidthConvertResponse(BaseModel):
    frequency: float
    wavelength: float
    freq_unit: str
    wvl_unit: str
    center_wavelength: float
    center_unit: str


class DefaultsResponse(BaseModel):
    wavelength: float
    omega: float
    frequency: float
    quality_factor: float
    transmission: float
    power_mW: float
    power_dBm: float
    linewidth_GHz: float
    linewidth_nm: float
    linewidth_MHz: float


class EquationsSourceResponse(BaseModel):
    source: str
