import type { ReactNode } from "react";

interface ConverterCardProps {
  title: string;
  caption?: string;
  children: ReactNode;
}

export function ConverterCard({ title, caption, children }: ConverterCardProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <header className="mb-4">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        {caption ? (
          <p className="mt-1 text-sm text-slate-500">{caption}</p>
        ) : null}
      </header>
      {children}
    </section>
  );
}

interface ResultDisplayProps {
  label: string;
  value: string;
}

export function ResultDisplay({ label, value }: ResultDisplayProps) {
  return (
    <div className="rounded-lg bg-slate-50 px-4 py-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-mono text-lg font-semibold text-slate-900">
        {value}
      </p>
    </div>
  );
}

interface SettingsPanelProps {
  decimalPlaces: number;
  stepSize: string;
  onDecimalPlacesChange: (value: number) => void;
  onStepSizeChange: (value: string) => void;
}

export function SettingsPanel({
  decimalPlaces,
  stepSize,
  onDecimalPlacesChange,
  onStepSizeChange,
}: SettingsPanelProps) {
  return (
    <aside className="w-56 shrink-0 space-y-5 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Decimal Places
        </label>
        <input
          type="range"
          min={0}
          max={6}
          step={1}
          value={decimalPlaces}
          onChange={(event) => onDecimalPlacesChange(Number(event.target.value))}
          className="w-full"
        />
        <p className="mt-1 text-xs text-slate-500">{decimalPlaces}</p>
      </div>
      <fieldset>
        <legend className="mb-2 text-sm font-medium text-slate-700">
          Step Size
        </legend>
        <div className="flex flex-col gap-2">
          {["10.0", "1.0", "0.1", "0.01"].map((option) => (
            <label key={option} className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="step-size"
                value={option}
                checked={stepSize === option}
                onChange={() => onStepSizeChange(option)}
              />
              {option}
            </label>
          ))}
        </div>
      </fieldset>
    </aside>
  );
}
