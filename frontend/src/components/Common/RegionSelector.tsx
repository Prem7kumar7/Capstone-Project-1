"use client";

import React from "react";
import { MapPin, Navigation, School, Train, Factory, Building2 } from "lucide-react";

interface Props {
  selectedRegion: string;
  onSelectRegion: (regionId: string) => void;
}

export const REGIONS_META = [
  {
    id: "lpu_main_campus",
    label: "LPU Campus",
    sub: "NH-44 Corridor",
    district: "Kapurthala",
    elevation: "234m",
    icon: School,
    color: "from-blue-600 to-indigo-600"
  },
  {
    id: "chaheru",
    label: "Chaheru / Chiheru",
    sub: "Rail & Stream Basin",
    district: "Kapurthala",
    elevation: "232m",
    icon: Train,
    color: "from-teal-600 to-emerald-600"
  },
  {
    id: "phagwara_urban",
    label: "Phagwara Urban",
    sub: "Municipal Basin",
    district: "Kapurthala",
    elevation: "249m",
    icon: Factory,
    color: "from-amber-600 to-orange-600"
  },
  {
    id: "jalandhar_metro",
    label: "Jalandhar Metro",
    sub: "Urban Metro Corridor",
    district: "Jalandhar",
    elevation: "242m",
    icon: Building2,
    color: "from-purple-600 to-rose-600"
  }
];

export function RegionSelector({ selectedRegion, onSelectRegion }: Props) {
  return (
    <div className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg">
      <div className="flex items-center justify-between mb-2 px-1">
        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-300">
          <MapPin className="w-3.5 h-3.5 text-sky-400" />
          <span>Active Study Region</span>
          <span className="text-slate-500 font-normal text-[11px]">| Select sub-catchment to inspect:</span>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded">
          Independent Hydraulic Boundaries
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {REGIONS_META.map((r) => {
          const Icon = r.icon;
          const isSelected = selectedRegion === r.id;
          return (
            <button
              key={r.id}
              onClick={() => onSelectRegion(r.id)}
              className={`p-2 rounded-lg border text-left transition relative flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-800/90 border-sky-500 shadow-md shadow-sky-950/30"
                  : "bg-slate-950/60 border-slate-800 hover:bg-slate-800/50 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1.5">
                  <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-sky-400" : "text-slate-400"}`} />
                  <span className={`text-xs font-bold ${isSelected ? "text-white" : "text-slate-300"}`}>
                    {r.label}
                  </span>
                </div>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
                )}
              </div>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mt-1">
                <span>{r.sub}</span>
                <span className="text-slate-500">{r.elevation}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
