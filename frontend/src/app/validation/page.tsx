"use client";

import React, { useEffect, useState } from "react";
import { fetchValidationMetrics } from "@/services/api";
import { CheckSquare, AlertCircle, PlusCircle, ShieldCheck, Database, FileCheck } from "lucide-react";

export default function ValidationPage() {
  const [validationData, setValidationData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchValidationMetrics()
      .then(setValidationData)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
          <CheckSquare className="w-6 h-6 text-emerald-400" />
          Model Scientific Validation & Ground-Truth Verification
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Empirical backtesting against verified sensor readings and documented municipal disaster logs
        </p>
      </div>

      {/* Zero Fabrication Integrity Statement */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
        <div className="flex items-center gap-2 font-bold text-slate-200 text-xs">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Scientific Integrity Guarantee (SIH 2026 Core Principle)</span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          In strict accordance with scientific standards, this platform does <strong>NOT generate fake accuracy statistics</strong> (e.g. &ldquo;95% accuracy&rdquo;) in the absence of genuine ground-truth field measurements. Validation metrics (Precision, Recall, F1, Depth MAE, RMSE) are calculated solely when empirical water depth observations from verified sources are logged.
        </p>
      </div>

      {/* Validation Status Block */}
      {validationData && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-sky-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Ground-Truth Dataset Status
              </span>
            </div>
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
                validationData.validation_status === "INSUFFICIENT_GROUND_TRUTH"
                  ? "bg-amber-950 text-amber-300 border-amber-800"
                  : "bg-emerald-950 text-emerald-300 border-emerald-800"
              }`}
            >
              {validationData.validation_status}
            </span>
          </div>

          <div className="flex items-center gap-3 p-4 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <div>
              <div className="font-bold text-slate-200">
                Total Ground-Truth Events in Database: {validationData.total_events_recorded}
              </div>
              <div className="text-slate-400 mt-0.5">{validationData.message}</div>
            </div>
          </div>

          {/* If no events, show protocol for logging */}
          {validationData.total_events_recorded === 0 && (
            <div className="p-4 bg-slate-950/50 rounded-lg border border-slate-800 text-xs text-slate-400 space-y-2">
              <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[11px]">
                Ground-Truth Ingestion Protocol:
              </h4>
              <ol className="list-decimal list-inside space-y-1 text-slate-400 font-mono text-[11px]">
                <li>Deploy ultrasonic water-level sensors at critical low points (e.g. NH-44 Underpass).</li>
                <li>Record time-series stage elevation (depth in meters) during monsoon rain events.</li>
                <li>Import municipal flood observation logs from DDMA Kapurthala / Jalandhar.</li>
                <li>Trigger automated backtesting against nowcasting model runs.</li>
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
