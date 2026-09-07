"use client";

import React from "react";
import { Clock, CloudRain, AlertTriangle, ShieldCheck, TrendingUp } from "lucide-react";
import { NowcastHorizonPoint } from "@/types/flood";

interface Props {
  timeline: NowcastHorizonPoint[];
  selectedLeadHours: number;
  onSelectHorizon: (leadHours: number) => void;
  baseRainfall: number;
}

export function NowcastTimelineSlider({
  timeline,
  selectedLeadHours,
  onSelectHorizon,
  baseRainfall
}: Props) {
  const currentPoint = timeline.find((p) => p.lead_time_hours === selectedLeadHours) || timeline[0];

  return (
    <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-lg space-y-3">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-sky-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            0–6 Hour Nowcast Horizon Timeline
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">
            SHORT-TERM NOWCAST BASELINE &bull; NWP Trend Extrapolation
          </span>
        </div>

        {currentPoint && (
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-slate-400">Selected Horizon:</span>
            <span className="font-bold text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              {currentPoint.label}
            </span>
            <span className="text-slate-400 ml-2">Rainfall:</span>
            <span className="font-bold text-cyan-400">
              {currentPoint.projected_rainfall_mm_h} mm/h
            </span>
            <span className="text-[10px] text-slate-500">
              ({(currentPoint.confidence_score * 100).toFixed(0)}% confidence)
            </span>
          </div>
        )}
      </div>

      {/* Timeline Stepper Buttons */}
      <div className="grid grid-cols-3 sm:grid-cols-9 gap-1.5 font-mono text-[11px]">
        {timeline.map((point) => {
          const isSelected = point.lead_time_hours === selectedLeadHours;
          let badgeColor = "bg-slate-800 text-slate-300 border-slate-700";
          if (point.overall_severity === "EXTREME") {
            badgeColor = "bg-rose-950 text-rose-300 border-rose-800";
          } else if (point.overall_severity === "HIGH") {
            badgeColor = "bg-orange-950 text-orange-300 border-orange-800";
          } else if (point.overall_severity === "MODERATE") {
            badgeColor = "bg-amber-950 text-amber-300 border-amber-800";
          } else if (point.overall_severity === "LOW" || point.overall_severity === "VERY_LOW") {
            badgeColor = "bg-emerald-950 text-emerald-300 border-emerald-800";
          }

          return (
            <button
              key={point.lead_time_hours}
              onClick={() => onSelectHorizon(point.lead_time_hours)}
              className={`p-2 rounded border text-center transition flex flex-col items-center justify-between ${
                isSelected
                  ? "bg-sky-950/80 border-sky-400 text-white shadow-md shadow-sky-950"
                  : "bg-slate-950/70 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <span className={`text-[11px] font-bold ${isSelected ? "text-sky-300" : ""}`}>
                {point.label}
              </span>
              <span className="text-[10px] text-cyan-300 font-black my-0.5">
                {point.projected_rainfall_mm_h} mm/h
              </span>
              <span className={`text-[9px] px-1 py-0.2 rounded border font-sans font-bold ${badgeColor}`}>
                Score {point.max_flood_risk_score.toFixed(0)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Provenance and Guidance Note */}
      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/80">
        <span className="flex items-center gap-1 text-slate-400">
          <TrendingUp className="w-3 h-3 text-sky-400" />
          Projections dampen over lead times (USDA NRCS & NWP dampening); uncalibrated Flood Risk Score (0–100).
        </span>
        <span className="text-cyan-400 font-bold">
          {currentPoint?.provenance === "OBSERVED" ? "● LIVE OBSERVATION" : "▲ MODEL NOWCAST PREDICTION"}
        </span>
      </div>
    </div>
  );
}
