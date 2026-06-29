import { useCallback, useEffect, useRef, useState } from "react";
import {
  ConverterCard,
  ResultDisplay,
  SettingsPanel,
} from "../components/ConverterCard";
import { NumberField } from "../components/NumberField";
import { UnitRadioGroup } from "../components/UnitRadioGroup";
import { api, ApiError } from "../lib/api";
import { FREQ_UNITS, formatValue, WVL_UNITS, type FreqUnit, type WvlUnit } from "../lib/units";

type PhotonicSource = "frequency" | "wavelength";
type TransmissionSource = "dB" | "percent";
type PowerSource = "mW" | "dBm";

export function UnitConverter() {
  const [decimalPlaces, setDecimalPlaces] = useState(3);
  const [stepSize, setStepSize] = useState("0.1");
  const step = parseFloat(stepSize);

  const [freqUnit, setFreqUnit] = useState<FreqUnit>("GHz");
  const [wvlUnit, setWvlUnit] = useState<WvlUnit>("nm");
  const [freqInput, setFreqInput] = useState(0);
  const [wvlInput, setWvlInput] = useState(0);
  const [omegaRadS, setOmegaRadS] = useState(0);
  const [photonicSource, setPhotonicSource] = useState<PhotonicSource>("wavelength");
  const [photonicError, setPhotonicError] = useState<string | null>(null);

  const [dbInput, setDbInput] = useState(0);
  const [percentInput, setPercentInput] = useState(100);
  const [transmissionSource, setTransmissionSource] =
    useState<TransmissionSource>("dB");
  const [transmissionError, setTransmissionError] = useState<string | null>(null);

  const [mwInput, setMwInput] = useState(1);
  const [dbmInput, setDbmInput] = useState(0);
  const [powerSource, setPowerSource] = useState<PowerSource>("dBm");
  const [powerError, setPowerError] = useState<string | null>(null);

  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    api.getDefaults().then((defaults) => {
      setWvlInput(defaults.wavelength);
      setDbInput(defaults.transmission);
      setPercentInput(100);
      setMwInput(defaults.power_mW);
      setDbmInput(defaults.power_dBm);
      setPhotonicSource("wavelength");
      setTransmissionSource("dB");
      setPowerSource("dBm");
    });
  }, []);

  useEffect(() => {
    const value = photonicSource === "frequency" ? freqInput : wvlInput;
    if (!Number.isFinite(value)) return;

    const timer = setTimeout(async () => {
      try {
        const result = await api.convertPhotonic({
          value,
          from: photonicSource,
          freq_unit: freqUnit,
          wvl_unit: wvlUnit,
        });
        setFreqInput(result.frequency);
        setWvlInput(result.wavelength);
        setOmegaRadS(result.angular_frequency_rad_s);
        setPhotonicError(null);
      } catch (error) {
        setPhotonicError(
          error instanceof ApiError ? error.message : "Conversion failed",
        );
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [freqInput, wvlInput, freqUnit, wvlUnit, photonicSource]);

  useEffect(() => {
    const value = transmissionSource === "dB" ? dbInput : percentInput;
    if (!Number.isFinite(value)) return;

    const timer = setTimeout(async () => {
      try {
        const result = await api.convertTransmission({
          value,
          from: transmissionSource,
        });
        setDbInput(result.dB);
        setPercentInput(result.percent);
        setTransmissionError(null);
      } catch (error) {
        setTransmissionError(
          error instanceof ApiError ? error.message : "Conversion failed",
        );
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [dbInput, percentInput, transmissionSource]);

  useEffect(() => {
    const value = powerSource === "mW" ? mwInput : dbmInput;
    if (!Number.isFinite(value)) return;

    const timer = setTimeout(async () => {
      try {
        const result = await api.convertPower({
          value,
          from: powerSource,
        });
        setMwInput(result.mW);
        setDbmInput(result.dBm);
        setPowerError(null);
      } catch (error) {
        setPowerError(
          error instanceof ApiError ? error.message : "Conversion failed",
        );
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [mwInput, dbmInput, powerSource]);

  const onFreqChange = useCallback((value: number) => {
    setPhotonicSource("frequency");
    setFreqInput(value);
  }, []);

  const onWvlChange = useCallback((value: number) => {
    setPhotonicSource("wavelength");
    setWvlInput(value);
  }, []);

  const onDbChange = useCallback((value: number) => {
    setTransmissionSource("dB");
    setDbInput(value);
  }, []);

  const onPercentChange = useCallback((value: number) => {
    setTransmissionSource("percent");
    setPercentInput(value);
  }, []);

  const onMwChange = useCallback((value: number) => {
    setPowerSource("mW");
    setMwInput(value);
  }, []);

  const onDbmChange = useCallback((value: number) => {
    setPowerSource("dBm");
    setDbmInput(value);
  }, []);

  return (
    <div className="flex gap-6">
      <SettingsPanel
        decimalPlaces={decimalPlaces}
        stepSize={stepSize}
        onDecimalPlacesChange={setDecimalPlaces}
        onStepSizeChange={setStepSize}
      />

      <div className="flex min-w-0 flex-1 flex-col gap-6">
        <div>
          <p className="text-xs text-slate-500">Last updated: 2026-06-28</p>
          <h1 className="mt-1 text-2xl font-bold text-slate-900">
            Unit Converter
          </h1>
        </div>

        <ConverterCard
          title="f ↔ λ Converter"
          caption="Edit frequency or wavelength — the other field updates to stay in sync."
        >
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <UnitRadioGroup
                label="Frequency Unit"
                options={FREQ_UNITS}
                value={freqUnit}
                onChange={setFreqUnit}
              />
              <NumberField
                label={`Input Frequency (${freqUnit})`}
                value={freqInput}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={onFreqChange}
              />
              <ResultDisplay
                label="Frequency"
                value={`f = ${formatValue(freqInput, decimalPlaces)} ${freqUnit}`}
              />
              <ResultDisplay
                label="Angular frequency"
                value={`ω = ${formatValue(omegaRadS, decimalPlaces)} rad/s`}
              />
            </div>
            <div className="space-y-4">
              <UnitRadioGroup
                label="Wavelength Unit"
                options={WVL_UNITS}
                value={wvlUnit}
                onChange={setWvlUnit}
              />
              <NumberField
                label={`Input Wavelength (${wvlUnit})`}
                value={wvlInput}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={onWvlChange}
              />
              <ResultDisplay
                label="Wavelength"
                value={`λ = ${formatValue(wvlInput, decimalPlaces)} ${wvlUnit}`}
              />
            </div>
          </div>
          {photonicError ? (
            <p className="mt-4 text-sm text-red-600">{photonicError}</p>
          ) : null}
        </ConverterCard>

        <ConverterCard
          title="T[dB] ↔ T[%] Converter"
          caption="Edit transmission in dB or percent — the other field updates to stay in sync."
        >
          <div className="grid gap-6 md:grid-cols-2">
            <NumberField
              label="T[dB]"
              value={dbInput}
              step={step}
              decimalPlaces={decimalPlaces}
              onChange={onDbChange}
            />
            <NumberField
              label="T[%]"
              value={percentInput}
              step={step}
              min={0}
              decimalPlaces={decimalPlaces}
              onChange={onPercentChange}
            />
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <ResultDisplay
              label="Transmission (dB)"
              value={`T[dB] = ${formatValue(dbInput, decimalPlaces)} dB`}
            />
            <ResultDisplay
              label="Transmission (%)"
              value={`T = ${formatValue(percentInput, decimalPlaces)}%`}
            />
          </div>
          {transmissionError ? (
            <p className="mt-4 text-sm text-red-600">{transmissionError}</p>
          ) : null}
        </ConverterCard>

        <ConverterCard
          title="P[dBm] ↔ P[mW] Converter"
          caption="Edit power in mW or dBm — the other field updates to stay in sync."
        >
          <div className="grid gap-6 md:grid-cols-2">
            <NumberField
              label="Power (mW)"
              value={mwInput}
              step={step}
              min={0}
              decimalPlaces={decimalPlaces}
              onChange={onMwChange}
            />
            <NumberField
              label="Power (dBm)"
              value={dbmInput}
              step={step}
              decimalPlaces={decimalPlaces}
              onChange={onDbmChange}
            />
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <ResultDisplay
              label="Power (dBm)"
              value={`P[dBm] = ${formatValue(dbmInput, decimalPlaces)} dBm`}
            />
            <ResultDisplay
              label="Power (mW)"
              value={`P[mW] = ${formatValue(mwInput, decimalPlaces)} mW`}
            />
          </div>
          {powerError ? (
            <p className="mt-4 text-sm text-red-600">{powerError}</p>
          ) : null}
        </ConverterCard>
      </div>
    </div>
  );
}
