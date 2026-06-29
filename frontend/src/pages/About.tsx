import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { EquationList } from "../components/Equation";
import { api } from "../lib/api";

const aboutMarkdown = `
This app provides common photonics calculations and visualizations.

### Default Units:
- **Wavelength**: nm (nanometers) or 1e-9 m
- **Angular Frequency (ω)**: Trad/s (tera-radians per second) or 1e12 rad/s
- **Frequency (f)**: GHz (gigahertz) or 1e9 Hz
- **Quality Factor (Q)**: M (millions)
- **Transmission/Loss**: dB (decibels)
- **Power**: mW (milliwatts) or dBm

### Features:
- Unit conversions between frequency, wavelength, and angular frequency
- Power conversions between mW and dBm
- Transmission conversions between dB and percentage
- Linewidth conversions between GHz and nm
- Interactive plotting tools for frequency-wavelength relationships
- Sample transmission plots

### Physics Constants:
- Speed of light: c = 2.998 × 10⁸ m/s
`;

const equations = [
  String.raw`\omega = \frac{2 \pi c}{\lambda}`,
  String.raw`\lambda = \frac{2 \pi c}{\omega}`,
  String.raw`\nu = \frac{c}{\lambda}`,
  String.raw`\lambda = \frac{c}{\nu}`,
  String.raw`T[dB] = 10 \log_{10} \left(\frac{P_{out}}{P_{in}}\right)`,
  String.raw`T[\%] = 100 \left(\frac{P_{out}}{P_{in}}\right)`,
  String.raw`P_{dBm} = 10 \log_{10} (P_{mW})`,
  String.raw`P_{mW} = 10^{\frac{P_{dBm}}{10}}`,
  String.raw`\Delta \lambda = \frac{\lambda_0^2}{c} \Delta \nu`,
  String.raw`\Delta \nu = \frac{c}{\lambda_0^2} \Delta \lambda`,
];

export function About() {
  const [source, setSource] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getEquationsSource()
      .then((response) => setSource(response.source))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">About Photonics Helper</h1>
      </header>

      <article className="prose prose-slate max-w-none rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <ReactMarkdown>{aboutMarkdown}</ReactMarkdown>
      </article>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Equations</h2>
        <EquationList equations={equations} />
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">
          Python Conversion functions
        </h2>
        {loading ? (
          <p className="text-sm text-slate-500">Loading source...</p>
        ) : (
          <pre className="max-h-96 overflow-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-100">
            <code>{source}</code>
          </pre>
        )}
      </section>
    </div>
  );
}
