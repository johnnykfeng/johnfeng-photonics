export const FREQ_UNITS = ["MHz", "GHz", "THz"] as const;
export const WVL_UNITS = ["fm", "pm", "nm", "um"] as const;
export const STEP_SIZES = ["10.0", "1.0", "0.1", "0.01"] as const;

export type FreqUnit = (typeof FREQ_UNITS)[number];
export type WvlUnit = (typeof WVL_UNITS)[number];
export type StepSize = (typeof STEP_SIZES)[number];

export function formatValue(value: number, decimalPlaces: number): string {
  if (Math.abs(value) < 0.001 && value !== 0) {
    return value.toExponential(decimalPlaces);
  }
  return value.toFixed(decimalPlaces);
}
