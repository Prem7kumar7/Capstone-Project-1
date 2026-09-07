"use client";

import React, { useEffect, useState } from "react";
import {
  WeatherCurrent,
  WeatherForecast,
  FloodPredictionRun,
  AlertAdvisory,
  SystemHealth,
  NowcastHorizonPoint
} from "@/types/flood";
import {
  fetchCurrentWeather,
  fetchWeatherForecast,
  fetchCurrentFloodRisk,
  fetchActiveAlerts,
  fetchSystemHealth,
  fetchBoundaryGeoJson,
  fetchRoadsGeoJson,
  fetchWaterwaysGeoJson,
  fetchInfrastructureGeoJson,
  fetchNowcastTimeline
} from "@/services/api";
import { RegionSelector } from "@/components/Common/RegionSelector";
import { NowcastTimelineSlider } from "@/components/Dashboard/NowcastTimelineSlider";
import { KpiCards } from "@/components/Dashboard/KpiCards";
import { RainfallChart } from "@/components/Dashboard/RainfallChart";
import { AlertsFeed } from "@/components/Dashboard/AlertsFeed";
import { FloodMap } from "@/components/Map/FloodMap";
import { DataHealthModal } from "@/components/Common/DataHealthModal";
import { Activity, RefreshCw, AlertTriangle, ShieldCheck } from "lucide-react";

export default function DashboardPage() {
  const [selectedRegion, setSelectedRegion] = useState<string>("lpu_main_campus");
  const [selectedLeadHours, setSelectedLeadHours] = useState<number>(0.0);
  const [weather, setWeather] = useState<WeatherCurrent | null>(null);
  const [forecast, setForecast] = useState<WeatherForecast | null>(null);
  const [floodRun, setFloodRun] = useState<FloodPredictionRun | null>(null);
  const [timeline, setTimeline] = useState<NowcastHorizonPoint[]>([]);
  const [alerts, setAlerts] = useState<AlertAdvisory[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [boundaryGeoJson, setBoundaryGeoJson] = useState<any>(null);
  const [roadsGeoJson, setRoadsGeoJson] = useState<any>(null);
  const [waterwaysGeoJson, setWaterwaysGeoJson] = useState<any>(null);
  const [infrastructureGeoJson, setInfrastructureGeoJson] = useState<any>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isHealthModalOpen, setIsHealthModalOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadDataForRegion = async (regionId: string, leadHours: number = 0.0) => {
    setErrorMsg(null);
    try {
      const [w, f, r, tl, a, h, b, rd, wt, inf] = await Promise.allSettled([
        fetchCurrentWeather(),
        fetchWeatherForecast(),
        fetchCurrentFloodRisk(regionId, leadHours),
        fetchNowcastTimeline(regionId),
        fetchActiveAlerts(false),
        fetchSystemHealth(),
        fetchBoundaryGeoJson(regionId),
        fetchRoadsGeoJson(regionId),
        fetchWaterwaysGeoJson(),
        fetchInfrastructureGeoJson(regionId)
      ]);

      if (w.status === "fulfilled") setWeather(w.value);
      if (f.status === "fulfilled") setForecast(f.value);
      if (r.status === "fulfilled") setFloodRun(r.value);
      if (tl.status === "fulfilled" && tl.value.forecast_horizons) {
        setTimeline(tl.value.forecast_horizons);
      }
      if (a.status === "fulfilled") setAlerts(a.value);
      if (h.status === "fulfilled") setHealth(h.value);
      if (b.status === "fulfilled") setBoundaryGeoJson(b.value);
      if (rd.status === "fulfilled") setRoadsGeoJson(rd.value);
      if (wt.status === "fulfilled") setWaterwaysGeoJson(wt.value);
      if (inf.status === "fulfilled") setInfrastructureGeoJson(inf.value);
    } catch (err: any) {
      console.error("Dashboard data fetch error:", err);
      setErrorMsg("Failed to connect to flood nowcasting backend service.");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadDataForRegion(selectedRegion, selectedLeadHours);
    // Periodic background refresh every 5 minutes
    const interval = setInterval(() => {
      loadDataForRegion(selectedRegion, selectedLeadHours);
    }, 300000);
    return () => clearInterval(interval);
  }, [selectedRegion]);

  const handleRegionChange = (newRegionId: string) => {
    setSelectedRegion(newRegionId);
    setSelectedLeadHours(0.0);
    setIsRefreshing(true);
    loadDataForRegion(newRegionId, 0.0);
  };

  const handleHorizonChange = async (leadHours: number) => {
    setSelectedLeadHours(leadHours);
    try {
      const updatedRisk = await fetchCurrentFloodRisk(selectedRegion, leadHours);
      setFloodRun(updatedRisk);
    } catch (err) {
      console.error("Failed updating nowcast horizon risk:", err);
    }
  };

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    loadDataForRegion(selectedRegion, selectedLeadHours);
  };

  return (
    <div className="space-y-5">
      {/* 1. Multi-Region Selector Bar */}
      <RegionSelector
        selectedRegion={selectedRegion}
        onSelectRegion={handleRegionChange}
      />

      {/* 2. Sub-Header / Status Bar */}
      <div className="flex flex-wrap items-center justify-between bg-slate-900 border border-slate-800 p-3.5 rounded-lg gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs font-bold font-mono tracking-wider text-white">
              {selectedLeadHours === 0.0 ? "LIVE MONITORING MODE" : `NOWCAST FORECAST (+${selectedLeadHours}h)`}
            </span>
          </div>
          <span className="text-slate-500 text-xs">|</span>
          <span className="text-xs text-slate-400">
            Selected Basin: <strong className="text-slate-200 capitalize">{selectedRegion.replace(/_/g, " ")}</strong>
          </span>
          {weather?.timestamp_ist && (
            <span className="text-xs text-slate-500 font-mono hidden md:inline">
              (Observation: {weather.timestamp_ist})
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Data Health Trigger Button */}
          <button
            onClick={() => setIsHealthModalOpen(true)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-md border border-slate-700 flex items-center gap-1.5 transition"
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            Data Source Health
          </button>

          {/* Manual Refresh */}
          <button
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md border border-slate-700 transition"
            title="Refresh Live Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-sky-400" : ""}`} />
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 bg-red-950/40 border border-red-800 rounded-lg text-xs text-red-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 3. 0-6 Hour Nowcasting Timeline Slider */}
      {timeline.length > 0 && (
        <NowcastTimelineSlider
          timeline={timeline}
          selectedLeadHours={selectedLeadHours}
          onSelectHorizon={handleHorizonChange}
          baseRainfall={weather?.precipitation_mm_h || 0}
        />
      )}

      {/* 4. KPI Cards Row */}
      <KpiCards weather={weather} floodRun={floodRun} />

      {/* 5. Main Map + Side Panel Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left 2 Cols: Interactive Leaflet GIS Map */}
        <div className="lg:col-span-2">
          <FloodMap
            hotspots={floodRun?.hotspots || []}
            boundaryGeoJson={boundaryGeoJson}
            roadsGeoJson={roadsGeoJson}
            waterwaysGeoJson={waterwaysGeoJson}
            infrastructureGeoJson={infrastructureGeoJson}
            regionId={selectedRegion}
          />
        </div>

        {/* Right 1 Col: Rainfall Chart & Quick Advisories */}
        <div className="space-y-5">
          <RainfallChart forecast={forecast} />

          {/* Quick Advisories Box */}
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Active Emergency Advisories
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                {alerts.length} Location Notices
              </span>
            </div>
            <div className="max-h-64 overflow-y-auto pr-1">
              <AlertsFeed alerts={alerts.slice(0, 3)} />
            </div>
          </div>
        </div>
      </div>

      {/* 6. Data Health Diagnostic Modal */}
      <DataHealthModal
        isOpen={isHealthModalOpen}
        onClose={() => setIsHealthModalOpen(false)}
        health={health}
      />
    </div>
  );
}
