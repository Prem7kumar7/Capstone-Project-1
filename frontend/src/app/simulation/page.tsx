"use client";

import React, { useState } from "react";
import { runSimulationScenario } from "@/services/api";
import { FloodPredictionRun } from "@/types/flood";
import { KpiCards } from "@/components/Dashboard/KpiCards";
import { FloodMap } from "@/components/Map/FloodMap";
import { AlertsFeed } from "@/components/Dashboard/AlertsFeed";
import { fetchBoundaryGeoJson, fetchRoadsGeoJson } from "@/services/api";
import { Sliders, Play, AlertTriangle, Info, Sparkles, RefreshCw } from "lucide-react";

export default function SimulationPage() {
  const [intensity, setIntensity] = useState(65.0); // mm/h
  const [cumulative, setCumulative] = useState(110.0); // mm
  const [duration, setDuration] = useState(3.0); // hours
  const [clogging, setClogging] = useState(40.0); // %
  const [scenarioName, setScenarioName] = useState("Intense Monsoon Cloudburst (Stress Test)");
  const [results, setResults] = useState<FloodPredictionRun | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [boundaryGeoJson, setBoundaryGeoJson] = useState<any>(null);
  const [roadsGeoJson, setRoadsGeoJson] = useState<any>(null);

  React.useEffect(() => {
    Promise.all([fetchBoundaryGeoJson(), fetchRoadsGeoJson()])
      .then(([b, r]) => {
        setBoundaryGeoJson(b);
        setRoadsGeoJson(r);
      })
      .catch(console.error);

    // Run initial baseline simulation scenario
    handleRunSimulation();
  }, []);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    try {
      const res = await runSimulationScenario({
        study_area_id: "lpu_main_campus",
        rainfall_intensity_mm_h: intensity,
        cumulative_rainfall_mm: cumulative,
        storm_duration_hours: duration,
        drainage_clogging_pct: clogging,
        scenario_label: scenarioName
      });
      setResults(res.results);
    } catch (err) {
      console.error("Simulation run error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  const handlePreset = (presetName: string, pInt: number, pCum: number, pDur: number, pClog: number) => {
    setScenarioName(presetName);
    setIntensity(pInt);
    setCumulative(pCum);
    setDuration(pDur);
    setClogging(pClog);
  };

  return (
    <div className="space-y-5">
      {/* MANDATORY SIMULATION DISCLAIMER BANNER */}
      <div className="p-4 bg-amber-950/40 border-2 border-amber-600/70 rounded-xl text-amber-200 flex items-start gap-3 shadow-lg">
        <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-amber-300">
            SIMULATION MODE — VALUES ARE SYNTHETIC AND ARE NOT REAL OBSERVATIONS
          </h2>
          <p className="text-xs text-amber-200/90 mt-1 leading-relaxed">
            This module evaluates the response of the <strong>SCS-CN runoff and terrain depression accumulation pipeline</strong> under hypothetical extreme weather and drainage failure conditions. No real-time sensors are being reported here.
          </p>
        </div>
      </div>

      {/* Interactive Scenario Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-amber-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Hydrological Scenario Parameters
            </h3>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 text-[11px]">Presets:</span>
            <button
              onClick={() => handlePreset("July 2023 Historic Storm Repeat", 45.0, 140.0, 4.0, 30.0)}
              className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-[10px]"
            >
              July 2023 Storm
            </button>
            <button
              onClick={() => handlePreset("Severe 100mm/h Cloudburst with Clogged Drains", 95.0, 160.0, 2.0, 75.0)}
              className="px-2 py-1 bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 rounded border border-rose-800 text-[10px]"
            >
              Extreme Cloudburst (75% Clog)
            </button>
            <button
              onClick={() => handlePreset("Normal Monsoon Shower", 20.0, 35.0, 2.0, 10.0)}
              className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-[10px]"
            >
              Normal Rain
            </button>
          </div>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
          {/* Slider 1: Rainfall Intensity */}
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="flex justify-between text-slate-300">
              <span className="font-sans font-semibold">Rainfall Intensity</span>
              <span className="text-sky-400 font-bold">{intensity} mm/h</span>
            </div>
            <input
              type="range"
              min="0"
              max="150"
              step="5"
              value={intensity}
              onChange={(e) => setIntensity(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 (Dry)</span>
              <span>80 (Cloudburst)</span>
              <span>150 (Catastrophic)</span>
            </div>
          </div>

          {/* Slider 2: Cumulative Rainfall */}
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="flex justify-between text-slate-300">
              <span className="font-sans font-semibold">Cumulative Storm Rain</span>
              <span className="text-indigo-400 font-bold">{cumulative} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="300"
              step="10"
              value={cumulative}
              onChange={(e) => setCumulative(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 mm</span>
              <span>150 mm (Heavy)</span>
              <span>300 mm (Flood)</span>
            </div>
          </div>

          {/* Slider 3: Storm Duration */}
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="flex justify-between text-slate-300">
              <span className="font-sans font-semibold">Storm Duration</span>
              <span className="text-amber-400 font-bold">{duration} hours</span>
            </div>
            <input
              type="range"
              min="1"
              max="8"
              step="0.5"
              value={duration}
              onChange={(e) => setDuration(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>1 hr (Flash)</span>
              <span>4 hrs</span>
              <span>8 hrs (Prolonged)</span>
            </div>
          </div>

          {/* Slider 4: Drainage Clogging */}
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2">
            <div className="flex justify-between text-slate-300">
              <span className="font-sans font-semibold">Drainage Clogging</span>
              <span className="text-rose-400 font-bold">{clogging}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={clogging}
              onChange={(e) => setClogging(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0% (Clean)</span>
              <span>50% (Choked)</span>
              <span>100% (Blocked)</span>
            </div>
          </div>
        </div>

        {/* Execution Trigger */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-400 font-mono">
            Active Scenario: <span className="text-slate-200 font-sans font-semibold">{scenarioName}</span>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isRunning}
            className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-2 shadow-lg transition"
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Computing Runoff & Flood Model...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run Hydrological Simulation
              </>
            )}
          </button>
        </div>
      </div>

      {/* Simulation Results KPIs */}
      {results && (
        <div className="space-y-5">
          <KpiCards
            weather={{
              study_area_id: "lpu_main_campus",
              timestamp_utc: results.run_timestamp_utc,
              timestamp_ist: results.run_timestamp_ist,
              temperature_c: 28.0,
              relative_humidity_pct: 90.0,
              precipitation_mm_h: results.current_rainfall_mm_h,
              rain_mm: results.current_rainfall_mm_h,
              wind_speed_kmh: 15.0,
              weather_code: 65,
              weather_condition: "Synthetic Simulation",
              data_source: "Synthetic Scenario Generator",
              provenance: "SIMULATED",
              status: "SIMULATED"
            }}
            floodRun={results}
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="lg:col-span-2">
              <FloodMap
                hotspots={results.hotspots}
                boundaryGeoJson={boundaryGeoJson}
                roadsGeoJson={roadsGeoJson}
              />
            </div>

            <div>
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Simulation Emergency Advisories
                  </h3>
                  <span className="text-[10px] font-mono text-amber-400">
                    [SYNTHETIC]
                  </span>
                </div>
                <AlertsFeed
                  alerts={results.hotspots.map((h, i) => ({
                    id: `SIM-ALT-${i}`,
                    study_area_id: "lpu_main_campus",
                    alert_level: (h.risk_category === "EXTREME" ? "RED" : h.risk_category === "HIGH" ? "ORANGE" : h.risk_category === "MODERATE" ? "YELLOW" : "GREEN") as any,
                    headline: `SIMULATED ADVISORY: ${h.location_name}`,
                    location_name: h.location_name,
                    forecast_rainfall_summary: `Simulation: ${intensity} mm/h | Total: ${cumulative} mm`,
                    flood_risk_score: h.flood_risk_score,
                    estimated_depth_bracket: h.estimated_depth_bracket,
                    estimated_time_to_impact: h.estimated_time_to_flood,
                    recommended_actions: "SIMULATED RESPONSE: Evacuate low-lying underpasses. Check pump capacity.",
                    data_source: "Hydrological Simulation Model",
                    provenance: "SIMULATED",
                    issued_at_ist: results.run_timestamp_ist,
                    is_simulation: true
                  }))}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
