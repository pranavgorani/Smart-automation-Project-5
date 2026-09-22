import React from 'react';
import { Bell, Search, ExternalLink, RefreshCw, Sparkles, Terminal } from 'lucide-react';

interface NavbarProps {
  currentDate?: string;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ currentDate, onRefresh, isRefreshing }) => {
  return (
    <header className="h-16 glass-panel px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-400 border border-slate-700">
            MoSPI • DIID
          </span>
          <span className="text-slate-500">/</span>
          <span className="text-xs text-slate-300 font-medium">Real-Time Airfare Price Index for CPI Augmentation</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {currentDate && (
          <div className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded border border-slate-800">
            Observation Cycle: <span className="text-slate-200 font-semibold">{currentDate}</span>
          </div>
        )}

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition disabled:opacity-50"
          title="Refresh Dashboard Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-medium transition border border-slate-700/60"
        >
          <Terminal className="w-3.5 h-3.5 text-indigo-400" />
          <span>Swagger API</span>
          <ExternalLink className="w-3 h-3 text-slate-400" />
        </a>
      </div>
    </header>
  );
};
