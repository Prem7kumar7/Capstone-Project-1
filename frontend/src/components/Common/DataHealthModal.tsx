import React from "react";
import { SystemHealth } from "@/types/flood";
import { ProvenanceBadge } from "./ProvenanceBadge";
import { Activity, X, CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  health: SystemHealth | null;
}

export const DataHealthModal: React.FC<Props> = ({ isOpen, onClose, health }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-950">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-emerald-400" />
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">Data Source Health & Provenance Panel</h2>
              <p className="text-xs text-slate-400">Real-time status of APIs, sensors, and modeling engines</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {health ? (
            <>
              {/* Overall Status Banner */}
              <div className="flex items-center justify-between p-3.5 bg-slate-950 rounded-lg border border-slate-800">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">System State:</span>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono ${
                    health.system_status === "OPERATIONAL" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-amber-950 text-amber-400 border border-amber-800"
                  }`}>
                    {health.system_status}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Verified: {health.checked_at_ist}</span>
                </div>
              </div>

              {/* Providers Table */}
              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Provider / Data Layer</th>
                      <th className="py-3 px-3">Type</th>
                      <th className="py-3 px-3">Status</th>
                      <th className="py-3 px-3">Latency</th>
                      <th className="py-3 px-3">Provenance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {health.providers.map((p, idx) => {
                      let statusBadge = (
                        <span className="flex items-center gap-1.5 text-emerald-400">
                          <CheckCircle2 className="w-3.5 h-3.5" /> ONLINE
                        </span>
                      );
                      if (p.status === "DEGRADED") {
                        statusBadge = (
                          <span className="flex items-center gap-1.5 text-amber-400">
                            <AlertTriangle className="w-3.5 h-3.5" /> DEGRADED
                          </span>
                        );
                      } else if (p.status === "OFFLINE" || p.status === "NOT_AVAILABLE") {
                        statusBadge = (
                          <span className="flex items-center gap-1.5 text-slate-500">
                            <XCircle className="w-3.5 h-3.5" /> {p.status}
                          </span>
                        );
                      } else if (p.status === "DORMANT") {
                        statusBadge = (
                          <span className="flex items-center gap-1.5 text-sky-400">
                            <Clock className="w-3.5 h-3.5" /> DORMANT
                          </span>
                        );
                      }

                      return (
                        <tr key={idx} className="hover:bg-slate-800/40 transition">
                          <td className="py-3 px-4">
                            <div className="font-semibold text-slate-200 font-sans">{p.provider_name}</div>
                            {p.notes && <div className="text-[11px] text-slate-400 font-sans mt-0.5">{p.notes}</div>}
                          </td>
                          <td className="py-3 px-3 text-slate-400 text-[11px]">{p.provider_type}</td>
                          <td className="py-3 px-3">{statusBadge}</td>
                          <td className="py-3 px-3 text-slate-300">
                            {p.latency_ms ? `${p.latency_ms} ms` : "—"}
                          </td>
                          <td className="py-3 px-3">
                            <ProvenanceBadge provenance={p.data_provenance} size="sm" />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Scientific Honesty Notice */}
              <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-400 space-y-1.5 font-sans">
                <p className="font-bold text-slate-300">Operational Integrity Statement:</p>
                <p>
                  1. Unconnected sensor platforms and non-existent underground pipes are never simulated as live observations.
                </p>
                <p>
                  2. In the absence of sub-surface pipe network surveys, the system transparently runs in <strong>Terrain + Land-Cover Runoff Susceptibility Mode</strong>.
                </p>
              </div>
            </>
          ) : (
            <div className="py-12 text-center text-slate-400">Loading diagnostic health status...</div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition"
          >
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
