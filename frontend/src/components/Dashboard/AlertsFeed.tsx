import React from "react";
import { AlertAdvisory } from "@/types/flood";
import { ProvenanceBadge } from "../Common/ProvenanceBadge";
import { ShieldAlert, AlertTriangle, AlertCircle, Info, Clock, MapPin } from "lucide-react";

interface Props {
  alerts: AlertAdvisory[];
}

export const AlertsFeed: React.FC<Props> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-center text-xs text-slate-500">
        No active emergency flood advisories for LPU & NH-44 corridor.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => {
        let borderClass = "border-emerald-800/60 bg-emerald-950/20";
        let badgeColor = "bg-emerald-950 text-emerald-400 border-emerald-700";
        let Icon = Info;

        if (alert.alert_level === "RED") {
          borderClass = "border-rose-800/80 bg-rose-950/25";
          badgeColor = "bg-rose-950 text-rose-400 border-rose-700";
          Icon = ShieldAlert;
        } else if (alert.alert_level === "ORANGE") {
          borderClass = "border-orange-800/80 bg-orange-950/25";
          badgeColor = "bg-orange-950 text-orange-400 border-orange-700";
          Icon = AlertTriangle;
        } else if (alert.alert_level === "YELLOW") {
          borderClass = "border-amber-800/70 bg-amber-950/20";
          badgeColor = "bg-amber-950 text-amber-400 border-amber-700";
          Icon = AlertCircle;
        }

        return (
          <div
            key={alert.id}
            className={`border rounded-lg p-4 transition-all ${borderClass}`}
          >
            {/* Advisory Header */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 flex-shrink-0" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-100">
                  {alert.headline}
                </h4>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${badgeColor}`}>
                  {alert.alert_level}
                </span>
                <ProvenanceBadge provenance={alert.provenance} size="sm" />
              </div>
            </div>

            {/* Key Metrics Row */}
            <div className="grid grid-cols-3 gap-2 my-2 py-2 px-3 bg-slate-950/70 rounded border border-slate-800 text-[11px] font-mono">
              <div>
                <span className="text-slate-500 block text-[10px]">Risk Score:</span>
                <span className="text-white font-bold">{alert.flood_risk_score.toFixed(0)} / 100</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Peak Est. Depth:</span>
                <span className="text-amber-300 font-bold">{alert.estimated_depth_bracket}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Est. Time-to-Impact:</span>
                <span className="text-sky-300 font-bold">{alert.estimated_time_to_impact}</span>
              </div>
            </div>

            {/* Recommended Actions */}
            <div className="mt-2 text-xs text-slate-300 space-y-1">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Emergency Recommended Protocol:
              </div>
              <pre className="font-sans text-xs whitespace-pre-wrap text-slate-300 bg-slate-950/40 p-2.5 rounded border border-slate-800/60 leading-relaxed">
                {alert.recommended_actions}
              </pre>
            </div>

            {/* Metadata Footer */}
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono">
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3 h-3 text-slate-400" />
                <span>{alert.location_name}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>Issued: {alert.issued_at_ist}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
