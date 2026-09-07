"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { FloodHotspot, PointInspectionResult } from "@/types/flood";
import { inspectLocationPoint } from "@/services/api";
import { Layers, Info, MapPin, AlertCircle, Waves, Timer } from "lucide-react";
import { ProvenanceBadge } from "../Common/ProvenanceBadge";

// Dynamically import Leaflet components to avoid SSR window errors
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const Polygon = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polygon),
  { ssr: false }
);
const Polyline = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polyline),
  { ssr: false }
);
const CircleMarker = dynamic(
  () => import("react-leaflet").then((mod) => mod.CircleMarker),
  { ssr: false }
);
const Popup = dynamic(
  () => import("react-leaflet").then((mod) => mod.Popup),
  { ssr: false }
);

interface Props {
  hotspots: FloodHotspot[];
  boundaryGeoJson?: any;
  roadsGeoJson?: any;
}

export const FloodMap: React.FC<Props> = ({
  hotspots,
  boundaryGeoJson,
  roadsGeoJson,
}) => {
  const [mounted, setMounted] = useState(false);
  const [showBoundary, setShowBoundary] = useState(true);
  const [showRoads, setShowRoads] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [selectedPoint, setSelectedPoint] = useState<PointInspectionResult | null>(null);
  const [isInspecting, setIsInspecting] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-full min-h-[480px] bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-center text-xs text-slate-500 font-mono">
        Initializing Geospatial GIS Viewer...
      </div>
    );
  }

  // LPU Centroid
  const centerLat = 31.2533;
  const centerLon = 75.7033;

  // Extract boundary coordinates if available
  let boundaryCoords: [number, number][] = [];
  if (boundaryGeoJson && boundaryGeoJson.features && boundaryGeoJson.features.length > 0) {
    const rawCoords = boundaryGeoJson.features[0].geometry.coordinates[0];
    boundaryCoords = rawCoords.map((c: [number, number]) => [c[1], c[0]]);
  }

  // Extract road coordinates
  let roadCoords: [number, number][] = [];
  if (roadsGeoJson && roadsGeoJson.features && roadsGeoJson.features.length > 0) {
    const rawCoords = roadsGeoJson.features[0].geometry.coordinates;
    roadCoords = rawCoords.map((c: [number, number]) => [c[1], c[0]]);
  }

  const handleInspect = async (lat: number, lon: number) => {
    setIsInspecting(true);
    try {
      const res = await inspectLocationPoint(lat, lon);
      setSelectedPoint(res);
    } catch (err) {
      console.error("Inspection error:", err);
    } finally {
      setIsInspecting(false);
    }
  };

  return (
    <div className="relative w-full h-full min-h-[520px] rounded-lg overflow-hidden border border-slate-800 shadow-xl bg-slate-950 flex flex-col">
      {/* Top Banner: Scientific Honesty & Drainage Status */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs z-10 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-200">Geographic Extent:</span>
          <span className="text-slate-400">Lovely Professional University & NH-44 Grand Trunk Road</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono bg-amber-950/90 text-amber-300 px-2 py-0.5 rounded border border-amber-800 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Drainage: NOT AVAILABLE (Terrain Susceptibility Mode)
          </span>
        </div>
      </div>

      {/* Interactive Map */}
      <div className="relative flex-1 w-full h-full">
        <MapContainer
          center={[centerLat, centerLon]}
          zoom={15}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          {/* CartoDB Dark Matter base tile layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {/* Verified LPU Campus Boundary Polygon */}
          {showBoundary && boundaryCoords.length > 0 && (
            <Polygon
              positions={boundaryCoords}
              pathOptions={{
                color: "#3b82f6",
                weight: 2,
                dashArray: "4, 6",
                fillColor: "#3b82f6",
                fillOpacity: 0.1,
              }}
            >
              <Popup>
                <div className="p-1 font-sans text-xs">
                  <div className="font-bold text-slate-100 mb-0.5">Lovely Professional University</div>
                  <div className="text-slate-400">Verified Campus Boundary (OSM Way 422435593)</div>
                  <div className="text-[10px] text-slate-500 font-mono mt-1">Area: ~600 Acres | Elevation: ~238m</div>
                </div>
              </Popup>
            </Polygon>
          )}

          {/* NH-44 Highway Road Segment */}
          {showRoads && roadCoords.length > 0 && (
            <Polyline
              positions={roadCoords}
              pathOptions={{
                color: "#f59e0b",
                weight: 4,
                opacity: 0.8,
              }}
            >
              <Popup>
                <div className="p-1 font-sans text-xs">
                  <div className="font-bold text-slate-100 mb-0.5">NH-44 (Grand Trunk Road)</div>
                  <div className="text-slate-400">National Highway corridor adjacent to LPU</div>
                  <div className="text-[10px] text-amber-400 font-mono mt-1">Critical low point: Underpass near Gate 1</div>
                </div>
              </Popup>
            </Polyline>
          )}

          {/* Flood Hotspots */}
          {showHotspots &&
            hotspots.map((h) => {
              let markerColor = "#10b981"; // Very Low / Low
              let radius = 9;
              if (h.risk_category === "EXTREME") {
                markerColor = "#ef4444";
                radius = 16;
              } else if (h.risk_category === "HIGH") {
                markerColor = "#f97316";
                radius = 14;
              } else if (h.risk_category === "MODERATE") {
                markerColor = "#f59e0b";
                radius = 11;
              }

              return (
                <CircleMarker
                  key={h.id}
                  center={[h.latitude, h.longitude]}
                  radius={radius}
                  pathOptions={{
                    color: "#ffffff",
                    weight: 1.5,
                    fillColor: markerColor,
                    fillOpacity: 0.85,
                  }}
                  eventHandlers={{
                    click: () => handleInspect(h.latitude, h.longitude),
                  }}
                >
                  <Popup>
                    <div className="p-1.5 font-sans text-xs space-y-1.5 min-w-[220px]">
                      <div className="flex items-center justify-between border-b border-slate-700 pb-1">
                        <span className="font-bold text-white text-xs">{h.location_name}</span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold uppercase font-mono ${
                          h.risk_category === "EXTREME" ? "bg-rose-950 text-rose-300" :
                          h.risk_category === "HIGH" ? "bg-orange-950 text-orange-300" :
                          h.risk_category === "MODERATE" ? "bg-amber-950 text-amber-300" : "bg-emerald-950 text-emerald-300"
                        }`}>
                          {h.risk_category}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono py-1">
                        <div>
                          <span className="text-slate-400 block text-[10px]">Risk Score:</span>
                          <span className="text-white font-bold">{h.flood_risk_score.toFixed(0)} / 100</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Est. Depth:</span>
                          <span className="text-cyan-300 font-bold">{h.estimated_depth_bracket}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Time-to-Flood:</span>
                          <span className="text-amber-300 font-bold">{h.estimated_time_to_flood}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Elevation:</span>
                          <span className="text-slate-200">{h.elevation_m ? `${h.elevation_m}m` : "—"}</span>
                        </div>
                      </div>

                      <div className="pt-1 border-t border-slate-700 text-[10px] text-amber-400/90 font-mono">
                        [MODEL ESTIMATE — Uncalibrated]
                      </div>

                      <button
                        onClick={() => handleInspect(h.latitude, h.longitude)}
                        className="w-full mt-1 px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold rounded text-center transition"
                      >
                        Inspect Hydrological Analysis
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
        </MapContainer>

        {/* Floating Layer Controls */}
        <div className="absolute top-4 right-4 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-3 shadow-lg text-xs space-y-2">
          <div className="flex items-center gap-2 font-bold text-slate-200 border-b border-slate-800 pb-1.5">
            <Layers className="w-3.5 h-3.5 text-sky-400" />
            <span>GIS Map Layers</span>
          </div>

          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={showHotspots}
              onChange={(e) => setShowHotspots(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
            />
            <span>Flood Risk Hotspots</span>
          </label>

          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={showBoundary}
              onChange={(e) => setShowBoundary(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
            />
            <span>OSM Campus Boundary</span>
          </label>

          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={showRoads}
              onChange={(e) => setShowRoads(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
            />
            <span>NH-44 Highway Corridor</span>
          </label>
        </div>

        {/* Map Legend */}
        <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-3 shadow-lg text-[11px] font-mono space-y-1.5">
          <div className="font-bold text-slate-300 font-sans text-xs border-b border-slate-800 pb-1">
            Flood Risk Score Legend
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>0 – 20: Very Low / Low</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span>40 – 60: Moderate Risk</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            <span>60 – 80: High Hazard</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>80 – 100: Extreme Inundation</span>
          </div>
        </div>
      </div>

      {/* Point Inspector Drawer / Modal */}
      {selectedPoint && (
        <div className="border-t border-slate-800 bg-slate-950 p-4 text-xs font-sans">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-sky-400" />
              <span className="font-bold text-white text-sm">
                Point Hydrology Inspection: {selectedPoint.location_label}
              </span>
            </div>
            <button
              onClick={() => setSelectedPoint(null)}
              className="text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 font-mono">
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Elevation</span>
              <span className="text-white font-bold">{selectedPoint.elevation_m} m</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Slope Gradient</span>
              <span className="text-white font-bold">{selectedPoint.slope_deg}°</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Topography</span>
              <span className={`font-bold ${selectedPoint.is_depression ? "text-amber-400" : "text-slate-300"}`}>
                {selectedPoint.is_depression ? "Depression" : "Conveying"}
              </span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Curve Number (CN)</span>
              <span className="text-white font-bold">{selectedPoint.curve_number}</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">SCS Runoff Depth</span>
              <span className="text-sky-300 font-bold">{selectedPoint.runoff_depth_mm} mm</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Flood Risk Score</span>
              <span className="text-amber-400 font-bold">{selectedPoint.flood_risk_score.toFixed(0)} / 100</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Peak Est. Depth</span>
              <span className="text-cyan-300 font-bold">{selectedPoint.estimated_depth_bracket}</span>
            </div>
            <div className="bg-slate-900 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-500 block">Est. Time-to-Flood</span>
              <span className="text-orange-300 font-bold">{selectedPoint.estimated_time_to_flood}</span>
            </div>
          </div>

          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1 text-amber-400/90 font-mono">
              <AlertCircle className="w-3.5 h-3.5" />
              Depths and time-to-flood are model estimates based on SCS-CN; not verified sensor readings.
            </span>
            <ProvenanceBadge provenance={selectedPoint.provenance} size="sm" />
          </div>
        </div>
      )}
    </div>
  );
};
