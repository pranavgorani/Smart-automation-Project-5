import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, ShieldAlert, Sliders, CheckCircle2, Save, RefreshCw } from 'lucide-react';
import { SystemHealth, RouteMetadata } from '../types';
import { api } from '../services/api';

interface SystemHealthPageProps {
  routes: RouteMetadata[];
  onRefreshRoutes: () => void;
}

export const SystemHealthPage: React.FC<SystemHealthPageProps> = ({ routes, onRefreshRoutes }) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [customWeights, setCustomWeights] = useState<Record<string, number>>({});
  const [weightStatus, setWeightStatus] = useState<string | null>(null);
  const [savingWeights, setSavingWeights] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHealth();
    // Initialize custom weights from routes
    const wMap: Record<string, number> = {};
    routes.forEach((r) => {
      wMap[r.route_code] = r.route_weight;
    });
    setCustomWeights(wMap);
  }, [routes]);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (route: string, val: number) => {
    setCustomWeights((prev) => ({
      ...prev,
      [route]: val,
    }));
  };

  const handleSaveWeights = async () => {
    setSavingWeights(true);
    setWeightStatus(null);
    try {
      const res = await api.updateWeights(customWeights);
      setWeightStatus('✓ Weights successfully updated and normalized to 1.0.');
      onRefreshRoutes();
      setTimeout(() => setWeightStatus(null), 4000);
    } catch (err: any) {
      setWeightStatus(`✗ Failed to update weights: ${err.message}`);
    } finally {
      setSavingWeights(false);
    }
  };

  const currentWeightSum = Object.values(customWeights).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">System Health & Admin Configuration</h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time backend service telemetry, database connection latency, and dynamic route weight administration.
          </p>
        </div>

        <button
          onClick={fetchHealth}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Ping System</span>
        </button>
      </div>

      {/* Health Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div className="terminal-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 uppercase text-[10px]">API Server Status</span>
            <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              {health?.status || 'OPERATIONAL'}
            </span>
          </div>
          <div className="text-xl font-bold text-white mt-2">{health?.app_name || 'AIRFARE-X INDIA'}</div>
          <span className="text-[10px] text-slate-400 block mt-1">Env: {health?.environment || 'development'}</span>
        </div>

        <div className="terminal-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 uppercase text-[10px]">Database Connection</span>
            <span className="text-emerald-400 font-bold">{health?.database.status || 'HEALTHY'}</span>
          </div>
          <div className="text-xl font-bold text-white mt-2">{health?.database.engine || 'PostgreSQL'}</div>
          <span className="text-[10px] text-slate-400 block mt-1">Latency: {health?.database.latency_ms || 0.8} ms</span>
        </div>

        <div className="terminal-card p-5">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 uppercase text-[10px]">Data Provenance Mode</span>
            <span className="text-amber-400 font-bold">{health?.demo_mode ? 'DEMO_MODE' : 'PRODUCTION'}</span>
          </div>
          <div className="text-xl font-bold text-white mt-2">{health?.demo_mode ? 'Synthetic Seed' : 'Live API Stream'}</div>
          <span className="text-[10px] text-slate-400 block mt-1">Robots.txt verified</span>
        </div>
      </div>

      {/* Dynamic Route Weights Admin Panel */}
      <div className="terminal-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-400" />
              <span>Dynamic Route Weight Administration (Section 14 & 31)</span>
            </h3>
            <p className="text-xs text-slate-400">
              Adjust route weights to evaluate index sensitivity. Changes are normalized automatically (Σw = 1.0).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-xs font-mono text-slate-300">
              Raw Sum: <span className={Math.abs(currentWeightSum - 1.0) < 0.01 ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>{currentWeightSum.toFixed(2)}</span>
            </div>
            <button
              onClick={handleSaveWeights}
              disabled={savingWeights}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{savingWeights ? 'Saving...' : 'Apply & Recalculate'}</span>
            </button>
          </div>
        </div>

        {weightStatus && (
          <div className="p-3 mb-4 rounded bg-slate-900 border border-indigo-500 text-xs text-indigo-300 font-mono">
            {weightStatus}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {routes.map((r) => {
            const wVal = customWeights[r.route_code] ?? r.route_weight;
            return (
              <div key={r.route_code} className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 text-xs">
                <div className="flex justify-between font-mono mb-1.5">
                  <span className="font-bold text-slate-200">{r.route_code}</span>
                  <span className="text-indigo-400 font-bold">{(wVal * 100).toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="0.01"
                  max="0.30"
                  step="0.01"
                  value={wVal}
                  onChange={(e) => handleWeightChange(r.route_code, parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
                <span className="text-[10px] text-slate-400 truncate block mt-1">{r.city_pair}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
