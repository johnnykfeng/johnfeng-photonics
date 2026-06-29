interface UnitRadioGroupProps<T extends string> {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
}

export function UnitRadioGroup<T extends string>({
  label,
  options,
  value,
  onChange,
}: UnitRadioGroupProps<T>) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-sm font-medium text-slate-700">{label}</legend>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <label
            key={option}
            className={[
              "cursor-pointer rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              value === option
                ? "border-sky-500 bg-sky-100 text-sky-900"
                : "border-slate-300 bg-white text-slate-600 hover:border-slate-400",
            ].join(" ")}
          >
            <input
              type="radio"
              name={label}
              value={option}
              checked={value === option}
              onChange={() => onChange(option)}
              className="sr-only"
            />
            {option}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
