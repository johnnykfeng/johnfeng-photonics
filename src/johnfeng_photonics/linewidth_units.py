from pydantic import BaseModel, model_validator

from .photonic_units import (
    SPEED_OF_LIGHT,
    Frequency,
    FrequencyUnit,
    Wavelength,
    WavelengthUnit,
)


class LinewidthUnit(BaseModel):
    """Linewidth with synchronized frequency and wavelength representations.

    Initialize with ``center_wavelength`` and exactly one of ``frequency`` or
    ``wavelength``; the other representation is derived automatically. Scalar
    and array-like inputs are supported; derived quantities always match the
    shape of the provided quantity.
    """

    frequency: Frequency
    wavelength: Wavelength
    center_wavelength: Wavelength

    @property
    def is_array(self) -> bool:
        """Return True when all synchronized quantities hold multiple elements."""
        return self.frequency.is_array

    @model_validator(mode="before")
    @classmethod
    def _derive_all_quantities(cls, data):
        if isinstance(data, LinewidthUnit):
            return {
                "frequency": data.frequency,
                "wavelength": data.wavelength,
                "center_wavelength": data.center_wavelength,
            }

        if not isinstance(data, dict):
            raise TypeError("LinewidthUnit must be initialized with keyword arguments")

        frequency = data.get("frequency")
        wavelength = data.get("wavelength")
        center_wavelength = data.get("center_wavelength")
        if center_wavelength is None:
            raise ValueError("center_wavelength must be provided")

        provided = sum(value is not None for value in (frequency, wavelength))
        if provided != 1:
            raise ValueError(
                "Exactly one of frequency or wavelength must be provided"
            )

        if not isinstance(center_wavelength, Wavelength):
            center_wavelength = Wavelength(value_si=center_wavelength)
        center_wl_si = center_wavelength.value_si

        if frequency is not None:
            if not isinstance(frequency, Frequency):
                frequency = Frequency(value_si=frequency)
            freq_hz = frequency.value_si
            wl_si = freq_hz * (center_wl_si**2) / SPEED_OF_LIGHT
            return {
                "frequency": frequency,
                "wavelength": Wavelength(value_si=wl_si, unit=WavelengthUnit.NANOMETER),
                "center_wavelength": center_wavelength,
            }

        if not isinstance(wavelength, Wavelength):
            wavelength = Wavelength(value_si=wavelength)
        wl_si = wavelength.value_si
        freq_hz = wl_si * SPEED_OF_LIGHT / (center_wl_si**2)
        return {
            "frequency": Frequency(value_si=freq_hz, unit=FrequencyUnit.MEGAHERTZ),
            "wavelength": wavelength,
            "center_wavelength": center_wavelength,
        }

    def __repr_args__(self) -> list[tuple[str, str]]:
        return [
            (
                "frequency",
                f"{self.frequency.value_unit:.2f} {self.frequency.unit.value}",
            ),
            (
                "wavelength",
                f"{self.wavelength.value_unit:.2f} {self.wavelength.unit.value}",
            ),
            (
                "center_wavelength",
                f"{self.center_wavelength.value_unit:.2f} {self.center_wavelength.unit.value}",
            ),
        ]


if __name__ == "__main__":
    center = Wavelength(value_si=1550e-9, unit="nm")
    lu = LinewidthUnit(
        frequency=Frequency(value_si=10e9, unit=FrequencyUnit.GIGAHERTZ),
        center_wavelength=center,
    )
    print(lu)
    print(f"{lu.wavelength.value_unit:.4f} {lu.wavelength.unit.value}")

    lu = LinewidthUnit(
        wavelength=Wavelength(value_si=0.01e-9, unit="nm"),
        center_wavelength=center,
    )
    print(lu)
    print(f"{lu.frequency.value_unit:.4f} {lu.frequency.unit.value}")
