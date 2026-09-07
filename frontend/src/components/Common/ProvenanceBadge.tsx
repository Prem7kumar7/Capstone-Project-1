import React from "react";

interface Props {
  provenance: "LIVE" | "FORECAST" | "HISTORICAL" | "SIMULATED" | "DERIVED" | string;
  size?: "sm" | "md";
}

export const ProvenanceBadge: React.FC<Props> = ({ provenance, size = "sm" }) => {
  const p = provenance.toUpperCase();

  let colorClasses = "bg-slate-800 text-slate-300 border-slate-700";
  if (p === "LIVE") {
    colorClasses = "bg-emerald-950/80 text-emerald-400 border-emerald-600/50";
  } else if (p === "FORECAST") {
    colorClasses = "bg-sky-950/80 text-sky-400 border-sky-600/50";
  } else if (p === "SIMULATED") {
    colorClasses = "bg-amber-950/80 text-amber-400 border-amber-600/50";
  } else if (p === "DERIVED") {
    colorClasses = "bg-indigo-950/80 text-indigo-400 border-indigo-600/50";
  } else if (p === "HISTORICAL") {
    colorClasses = "bg-neutral-900 text-neutral-400 border-neutral-700";
  }

  const padding = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={`inline-flex items-center font-mono font-semibold tracking-wider rounded border ${colorClasses} ${padding}`}
      title={`Data Provenance: ${p}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75"></span>
      {p}
    </span>
  );
};
