import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, AlertCircle, Info } from 'lucide-react';
import { LeadTimeData, RouteMetadata } from '../types';
import { api } from '../services/api';

interface LeadTimePageProps {
  routes: RouteMetadata[];
}

export const LeadTimePage: React.FC<LeadTimePageProps> = ({ routes }) => {
  const [selectedRoute, setSelectedRoute] = useState<string>('ALL');
  const [data, setData] = useState<LeadTimeData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [selectedRoute]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.getLeadTime(selectedRoute !== 'ALL' ? selectedRoute : undefined);
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Lead-Time Analytics & Booking Horizon Elasticity
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic airfare progression across standardized advance purchase windows (T+1, T+7, T+15, T+30, T+45).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Sector Filter:</span>
          <select
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="ALL">All Monitored Routes</option>
            {routes.map((r) => (
              <option key={r.route_code} value={r.route_code}>
                {r.route_code}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Compliance Disclaimer Alert */}
      <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
        <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-200">Analytical Disclaimer: </span>
          The elasticity metric represents an empirical pricing slope across observed lead-time buckets, not a structural causal economic elasticity.
        </div>
      </div>

      {/* Elasticity Metric Banner */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Empirical Elasticity</span>
            <div className="text-3xl font-bold font-mono text-emerald-400 mt-1">
              {data.empirical_elasticity}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">{data.interpretation}</p>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Last-Minute Premium (T+1 vs T+45)</span>
            {data.curve.length >= 2 && (
              <div className="text-3xl font-bold font-mono text-rose-400 mt-1">
                +{(
                  ((data.curve[0].median_fare - data.curve[data.curve.length - 1].median_fare) /
                    data.curve[data.curve.length - 1].median_fare) *
                  100
                ).toFixed(1)}%
              </div>
            )}
            <p className="text-[11px] text-slate-400 mt-1">Emergency vs promotional baseline</p>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Baseline Benchmark</span>
            <div className="text-3xl font-bold font-mono text-indigo-400 mt-1">
              T+30
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Normal consumer planning horizon</p>
          </div>
        </div>
      )}

      {/* Lead-Time Curve Table */}
      {data && (
        <div className="terminal-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Advance Purchase Window Breakdown ({data.route_filter})
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Window</th>
                  <th className="py-2.5 px-3">Lead Days</th>
                  <th className="py-2.5 px-3">Median Airfare</th>
                  <th className="py-2.5 px-3">Interquartile Band (P25 - P75)</th>
                  <th className="py-2.5 px-3">Relative Index (T+30=100)</th>
                  <th className="py-2.5 px-3">Quotes Sampled</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {data.curve.map((c) => (
                  <tr key={c.advance_window} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-3 font-bold text-indigo-300">{c.advance_window}</td>
                    <td className="py-2.5 px-3 text-slate-400">{c.advance_days} days prior</td>
                    <td className="py-2.5 px-3 font-bold text-slate-100">₹{c.median_fare.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-slate-400">
                      ₹{c.p25.toLocaleString()} — ₹{c.p75.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-emerald-400">{c.relative_index.toFixed(1)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{c.observations.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
