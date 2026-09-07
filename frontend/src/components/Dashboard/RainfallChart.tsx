import React from "react";
import { WeatherForecast } from "@/types/flood";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

interface Props {
  forecast: WeatherForecast | null;
}

export const RainfallChart: React.FC<Props> = ({ forecast }) => {
  if (!forecast || !forecast.hourly || forecast.hourly.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 h-64 flex items-center justify-center text-xs text-slate-500">
        Awaiting rainfall forecast timeseries...
      </div>
    );
  }

  // Format chart data for 6 hours
  const data = forecast.hourly.map((item, idx) => {
    // Extract time label (e.g. 14:00)
    const timePart = item.timestamp_utc.includes("T")
      ? item.timestamp_utc.split("T")[1].substring(0, 5)
      : `+${idx + 1}h`;

    return {
      time: timePart,
      precipitation_mm: item.precipitation_mm,
      probability_pct: item.precipitation_probability_pct ?? 0,
      temperature_c: item.temperature_c ?? 0
    };
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col justify-between h-72">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            0–6 Hour Precipitation Forecast &amp; Rain Probability (NWP Baseline)
          </h3>
          <p className="text-[11px] text-slate-400">Open-Meteo Global NWP Model (ECMWF/GFS blend)</p>
        </div>
        <span className="text-[10px] font-mono text-sky-400 bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800">
          6H Horizon
        </span>
      </div>

      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="precipGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} unit="mm" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "6px",
                fontSize: "11px",
                color: "#f8fafc"
              }}
              formatter={(val: any, name: string) => {
                if (name === "precipitation_mm") return [`${val} mm`, "Expected Rain"];
                if (name === "probability_pct") return [`${val}%`, "Precip Probability"];
                return [val, name];
              }}
            />
            <Area
              type="monotone"
              dataKey="precipitation_mm"
              stroke="#38bdf8"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#precipGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 font-mono">
        <span>Cum. Total: {forecast.cumulative_forecast_6h_mm} mm</span>
        <span>Peak Rate: {forecast.max_forecast_intensity_mm_h} mm/h</span>
      </div>
    </div>
  );
};
