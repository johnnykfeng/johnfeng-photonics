import { useCallback, useEffect, useRef, useState } from "react";
import {
  ConverterCard,
  ResultDisplay,
  SettingsPanel,
} from "../components/ConverterCard";
import { NumberField } from "../components/NumberField";
import { UnitRadioGroup } from "../components/UnitRadioGroup";
import { Equation } from "../components/Equation";
import { api, ApiError } from "../lib/api";
import { FREQ_UNITS, formatValue, WVL_UNITS, type FreqUnit, type WvlUnit } from "../lib/units";

export function LinewidthConverter() {
  const [decimalPlaces, setDecimalPlaces] = useState(6);
  const [stepSize, setStepSize] = useState("0.1");
  const step = parseFloat(stepSize);

  const [freqUnit1, setFreqUnit1] = useState<FreqUnit>("MHz");
  const [wvlUnit1, setWvlUnit1] = useState<WvlUnit>("nm");
  const [centerUnit1, setCenterUnit1] = useState<WvlUnit>("nm");
  const [linewidthFreqInput, setLinewidthFreqInput] = useState(0);
  const [centerWavelength1, setCenterWavelength1] = useState(0);
  const [linewidthWvlOutput, setLinewidthWvlOutput] = useState(0);
  const [freqToWvlError, setFreqToWvlError] = useState<string | null>(null);

  const [wvlUnit2, setWvlUnit2] = useState<WvlUnit>("nm");
  const [centerUnit2, setCenterUnit2] = useState<WvlUnit>("nm");
  const [freqUnit2, setFreqUnit2] = useState<FreqUnit>("GHz");
  const [linewidthWvlInput, setLinewidthWvlInput] = useState(0);
  const [centerWavelength2, setCenterWavelength2] = useState(0);
  const [linewidthFreqOutput, setLinewidthFreqOutput] = useState(0);
  const [wvlToFreqError, setWvlToFreqError] = useState<string | null>(null);

  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    api.getDefaults().then((defaults) => {
      setLinewidthFreqInput(defaults.linewidth_MHz);
      setCenterWavelength1(defaults.wavelength);
      setCenterWavelength2(defaults.wavelength);
      setLinewidthWvlInput(defaults.linewidth_nm);
    });
  }, []);

  useEffect(() => {
    if (!Number.isFinite(linewidthFreqInput) || !Number.isFinite(centerWavelength1)) {
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const result = await api.convertLinewidth({
          value: linewidthFreqInput,
          from: "frequency",
          freq_unit: freqUnit1,
          wvl_unit: wvlUnit1,
          center_wavelength: centerWavelength1,
          center_unit: centerUnit1,
        });
        setLinewidthWvlOutput(result.wavelength);
        setFreqToWvlError(null);
      } catch (error) {
        setFreqToWvlError(
          error instanceof ApiError ? error.message : "Conversion failed",
        );
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [
    linewidthFreqInput,
    centerWavelength1,
    freqUnit1,
    wvlUnit1,
    centerUnit1,
  ]);

  useEffect(() => {
    if (!Number.isFinite(linewidthWvlInput) || !Number.isFinite(centerWavelength2)) {
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const result = await api.convertLinewidth({
          value: linewidthWvlInput,
          from: "wavelength",
          freq_unit: freqUnit2,
          wvl_unit: wvlUnit2,
          center_wavelength: centerWavelength2,
          center_unit: centerUnit2,
        });
        setLinewidthFreqOutput(result.frequency);
        setWvlToFreqError(null);
      } catch (error) {
        setWvlToFreqError(
          error instanceof ApiError ? error.message : "Conversion failed",
        );
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [
    linewidthWvlInput,
    centerWavelength2,
    freqUnit2,
    wvlUnit2,
    centerUnit2,
  ]);

  const onLinewidthFreqChange = useCallback((value: number) => {
    setLinewidthFreqInput(value);
  }, []);

  const onLinewidthWvlChange = useCallback((value: number) => {
    setLinewidthWvlInput(value);
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
            Linewidth Converter
          </h1>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ConverterCard title="Δν → Δλ">
            <Equation math="\Delta \lambda = \frac{\lambda_0^2}{c} \Delta \nu" />
            <div className="space-y-4">
              <UnitRadioGroup
                label="Frequency Unit"
                options={FREQ_UNITS}
                value={freqUnit1}
                onChange={setFreqUnit1}
              />
              <UnitRadioGroup
                label="Output Wavelength Unit"
                options={WVL_UNITS}
                value={wvlUnit1}
                onChange={setWvlUnit1}
              />
              <UnitRadioGroup
                label="Center Wavelength Unit"
                options={WVL_UNITS}
                value={centerUnit1}
                onChange={setCenterUnit1}
              />
              <NumberField
                label={`Linewidth (${freqUnit1})`}
                value={linewidthFreqInput}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={onLinewidthFreqChange}
              />
              <NumberField
                label={`Center Wavelength (${centerUnit1})`}
                value={centerWavelength1}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={setCenterWavelength1}
              />
              <ResultDisplay
                label="Linewidth (wavelength)"
                value={`Δλ = ${formatValue(linewidthWvlOutput, decimalPlaces)} ${wvlUnit1}`}
              />
              {freqToWvlError ? (
                <p className="text-sm text-red-600">{freqToWvlError}</p>
              ) : null}
            </div>
          </ConverterCard>

          <ConverterCard title="Δλ → Δν">
            <Equation math="\Delta \nu = \frac{c}{\lambda_0^2} \Delta \lambda" />
            <div className="space-y-4">
              <UnitRadioGroup
                label="Linewidth Wavelength Unit"
                options={WVL_UNITS}
                value={wvlUnit2}
                onChange={setWvlUnit2}
              />
              <UnitRadioGroup
                label="Center Wavelength Unit"
                options={WVL_UNITS}
                value={centerUnit2}
                onChange={setCenterUnit2}
              />
              <UnitRadioGroup
                label="Output Frequency Unit"
                options={FREQ_UNITS}
                value={freqUnit2}
                onChange={setFreqUnit2}
              />
              <NumberField
                label={`Linewidth (${wvlUnit2})`}
                value={linewidthWvlInput}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={onLinewidthWvlChange}
              />
              <NumberField
                label={`Center Wavelength (${centerUnit2})`}
                value={centerWavelength2}
                step={step}
                decimalPlaces={decimalPlaces}
                onChange={setCenterWavelength2}
              />
              <ResultDisplay
                label="Linewidth (frequency)"
                value={`Δν = ${formatValue(linewidthFreqOutput, decimalPlaces)} ${freqUnit2}`}
              />
              {wvlToFreqError ? (
                <p className="text-sm text-red-600">{wvlToFreqError}</p>
              ) : null}
            </div>
          </ConverterCard>
        </div>
      </div>
    </div>
  );
}
