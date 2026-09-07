"use client";

import React, { useEffect, useState } from "react";
import { fetchHydrologyConfig, updateHydrologyConfig } from "@/services/api";
import { Settings, Save, CheckCircle2, Shield, FileText, Activity } from "lucide-react";

export default function AdminPage() {
  const [config, setConfig] = useState<any>(null);
  const [lambdaRatio, setLambdaRatio] = useState<number>(0.20);
  const [soilGroup, setSoilGroup] = useState<string>("B");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetchHydrologyConfig()
      .then((cfg) => {
        setConfig(cfg);
        if (cfg.initial_abstraction_ratio_lambda) {
          setLambdaRatio(cfg.initial_abstraction_ratio_lambda);
        }
        if (cfg.soil_hydrologic_group) {
          setSoilGroup(cfg.soil_hydrologic_group);
        }
      })
      .catch(console.error);
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await updateHydrologyConfig({
        soil_hydrologic_group: soilGroup,
        initial_abstraction_ratio_lambda: lambdaRatio,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error("Config save error:", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Settings className="w-6 h-6 text-sky-400" />
            Hydrological Calibration & Engineering Controls
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Data-driven SCS-CN coefficients, soil classifications, and hydraulic model coupler state
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-lg flex items-center gap-2 shadow-lg transition"
        >
          {saveSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              Parameters Saved
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Configuration
            </>
          )}
        </button>
      </div>

      {/* Grid of Configuration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
        {/* Card 1: SCS-CN Calibration */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 font-bold text-slate-200 border-b border-slate-800 pb-2">
            <FileText className="w-4 h-4 text-sky-400" />
            <span>SCS-CN Parameterization</span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-slate-400 block mb-1">Soil Hydrologic Group</label>
              <select
                value={soilGroup}
                onChange={(e) => setSoilGroup(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono focus:border-sky-500 focus:outline-none"
              >
                <option value="A">Group A (Deep sand, high infiltration &gt; 25 mm/h)</option>
                <option value="B">Group B (Silt loam / alluvial plains, moderate infiltration 12-25 mm/h - Active Punjab)</option>
                <option value="C">Group C (Clay loam, slow infiltration 2-12 mm/h)</option>
                <option value="D">Group D (Heavy clay / hardpan, very slow infiltration &lt; 2 mm/h)</option>
              </select>
            </div>

            <div>
              <label className="text-slate-400 block mb-1">
                Initial Abstraction Ratio (&lambda; in Ia = &lambda; &times; S)
              </label>
              <select
                value={lambdaRatio}
                onChange={(e) => setLambdaRatio(parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono focus:border-sky-500 focus:outline-none"
              >
                <option value={0.20}>&lambda; = 0.20 (Standard USDA NRCS default)</option>
                <option value={0.05}>&lambda; = 0.05 (Indian CWC / MoWR Subcontinental Standard for monsoon events)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">
                Central Water Commission (CWC) recommends &lambda; = 0.05 for Indian urban catchments where initial abstraction is reduced during monsoonal saturation.
              </p>
            </div>
          </div>
        </div>

        {/* Card 2: Curve Number Table View */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 font-bold text-slate-200 border-b border-slate-800 pb-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Active Land Cover Curve Numbers (CN)</span>
          </div>

          <div className="border border-slate-800 rounded-lg overflow-hidden">
            <table className="w-full text-left font-mono text-[11px]">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-semibold">
                <tr>
                  <th className="p-2.5">Land Cover Category</th>
                  <th className="p-2.5">CN</th>
                  <th className="p-2.5">Impervious %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {config?.curve_numbers &&
                  Object.entries(config.curve_numbers).map(([key, item]: any) => (
                    <tr key={key} className="hover:bg-slate-800/40">
                      <td className="p-2.5 font-sans text-slate-300">{item.description}</td>
                      <td className="p-2.5 font-bold text-sky-400">{item.cn_value}</td>
                      <td className="p-2.5 text-slate-400">{(item.impervious_fraction * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Card 3: EPA SWMM Coupler Module State */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              EPA SWMM Hydraulic Coupler State
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700">
              DORMANT
            </span>
          </div>

          <p className="text-slate-400 text-xs leading-relaxed">
            The EPA SWMM 1D/2D hydraulic pipe engine remains dormant to prevent scientific fabrication.
            To activate true conduit and junction hydraulics, upload an official campus storm sewer network model file (<code className="text-sky-300">.inp</code>) containing verified invert elevations and pipe diameters.
          </p>

          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-400">
            Current fallback active: <strong>Simplified Runoff & Terrain Susceptibility Model</strong>
          </div>
        </div>

        {/* Card 4: Advanced Spatial Nowcasting State */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200 flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-400" />
              Doppler Weather Radar / Optical Flow Engine
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700">
              AWAITING RADAR FEED
            </span>
          </div>

          <p className="text-slate-400 text-xs leading-relaxed">
            The semi-Lagrangian advection and optical flow nowcasting engine is architecturally decoupled.
            It awaits a live Doppler Weather Radar (DWR) polar volume stream (e.g. IMD Patiala/Amritsar radar) before switching from NWP point extrapolation to spatial advection tracking.
          </p>
        </div>
      </div>
    </div>
  );
}
