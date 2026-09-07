"use client";

import React from "react";
import dynamic from "next/dynamic";
import { FloodHotspot } from "@/types/flood";

interface Props {
  hotspots: FloodHotspot[];
  boundaryGeoJson?: any;
  roadsGeoJson?: any;
  waterwaysGeoJson?: any;
  infrastructureGeoJson?: any;
  regionId?: string;
}

const LeafletMapInner = dynamic(() => import("./LeafletMapInner"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[540px] bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-center text-xs text-slate-500 font-mono">
      <div className="flex flex-col items-center gap-2">
        <div className="w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
        <span>Loading High-Resolution LPU GIS Basemap...</span>
      </div>
    </div>
  ),
});

export const FloodMap: React.FC<Props> = (props) => {
  return <LeafletMapInner {...props} />;
};
