import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Shield, Activity, Sliders, Settings, CheckSquare } from "lucide-react";

export const metadata: Metadata = {
  title: "Urban Flood Nowcasting System | Lovely Professional University (LPU)",
  description: "Dynamic Coupling of Rainfall Forecasts and Urban Drainage Network Models (SIH 2026)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased">
        {/* Top Emergency Operation Bar */}
        <header className="border-b border-slate-800 bg-slate-900 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-14">
              {/* Logo / Title */}
              <div className="flex items-center gap-3">
                <div className="bg-blue-600 p-1.5 rounded-lg text-white">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white tracking-wide">
                      URBAN FLOOD NOWCASTING PLATFORM
                    </span>
                    <span className="text-[10px] font-mono bg-blue-950 text-blue-400 px-2 py-0.2 rounded border border-blue-800">
                      SIH 2026
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Lovely Professional University & NH-44 Grand Trunk Road, Phagwara, Punjab
                  </div>
                </div>
              </div>

              {/* Navigation Links */}
              <nav className="flex items-center gap-1 text-xs">
                <Link
                  href="/"
                  className="px-3 py-1.5 rounded-md font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition"
                >
                  Live Dashboard
                </Link>
                <Link
                  href="/simulation"
                  className="px-3 py-1.5 rounded-md font-medium text-amber-400 hover:text-amber-300 hover:bg-amber-950/40 border border-amber-800/40 transition flex items-center gap-1.5"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  Scenario Simulator
                </Link>
                <Link
                  href="/admin"
                  className="px-3 py-1.5 rounded-md font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5"
                >
                  <Settings className="w-3.5 h-3.5" />
                  Admin Config
                </Link>
                <Link
                  href="/validation"
                  className="px-3 py-1.5 rounded-md font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5"
                >
                  <CheckSquare className="w-3.5 h-3.5" />
                  Validation
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content Viewport */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>

        {/* Institutional Footer */}
        <footer className="border-t border-slate-800 bg-slate-950 py-3 text-center text-xs text-slate-500 font-mono">
          <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
            <span>Lovely Professional University &bull; School of Computer Science & Engineering</span>
            <span>SIH 2026 Problem Statement &bull; Dynamic Rainfall & Drainage Coupling</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
