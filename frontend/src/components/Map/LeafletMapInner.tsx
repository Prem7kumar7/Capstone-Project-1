"use client";

import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  Polyline,
  CircleMarker,
  Popup,
  Tooltip,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { FloodHotspot, PointInspectionResult } from "@/types/flood";
import { inspectLocationPoint } from "@/services/api";
import { Layers, MapPin, AlertCircle, Compass, Eye, ShieldAlert, Navigation } from "lucide-react";
import { ProvenanceBadge } from "../Common/ProvenanceBadge";

interface Props {
  hotspots: FloodHotspot[];
  boundaryGeoJson?: any;
  roadsGeoJson?: any;
}

// Map Controller for programmatic flyTo / setView
function MapViewController({
  center,
  zoom,
}: {
  center: [number, number];
  zoom: number;
}) {
  const map = useMap();
  useEffect(() => {
    if (map) {
      map.setView(center, zoom, { animate: true });
    }
  }, [map, center, zoom]);
  return null;
}

// Map Click Handler for point-based hydrological inspection
function MapClickHandler({
  onMapClick,
}: {
  onMapClick: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function LeafletMapInner({
  hotspots,
  boundaryGeoJson,
  roadsGeoJson,
}: Props) {
  const [basemapType, setBasemapType] = useState<"osm" | "satellite" | "topo">("osm");
  const [showBoundary, setShowBoundary] = useState(true);
  const [showRoads, setShowRoads] = useState(true);
  const [showHotspots, setShowHotspots] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [mapCenter, setMapCenter] = useState<[number, number]>([31.2533, 75.7033]);
  const [mapZoom, setMapZoom] = useState<number>(16.2); // Focused directly on LPU Campus
  const [selectedPoint, setSelectedPoint] = useState<PointInspectionResult | null>(null);
  const [isInspecting, setIsInspecting] = useState(false);

  // Extract boundary coordinates
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
      console.error("Point inspection failed:", err);
    } finally {
      setIsInspecting(false);
    }
  };

  // Watermark-free tile definitions
  let tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  let tileAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
  let maxZoom = 19;

  if (basemapType === "satellite") {
    tileUrl = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
    tileAttribution = "Tiles &copy; Esri, Maxar, Earthstar Geographics, USDA, USGS";
    maxZoom = 19;
  } else if (basemapType === "topo") {
    tileUrl = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png";
    tileAttribution = '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> contributors';
    maxZoom = 17;
  }

  return (
    <div className="relative w-full h-full min-h-[540px] rounded-lg overflow-hidden border border-slate-800 shadow-2xl bg-slate-950 flex flex-col">
      {/* Top Header Controls */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs z-10 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-sky-400" />
            Study Area:
          </span>
          <span className="text-slate-200 font-semibold">
            Lovely Professional University (LPU), Phagwara
          </span>
          <span className="text-slate-500 text-[11px] font-mono hidden sm:inline">
            (31.2533°N, 75.7033°E)
          </span>
        </div>

        {/* Quick Navigation Targets */}
        <div className="flex items-center gap-1.5 font-mono text-[11px]">
          <span className="text-slate-400 mr-1 text-[10px] uppercase tracking-wider font-sans">Focus:</span>
          <button
            onClick={() => {
              setMapCenter([31.2533, 75.7033]);
              setMapZoom(16.2);
            }}
            className="px-2 py-0.5 bg-blue-950 hover:bg-blue-900 text-blue-300 rounded border border-blue-800 transition flex items-center gap-1"
            title="Zoom directly into Lovely Professional University campus"
          >
            <Navigation className="w-2.5 h-2.5" />
            LPU Campus
          </button>
          <button
            onClick={() => {
              setMapCenter([31.2530, 75.6985]);
              setMapZoom(17.8);
            }}
            className="px-2 py-0.5 bg-rose-950 hover:bg-rose-900 text-rose-300 rounded border border-rose-800 transition flex items-center gap-1"
            title="Focus on critical low-lying underpass at NH-44 Gate 1"
          >
            <ShieldAlert className="w-2.5 h-2.5" />
            NH-44 Underpass
          </button>
          <button
            onClick={() => {
              setMapCenter([31.2400, 75.7350]);
              setMapZoom(13);
            }}
            className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition"
            title="Zoom out to Regional Jalandhar-Phagwara Basin"
          >
            Phagwara Basin
          </button>
        </div>
      </div>

      {/* Map Viewport */}
      <div className="relative flex-1 w-full h-full min-h-[440px]">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          <MapViewController center={mapCenter} zoom={mapZoom} />
          <MapClickHandler onMapClick={handleInspect} />

          {/* Watermark-Free Base Tile Layer */}
          <TileLayer
            key={basemapType}
            attribution={tileAttribution}
            url={tileUrl}
            maxZoom={maxZoom}
          />

          {/* Verified LPU Campus Boundary Polygon */}
          {showBoundary && boundaryCoords.length > 0 && (
            <Polygon
              positions={boundaryCoords}
              pathOptions={{
                color: "#2563eb",
                weight: 2.5,
                dashArray: "6, 6",
                fillColor: "#3b82f6",
                fillOpacity: basemapType === "satellite" ? 0.25 : 0.15,
              }}
            >
              <Popup>
                <div className="p-1 font-sans text-xs">
                  <div className="font-bold text-slate-100 text-sm mb-0.5">Lovely Professional University</div>
                  <div className="text-slate-300">Verified Campus Boundary (OSM Way 422435593)</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-1">Area: ~600 Acres | Elevation: ~238m</div>
                  <div className="text-[10px] text-emerald-400 font-mono mt-1">Status: Verified Spatial Extent</div>
                </div>
              </Popup>
            </Polygon>
          )}

          {/* NH-44 Highway Road LineString */}
          {showRoads && roadCoords.length > 0 && (
            <Polyline
              positions={roadCoords}
              pathOptions={{
                color: "#d97706",
                weight: 5,
                opacity: 0.9,
              }}
            >
              <Popup>
                <div className="p-1 font-sans text-xs">
                  <div className="font-bold text-slate-100 text-sm mb-0.5">NH-44 (Grand Trunk Road)</div>
                  <div className="text-slate-300">Delhi &ndash; Jalandhar Highway passing LPU Main Gates</div>
                  <div className="text-[10px] text-amber-300 font-mono mt-1">
                    Critical Hotspot: Underpass near Gate 1 (233.1m elevation depression)
                  </div>
                </div>
              </Popup>
            </Polyline>
          )}

          {/* Dynamic Flood Hotspot Markers with Permanent Labels */}
          {showHotspots &&
            hotspots.map((h) => {
              let markerColor = "#10b981";
              let radius = 10;
              let badgeBg = "bg-emerald-950 text-emerald-300 border-emerald-800";

              if (h.risk_category === "EXTREME") {
                markerColor = "#ef4444";
                radius = 16;
                badgeBg = "bg-rose-950 text-rose-300 border-rose-800";
              } else if (h.risk_category === "HIGH") {
                markerColor = "#f97316";
                radius = 14;
                badgeBg = "bg-orange-950 text-orange-300 border-orange-800";
              } else if (h.risk_category === "MODERATE") {
                markerColor = "#f59e0b";
                radius = 12;
                badgeBg = "bg-amber-950 text-amber-300 border-amber-800";
              }

              return (
                <CircleMarker
                  key={h.id}
                  center={[h.latitude, h.longitude]}
                  radius={radius}
                  pathOptions={{
                    color: "#ffffff",
                    weight: 2,
                    fillColor: markerColor,
                    fillOpacity: 0.9,
                  }}
                  eventHandlers={{
                    click: () => handleInspect(h.latitude, h.longitude),
                  }}
                >
                  {/* Permanent floating location label */}
                  {showLabels && (
                    <Tooltip
                      permanent
                      direction="top"
                      offset={[0, -radius - 2]}
                      className="custom-marker-tooltip"
                    >
                      <div className="font-sans font-bold text-[10px] text-slate-100 flex items-center gap-1 bg-slate-950/90 px-2 py-0.5 rounded border border-slate-700 shadow-md">
                        <span>{h.location_name}</span>
                        <span className={`px-1 py-0.2 rounded font-mono font-black text-[9px] border ${badgeBg}`}>
                          {h.flood_risk_score.toFixed(0)}
                        </span>
                      </div>
                    </Tooltip>
                  )}

                  <Popup>
                    <div className="p-2 font-sans text-xs space-y-2 min-w-[240px]">
                      <div className="flex items-center justify-between border-b border-slate-700 pb-1.5">
                        <span className="font-bold text-white text-xs">{h.location_name}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${badgeBg}`}>
                          {h.risk_category}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono py-1">
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                          <span className="text-slate-400 block text-[10px]">Risk Score:</span>
                          <span className="text-white font-bold">{h.flood_risk_score.toFixed(0)} / 100</span>
                        </div>
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                          <span className="text-slate-400 block text-[10px]">Est. Depth:</span>
                          <span className="text-cyan-300 font-bold">{h.estimated_depth_bracket}</span>
                        </div>
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                          <span className="text-slate-400 block text-[10px]">Time-to-Flood:</span>
                          <span className="text-amber-300 font-bold">{h.estimated_time_to_flood}</span>
                        </div>
                        <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                          <span className="text-slate-400 block text-[10px]">DEM Elevation:</span>
                          <span className="text-slate-200 font-bold">{h.elevation_m ? `${h.elevation_m}m` : "—"}</span>
                        </div>
                      </div>

                      <div className="text-[10px] text-amber-300/90 font-mono">
                        [MODEL ESTIMATE &bull; Uncalibrated Index]
                      </div>

                      <button
                        onClick={() => handleInspect(h.latitude, h.longitude)}
                        className="w-full px-2 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded transition flex items-center justify-center gap-1 shadow"
                      >
                        Inspect Full Hydrological Profile
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
        </MapContainer>

        {/* Floating Layer & Basemap Switcher (Top Right) */}
        <div className="absolute top-4 right-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-800 rounded-lg p-3 shadow-xl text-xs space-y-2.5 max-w-[210px]">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
              <Eye className="w-3 h-3 text-sky-400" />
              Basemap Style
            </div>
            <div className="grid grid-cols-2 gap-1 font-mono text-[10px]">
              <button
                onClick={() => setBasemapType("osm")}
                className={`px-2 py-1 rounded font-semibold border transition ${
                  basemapType === "osm"
                    ? "bg-sky-600 text-white border-sky-400"
                    : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                }`}
              >
                Street (OSM)
              </button>
              <button
                onClick={() => setBasemapType("satellite")}
                className={`px-2 py-1 rounded font-semibold border transition ${
                  basemapType === "satellite"
                    ? "bg-sky-600 text-white border-sky-400"
                    : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                }`}
              >
                Satellite (Esri)
              </button>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-2 space-y-1.5">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Layers className="w-3 h-3 text-sky-400" />
              Overlays
            </div>

            <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={showHotspots}
                onChange={(e) => setShowHotspots(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
              />
              <span>Flood Hotspots</span>
            </label>

            <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={showLabels}
                onChange={(e) => setShowLabels(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
              />
              <span>Location Names</span>
            </label>

            <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={showBoundary}
                onChange={(e) => setShowBoundary(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
              />
              <span>Campus Boundary</span>
            </label>

            <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={showRoads}
                onChange={(e) => setShowRoads(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
              />
              <span>NH-44 Highway</span>
            </label>
          </div>
        </div>

        {/* Map Legend (Bottom Left) */}
        <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-800 rounded-lg p-3 shadow-xl text-[11px] font-mono space-y-1">
          <div className="font-bold text-slate-200 font-sans text-xs border-b border-slate-800 pb-1 mb-1">
            Flood Risk Score Scale
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>0 &ndash; 20: Very Low / Low</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span>40 &ndash; 60: Moderate Risk</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            <span>60 &ndash; 80: High Hazard</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>80 &ndash; 100: Extreme Inundation</span>
          </div>
          <div className="text-[10px] text-slate-400 font-sans pt-1 border-t border-slate-800/80">
            Click anywhere on map to inspect point
          </div>
        </div>
      </div>

      {/* Point Inspector Drawer / Modal */}
      {selectedPoint && (
        <div className="border-t border-slate-800 bg-slate-950 p-4 text-xs font-sans animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-sky-400" />
              <span className="font-bold text-white text-sm">
                Point Hydrological Profile: {selectedPoint.location_label}
              </span>
            </div>
            <button
              onClick={() => setSelectedPoint(null)}
              className="text-slate-400 hover:text-white px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 transition"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 font-mono">
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">DEM Elevation</span>
              <span className="text-white font-bold text-sm">{selectedPoint.elevation_m} m</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Slope Angle</span>
              <span className="text-white font-bold text-sm">{selectedPoint.slope_deg}°</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Terrain Relief</span>
              <span className={`font-bold text-sm ${selectedPoint.is_depression ? "text-amber-400" : "text-emerald-400"}`}>
                {selectedPoint.is_depression ? "Depression" : "Conveying"}
              </span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Curve Number</span>
              <span className="text-white font-bold text-sm">{selectedPoint.curve_number}</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">SCS Runoff Depth</span>
              <span className="text-sky-300 font-bold text-sm">{selectedPoint.runoff_depth_mm} mm</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Flood Risk Score</span>
              <span className="text-amber-400 font-bold text-sm">{selectedPoint.flood_risk_score.toFixed(0)} / 100</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Est. Depth</span>
              <span className="text-cyan-300 font-bold text-sm">{selectedPoint.estimated_depth_bracket}</span>
            </div>
            <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 block">Est. Time-to-Flood</span>
              <span className="text-orange-300 font-bold text-sm">{selectedPoint.estimated_time_to_flood}</span>
            </div>
          </div>

          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 flex-wrap gap-2">
            <span className="flex items-center gap-1.5 text-amber-400 font-mono">
              <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
              Depths and time-to-flood are model estimates based on SCS-CN runoff accumulation; not measured sensor readings.
            </span>
            <ProvenanceBadge provenance={selectedPoint.provenance} size="sm" />
          </div>
        </div>
      )}
    </div>
  );
}
