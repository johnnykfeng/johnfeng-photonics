interface NumberFieldProps {
  label: string;
  value: number;
  step: number;
  min?: number;
  decimalPlaces?: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function NumberField({
  label,
  value,
  step,
  min = 0,
  decimalPlaces = 3,
  onChange,
  disabled = false,
}: NumberFieldProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      <input
        type="number"
        value={Number.isFinite(value) ? value : ""}
        step={step}
        min={min}
        disabled={disabled}
        onChange={(event) => onChange(Number(event.target.value))}
        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200 disabled:bg-slate-100"
      />
      <span className="text-xs text-slate-400">
        Display precision: {decimalPlaces} decimal places
      </span>
    </label>
  );
}
