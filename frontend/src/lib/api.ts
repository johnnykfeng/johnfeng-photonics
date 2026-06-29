import type { FreqUnit, WvlUnit } from "./units";

export interface Defaults {
  wavelength: number;
  omega: number;
  frequency: number;
  quality_factor: number;
  transmission: number;
  power_mW: number;
  power_dBm: number;
  linewidth_GHz: number;
  linewidth_nm: number;
  linewidth_MHz: number;
}

export interface PhotonicConvertRequest {
  value: number;
  from: "frequency" | "wavelength";
  freq_unit: FreqUnit;
  wvl_unit: WvlUnit;
}

export interface PhotonicConvertResponse {
  frequency: number;
  wavelength: number;
  angular_frequency_rad_s: number;
  freq_unit: string;
  wvl_unit: string;
}

export interface TransmissionConvertRequest {
  value: number;
  from: "dB" | "percent";
}

export interface TransmissionConvertResponse {
  dB: number;
  percent: number;
}

export interface PowerConvertRequest {
  value: number;
  from: "mW" | "dBm";
}

export interface PowerConvertResponse {
  mW: number;
  dBm: number;
}

export interface LinewidthConvertRequest {
  value: number;
  from: "frequency" | "wavelength";
  freq_unit: FreqUnit;
  wvl_unit: WvlUnit;
  center_wavelength: number;
  center_unit: WvlUnit;
}

export interface LinewidthConvertResponse {
  frequency: number;
  wavelength: number;
  freq_unit: string;
  wvl_unit: string;
  center_wavelength: number;
  center_unit: string;
}

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(detail, response.status);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getDefaults: () => request<Defaults>("/api/meta/defaults"),
  getEquationsSource: () =>
    request<{ source: string }>("/api/meta/equations-source"),
  convertPhotonic: (body: PhotonicConvertRequest) =>
    request<PhotonicConvertResponse>("/api/convert/photonic", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  convertTransmission: (body: TransmissionConvertRequest) =>
    request<TransmissionConvertResponse>("/api/convert/transmission", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  convertPower: (body: PowerConvertRequest) =>
    request<PowerConvertResponse>("/api/convert/power", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  convertLinewidth: (body: LinewidthConvertRequest) =>
    request<LinewidthConvertResponse>("/api/convert/linewidth", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

export { ApiError };
