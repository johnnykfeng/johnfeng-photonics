from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from api.schemas import (
    LinewidthConvertRequest,
    LinewidthConvertResponse,
    PhotonicConvertRequest,
    PhotonicConvertResponse,
    PowerConvertRequest,
    PowerConvertResponse,
    TransmissionConvertRequest,
    TransmissionConvertResponse,
)
from johnfeng_photonics.linewidth_units import LinewidthUnit
from johnfeng_photonics.photonic_units import (
    AngularFrequencyUnit,
    Frequency,
    FrequencyUnit,
    PhotonicUnit,
    Wavelength,
    WavelengthUnit,
)
from johnfeng_photonics.power_units import PowerUnit, TransmissionUnit

router = APIRouter(prefix="/convert", tags=["convert"])


def _validation_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/photonic", response_model=PhotonicConvertResponse)
def convert_photonic(body: PhotonicConvertRequest) -> PhotonicConvertResponse:
    try:
        freq_unit_enum = FrequencyUnit(body.freq_unit)
        wvl_unit_enum = WavelengthUnit(body.wvl_unit)

        if body.from_field == "frequency":
            pu = PhotonicUnit(
                frequency=Frequency(
                    value_si=body.value * freq_unit_enum.si_factor,
                    unit=freq_unit_enum,
                )
            )
        else:
            pu = PhotonicUnit(
                wavelength=Wavelength(
                    value_si=body.value * wvl_unit_enum.si_factor,
                    unit=wvl_unit_enum,
                )
            )

        pu.frequency.unit = freq_unit_enum
        pu.wavelength.unit = wvl_unit_enum
        pu.angular_frequency.unit = AngularFrequencyUnit.RAD_PER_SEC

        return PhotonicConvertResponse(
            frequency=float(pu.frequency.value_unit),
            wavelength=float(pu.wavelength.value_unit),
            angular_frequency_rad_s=float(pu.angular_frequency.value_unit),
            freq_unit=body.freq_unit,
            wvl_unit=body.wvl_unit,
        )
    except (ValidationError, ValueError, TypeError) as exc:
        raise _validation_error(exc) from exc


@router.post("/transmission", response_model=TransmissionConvertResponse)
def convert_transmission(
    body: TransmissionConvertRequest,
) -> TransmissionConvertResponse:
    try:
        if body.from_field == "dB":
            tu = TransmissionUnit(decibel=body.value)
        else:
            tu = TransmissionUnit(percent=body.value)

        return TransmissionConvertResponse(
            dB=float(tu.decibel.value_unit),
            percent=float(tu.percent.value_unit),
        )
    except (ValidationError, ValueError, TypeError) as exc:
        raise _validation_error(exc) from exc


@router.post("/power", response_model=PowerConvertResponse)
def convert_power(body: PowerConvertRequest) -> PowerConvertResponse:
    try:
        if body.from_field == "mW":
            pu = PowerUnit(milliwatt=body.value)
        else:
            pu = PowerUnit(decibel_milliwatt=body.value)

        return PowerConvertResponse(
            mW=float(pu.milliwatt.value_unit),
            dBm=float(pu.decibel_milliwatt.value_unit),
        )
    except (ValidationError, ValueError, TypeError) as exc:
        raise _validation_error(exc) from exc


@router.post("/linewidth", response_model=LinewidthConvertResponse)
def convert_linewidth(body: LinewidthConvertRequest) -> LinewidthConvertResponse:
    try:
        freq_unit_enum = FrequencyUnit(body.freq_unit)
        wvl_unit_enum = WavelengthUnit(body.wvl_unit)
        center_unit_enum = WavelengthUnit(body.center_unit)

        center_wavelength = Wavelength(
            value_si=body.center_wavelength * center_unit_enum.si_factor,
            unit=center_unit_enum,
        )

        if body.from_field == "frequency":
            linewidth = LinewidthUnit(
                frequency=Frequency(
                    value_si=body.value * freq_unit_enum.si_factor,
                    unit=freq_unit_enum,
                ),
                center_wavelength=center_wavelength,
            )
            linewidth.wavelength.unit = wvl_unit_enum
        else:
            linewidth = LinewidthUnit(
                wavelength=Wavelength(
                    value_si=body.value * wvl_unit_enum.si_factor,
                    unit=wvl_unit_enum,
                ),
                center_wavelength=center_wavelength,
            )
            linewidth.frequency.unit = freq_unit_enum

        return LinewidthConvertResponse(
            frequency=float(linewidth.frequency.value_unit),
            wavelength=float(linewidth.wavelength.value_unit),
            freq_unit=body.freq_unit,
            wvl_unit=body.wvl_unit,
            center_wavelength=float(center_wavelength.value_unit),
            center_unit=body.center_unit,
        )
    except (ValidationError, ValueError, TypeError) as exc:
        raise _validation_error(exc) from exc
