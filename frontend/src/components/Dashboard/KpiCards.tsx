import React from "react";
import { FloodPredictionRun, WeatherCurrent } from "@/types/flood";
import { ProvenanceBadge } from "../Common/ProvenanceBadge";
import { CloudRain, TrendingUp, AlertOctagon, Waves, Timer, ShieldAlert } from "lucide-react";

interface Props {
  weather: WeatherCurrent | null;
  floodRun: FloodPredictionRun | null;
}

export const KpiCards: React.FC<Props> = ({ weather, floodRun }) => {
  const currentRain = weather?.precipitation_mm_h ?? (floodRun?.current_rainfall_mm_h ?? 0.0);
  const forecast6h = floodRun?.forecast_cumulative_6h_mm ?? 0.0;
  const riskScore = floodRun?.max_flood_risk_score ?? 0.0;
  const overallSeverity = floodRun?.overall_severity ?? "VERY_LOW";
  const depthBracket = floodRun?.highest_estimated_depth_bracket ?? "< 0.10 m";
  const earliestTime = floodRun?.earliest_time_to_flood ?? "> 6 hours / Low Risk";
  const hotspotsCount = floodRun?.affected_hotspots_count ?? 0;

  // Severity color formatting
  let severityBadgeClass = "bg-emerald-950 text-emerald-400 border-emerald-800";
  if (overallSeverity === "EXTREME") {
    severityBadgeClass = "bg-rose-950 text-rose-400 border-rose-800 pulse-red";
  } else if (overallSeverity === "HIGH") {
    severityBadgeClass = "bg-orange-950 text-orange-400 border-orange-800";
  } else if (overallSeverity === "MODERATE") {
    severityBadgeClass = "bg-amber-950 text-amber-400 border-amber-800";
  } else if (overallSeverity === "LOW") {
    severityBadgeClass = "bg-sky-950 text-sky-400 border-sky-800";
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* 1. Current Rainfall */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Current Rain</span>
          <CloudRain className="w-4 h-4 text-sky-400" />
        </div>
        <div className="my-1">
          <div className="text-xl font-bold font-mono text-white">
            {currentRain.toFixed(1)} <span className="text-xs font-sans text-slate-400 font-normal">mm/h</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5 truncate">
            {weather?.weather_condition || "Observing live"}
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Live feed</span>
          <ProvenanceBadge provenance={weather?.provenance || "LIVE"} size="sm" />
        </div>
      </div>

      {/* 2. 6h Cumulative Forecast */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">6h Forecast</span>
          <TrendingUp className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="my-1">
          <div className="text-xl font-bold font-mono text-white">
            {forecast6h.toFixed(1)} <span className="text-xs font-sans text-slate-400 font-normal">mm</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Max: {floodRun?.max_forecast_intensity_mm_h?.toFixed(1) || 0} mm/h
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">NWP ECMWF/GFS</span>
          <ProvenanceBadge provenance="FORECAST" size="sm" />
        </div>
      </div>

      {/* 3. Max Flood Risk Score */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Flood Risk Score</span>
          <AlertOctagon className="w-4 h-4 text-amber-400" />
        </div>
        <div className="my-1">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black font-mono text-white">{riskScore.toFixed(0)}</span>
            <span className="text-xs text-slate-400 font-mono">/ 100</span>
          </div>
          <div className="mt-1">
            <span className={`inline-block px-1.5 py-0.5 text-[10px] font-bold uppercase rounded border ${severityBadgeClass}`}>
              {overallSeverity}
            </span>
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Uncalibrated Index</span>
          <ProvenanceBadge provenance={floodRun?.execution_mode || "DERIVED"} size="sm" />
        </div>
      </div>

      {/* 4. Highest Estimated Depth */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Peak Est. Depth</span>
          <Waves className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="my-1">
          <div className="text-base font-bold font-mono text-white truncate">
            {depthBracket}
          </div>
          <div className="text-[10px] text-amber-400/90 font-mono mt-1 flex items-center gap-1">
            <span>[MODEL ESTIMATE]</span>
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Not sensor data</span>
          <ProvenanceBadge provenance="DERIVED" size="sm" />
        </div>
      </div>

      {/* 5. Earliest Time to Flood */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Time-to-Flood</span>
          <Timer className="w-4 h-4 text-orange-400" />
        </div>
        <div className="my-1">
          <div className="text-xs font-bold font-mono text-white truncate">
            {earliestTime}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            ESTIMATED lead window
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">SCS accumulation</span>
          <ProvenanceBadge provenance="DERIVED" size="sm" />
        </div>
      </div>

      {/* 6. Active High Risk Zones */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Active Hotspots</span>
          <ShieldAlert className="w-4 h-4 text-red-400" />
        </div>
        <div className="my-1">
          <div className="text-2xl font-black font-mono text-white">
            {hotspotsCount} <span className="text-xs font-normal text-slate-400 font-sans">monitored</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            NH-44 & LPU Basin
          </div>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <span className="text-[10px] text-slate-500">Verified nodes</span>
          <ProvenanceBadge provenance="HISTORICAL" size="sm" />
        </div>
      </div>
    </div>
  );
};
