from enum import Enum
from typing import Union

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ScalarOrArray = Union[float, NDArray[np.floating]]


def _coerce_scalar_or_array(value) -> ScalarOrArray:
    """Normalize scalar or array-like input to float or ndarray."""
    if isinstance(value, np.ndarray):
        return np.asarray(value, dtype=float)
    if isinstance(value, (list, tuple)):
        return np.asarray(value, dtype=float)
    return float(value)


def _validate_strictly_positive(value: ScalarOrArray) -> ScalarOrArray:
    """Ensure every element in value_si is strictly positive."""
    if isinstance(value, np.ndarray):
        if value.size and np.any(value <= 0):
            raise ValueError("value_si must be strictly positive")
        return value
    if value <= 0:
        raise ValueError("value_si must be strictly positive")
    return value


class DecibelUnit(str, Enum):
    """Enumeration of decibel units (case-insensitive parsing)."""

    DECIBEL = "dB"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for unit strings."""
        if not isinstance(value, str):
            return None
        value_lower = value.lower()
        for member in cls:
            if member.value.lower() == value_lower:
                return member
        return None


class PercentUnit(str, Enum):
    """Enumeration of percent units (case-insensitive parsing)."""

    PERCENT = "%"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for unit strings."""
        if not isinstance(value, str):
            return None
        value_lower = value.lower()
        aliases = {"percent", "pct"}
        if value_lower in aliases:
            return cls.PERCENT
        for member in cls:
            if member.value.lower() == value_lower:
                return member
        return None


class Decibel(BaseModel):
    """Model representing transmission or attenuation in decibels."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value_si: ScalarOrArray = Field(
        ...,
        description="The value in decibels.",
    )
    unit: DecibelUnit = Field(
        default=DecibelUnit.DECIBEL,
        description="The unit of measurement.",
    )

    @field_validator("value_si", mode="before")
    @classmethod
    def _coerce_value_si(cls, value):
        return _coerce_scalar_or_array(value)

    @property
    def is_array(self) -> bool:
        """Return True when value_si holds multiple elements."""
        return isinstance(self.value_si, np.ndarray)

    @property
    def value_unit(self) -> ScalarOrArray:
        """Return the value expressed in the selected unit."""
        return self.value_si


class Percent(BaseModel):
    """Model representing transmission as a percentage."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value_si: ScalarOrArray = Field(
        ...,
        description="The value in percent (must be strictly positive).",
    )
    unit: PercentUnit = Field(
        default=PercentUnit.PERCENT,
        description="The unit of measurement.",
    )

    @field_validator("value_si", mode="before")
    @classmethod
    def _coerce_value_si(cls, value):
        return _coerce_scalar_or_array(value)

    @field_validator("value_si")
    @classmethod
    def _validate_value_si(cls, value):
        return _validate_strictly_positive(value)

    @property
    def is_array(self) -> bool:
        """Return True when value_si holds multiple elements."""
        return isinstance(self.value_si, np.ndarray)

    @property
    def value_unit(self) -> ScalarOrArray:
        """Return the value expressed in the selected unit."""
        return self.value_si


class MilliwattUnit(str, Enum):
    """Enumeration of milliwatt units (case-insensitive parsing)."""

    MILLIWATT = "mW"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for unit strings."""
        if not isinstance(value, str):
            return None
        value_lower = value.lower()
        for member in cls:
            if member.value.lower() == value_lower:
                return member
        return None


class DecibelMilliwattUnit(str, Enum):
    """Enumeration of dBm units (case-insensitive parsing)."""

    DECIBEL_MILLIWATT = "dBm"

    @classmethod
    def _missing_(cls, value):
        """Allow case-insensitive matching for unit strings."""
        if not isinstance(value, str):
            return None
        value_lower = value.lower()
        for member in cls:
            if member.value.lower() == value_lower:
                return member
        return None


class Milliwatt(BaseModel):
    """Model representing optical power in milliwatts."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value_si: ScalarOrArray = Field(
        ...,
        description="The power in milliwatts (must be strictly positive).",
    )
    unit: MilliwattUnit = Field(
        default=MilliwattUnit.MILLIWATT,
        description="The unit of measurement.",
    )

    @field_validator("value_si", mode="before")
    @classmethod
    def _coerce_value_si(cls, value):
        return _coerce_scalar_or_array(value)

    @field_validator("value_si")
    @classmethod
    def _validate_value_si(cls, value):
        return _validate_strictly_positive(value)

    @property
    def is_array(self) -> bool:
        """Return True when value_si holds multiple elements."""
        return isinstance(self.value_si, np.ndarray)

    @property
    def value_unit(self) -> ScalarOrArray:
        """Return the power expressed in the selected unit."""
        return self.value_si


class DecibelMilliwatt(BaseModel):
    """Model representing optical power in dBm."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value_si: ScalarOrArray = Field(
        ...,
        description="The power in dBm.",
    )
    unit: DecibelMilliwattUnit = Field(
        default=DecibelMilliwattUnit.DECIBEL_MILLIWATT,
        description="The unit of measurement.",
    )

    @field_validator("value_si", mode="before")
    @classmethod
    def _coerce_value_si(cls, value):
        return _coerce_scalar_or_array(value)

    @property
    def is_array(self) -> bool:
        """Return True when value_si holds multiple elements."""
        return isinstance(self.value_si, np.ndarray)

    @property
    def value_unit(self) -> ScalarOrArray:
        """Return the power expressed in the selected unit."""
        return self.value_si


class TransmissionUnit(BaseModel):
    """Transmission with synchronized decibel and percent representations.

    Initialize with exactly one of ``decibel`` or ``percent``; the other
    representation is derived automatically. Scalar and array-like inputs
    are supported; derived quantities always match the shape of the provided
    quantity.
    """

    decibel: Decibel
    percent: Percent

    @property
    def is_array(self) -> bool:
        """Return True when all synchronized quantities hold multiple elements."""
        return self.decibel.is_array

    @model_validator(mode="before")
    @classmethod
    def _derive_all_quantities(cls, data):
        if isinstance(data, TransmissionUnit):
            return {
                "decibel": data.decibel,
                "percent": data.percent,
            }

        if not isinstance(data, dict):
            raise TypeError("TransmissionUnit must be initialized with keyword arguments")

        decibel = data.get("decibel")
        percent = data.get("percent")
        provided = sum(value is not None for value in (decibel, percent))
        if provided != 1:
            raise ValueError("Exactly one of decibel or percent must be provided")

        if decibel is not None:
            if not isinstance(decibel, Decibel):
                decibel = Decibel(value_si=decibel)
            db = decibel.value_si
            pct = 100 * np.power(10, db / 10)
            return {
                "decibel": decibel,
                "percent": Percent(value_si=pct),
            }

        if not isinstance(percent, Percent):
            percent = Percent(value_si=percent)
        pct = percent.value_si
        db = 10 * np.log10(pct / 100)
        return {
            "decibel": Decibel(value_si=db),
            "percent": percent,
        }


class PowerUnit(BaseModel):
    """Optical power with synchronized milliwatt and dBm representations.

    Initialize with exactly one of ``milliwatt`` or ``decibel_milliwatt``;
    the other representation is derived automatically. Scalar and array-like
    inputs are supported; derived quantities always match the shape of the
    provided quantity.
    """

    milliwatt: Milliwatt
    decibel_milliwatt: DecibelMilliwatt

    @property
    def is_array(self) -> bool:
        """Return True when all synchronized quantities hold multiple elements."""
        return self.milliwatt.is_array

    @model_validator(mode="before")
    @classmethod
    def _derive_all_quantities(cls, data):
        if isinstance(data, PowerUnit):
            return {
                "milliwatt": data.milliwatt,
                "decibel_milliwatt": data.decibel_milliwatt,
            }

        if not isinstance(data, dict):
            raise TypeError("PowerUnit must be initialized with keyword arguments")

        milliwatt = data.get("milliwatt")
        decibel_milliwatt = data.get("decibel_milliwatt")
        provided = sum(value is not None for value in (milliwatt, decibel_milliwatt))
        if provided != 1:
            raise ValueError(
                "Exactly one of milliwatt or decibel_milliwatt must be provided"
            )

        if milliwatt is not None:
            if not isinstance(milliwatt, Milliwatt):
                milliwatt = Milliwatt(value_si=milliwatt)
            mw = milliwatt.value_si
            dbm = 10 * np.log10(mw)
            return {
                "milliwatt": milliwatt,
                "decibel_milliwatt": DecibelMilliwatt(value_si=dbm),
            }

        if not isinstance(decibel_milliwatt, DecibelMilliwatt):
            decibel_milliwatt = DecibelMilliwatt(value_si=decibel_milliwatt)
        dbm = decibel_milliwatt.value_si
        mw = np.power(10, dbm / 10)
        return {
            "milliwatt": Milliwatt(value_si=mw),
            "decibel_milliwatt": decibel_milliwatt,
        }


if __name__ == "__main__":
    tu = TransmissionUnit(decibel=0.0)
    print(tu)
    print(f"{tu.percent.value_unit:.3f} %")

    pu = PowerUnit(milliwatt=1.0)
    print(pu)
    print(f"{pu.decibel_milliwatt.value_unit:.3f} dBm")
