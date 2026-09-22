import React from 'react';
import { ShieldAlert, Sparkles, RefreshCw } from 'lucide-react';

interface DemoBannerProps {
  isDemo: boolean;
  onRunDemo?: () => void;
  isLoading?: boolean;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({ isDemo, onRunDemo, isLoading }) => {
  if (!isDemo) return null;

  return (
    <div className="bg-gradient-to-r from-amber-950/70 via-indigo-950/70 to-slate-900 border-l-4 border-amber-500 border-y border-r border-amber-500/30 text-slate-200 px-4 py-2.5 rounded-lg mb-6 flex flex-wrap items-center justify-between gap-3 shadow-lg shadow-amber-950/20">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-500/20 text-amber-400 rounded-md">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-amber-300 text-sm tracking-wide uppercase">Demo Mode Active</span>
            <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-200 border border-amber-500/30">MoSPI Prototype</span>
          </div>
          <p className="text-xs text-slate-300 mt-0.5">
            Synthetic airfare observations are being used because live Amadeus/SerpAPI credentials are not configured. Data generated strictly via reproducible econometric simulation across 13 Indian routes.
          </p>
        </div>
      </div>

      {onRunDemo && (
        <button
          onClick={onRunDemo}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-semibold shadow-md transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Processing Pipeline...' : 'Run Demo Pipeline'}</span>
        </button>
      )}
    </div>
  );
};
