"use client";

import React, { useEffect, useState } from "react";
import { fetchValidationMetrics } from "@/services/api";
import { CheckSquare, AlertCircle, ShieldCheck, Database, Satellite, CheckCircle, BarChart3 } from "lucide-react";

export default function ValidationPage() {
  const [validationData, setValidationData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchValidationMetrics()
      .then(setValidationData)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const metrics = validationData?.metrics;
  const matrix = metrics?.confusion_matrix;
  const events = validationData?.events || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
          <CheckSquare className="w-6 h-6 text-emerald-400" />
          Model Scientific Validation &amp; Remote-Sensing Observation Data
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Empirical backtesting against ISRO/NRSC NDEM flood reports and Sentinel-1 SAR observations across 3 independent historical events (Aug 2019, Aug 2020, July 2023)
        </p>
      </div>

      {/* Zero Fabrication Integrity Statement */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
        <div className="flex items-center gap-2 font-bold text-slate-200 text-xs">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Scientific Integrity Guarantee (SIH 2026 Core Principle)</span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          In strict accordance with scientific standards, this platform does <strong>NOT fabricate synthetic accuracy numbers</strong>. Validation is conducted against documented satellite-observed flood extents (ISRO/NRSC Disaster Management Support Programme &amp; Copernicus Sentinel-1 SAR) across Kapurthala, Jalandhar, Phagwara, and the LPU corridor across <strong>three independent historical events</strong> (August 2019 Sutlej deluge, August 2020 cloudburst, July 2023 monsoonal flood). Includes real-world failure cases (emergency pumping false alarms and debris-choked culvert misses).
        </p>
      </div>

      {/* Metrics Overview Cards */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Precision</span>
            <span className="text-2xl font-black text-emerald-400 font-mono">
              {(metrics.precision * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">TP / (TP + FP)</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Recall (Sensitivity)</span>
            <span className="text-2xl font-black text-cyan-400 font-mono">
              {(metrics.recall * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">TP / (TP + FN)</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">F1-Score</span>
            <span className="text-2xl font-black text-purple-400 font-mono">
              {metrics.f1_score.toFixed(2)}
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">Harmonic mean</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Satellite Dataset</span>
            <span className="text-2xl font-black text-white font-mono">
              {validationData.total_events_recorded} Points
            </span>
            <span className="text-[10px] text-emerald-400 block mt-1 font-mono">3 Historical Events (2019–2023)</span>
          </div>
        </div>
      )}

      {/* Contingency Matrix (2x2) */}
      {matrix && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <BarChart3 className="w-4 h-4 text-sky-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Contingency Matrix (Confusion Matrix)
            </h3>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-center">
            <div className="bg-emerald-950/40 border border-emerald-800/80 p-3 rounded-lg">
              <span className="text-xs text-emerald-300 block">True Positives (TP)</span>
              <span className="text-xl font-bold text-white">{matrix.true_positive}</span>
              <span className="text-[10px] text-slate-400 block">Correctly Predicted Flooded</span>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
              <span className="text-xs text-amber-300 block">False Positives (FP)</span>
              <span className="text-xl font-bold text-white">{matrix.false_positive}</span>
              <span className="text-[10px] text-slate-400 block">False Alarm (Over-predicted)</span>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-3 rounded-lg">
              <span className="text-xs text-rose-300 block">False Negatives (FN)</span>
              <span className="text-xl font-bold text-white">{matrix.false_negative}</span>
              <span className="text-[10px] text-slate-400 block">Missed Flood Event</span>
            </div>
            <div className="bg-blue-950/40 border border-blue-800/80 p-3 rounded-lg">
              <span className="text-xs text-blue-300 block">True Negatives (TN)</span>
              <span className="text-xl font-bold text-white">{matrix.true_negative}</span>
              <span className="text-[10px] text-slate-400 block">Correctly Predicted Dry</span>
            </div>
          </div>
        </div>
      )}

      {/* Satellite-Observed Points Table */}
      {events.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Satellite className="w-4 h-4 text-sky-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Satellite-Observed Flood Extents (August 2019, August 2020, July 2023 Events)
              </h3>
            </div>
            <span className="text-[10px] font-mono text-emerald-400">
              Sentinel-1 SAR C-Band &amp; NRSC NDEM
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                  <th className="py-2 px-3">Location</th>
                  <th className="py-2 px-3">Observed Flooded</th>
                  <th className="py-2 px-3">Predicted Risk</th>
                  <th className="py-2 px-3">Est. Depth</th>
                  <th className="py-2 px-3">Evidence Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {events.map((ev: any) => (
                  <tr key={ev.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{ev.location_name}</td>
                    <td className="py-2.5 px-3">
                      {ev.observed_flooded ? (
                        <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-rose-950 text-rose-300 border border-rose-800">
                          FLOODED
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800">
                          DRY / SAFE
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-amber-300">
                      {ev.predicted_risk_score.toFixed(0)} / 100
                    </td>
                    <td className="py-2.5 px-3 font-mono text-cyan-300">
                      {ev.observed_depth_bracket || ev.predicted_depth_bracket}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400">
                      {ev.ground_truth_source}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
