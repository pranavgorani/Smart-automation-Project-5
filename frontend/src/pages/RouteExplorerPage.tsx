import React, { useState, useEffect } from 'react';
import { Navigation, Filter, Layers, ArrowRight, BarChart3, TrendingUp } from 'lucide-react';
import { RouteMetadata, HeatmapResponse } from '../types';
import { api } from '../services/api';

interface RouteExplorerPageProps {
  routes: RouteMetadata[];
}

export const RouteExplorerPage: React.FC<RouteExplorerPageProps> = ({ routes }) => {
  const [selectedRoute, setSelectedRoute] = useState('DEL-BOM');
  const [advanceWindow, setAdvanceWindow] = useState<number | undefined>(undefined);
  const [routeStats, setRouteStats] = useState<any>(null);
  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [heatmapTimeframe, setHeatmapTimeframe] = useState('daily');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRouteDetails();
  }, [selectedRoute, advanceWindow]);

  useEffect(() => {
    fetchHeatmap();
  }, [heatmapTimeframe]);

  const fetchRouteDetails = async () => {
    setLoading(true);
    try {
      const parts = selectedRoute.split('-');
      const origin = parts[0];
      const destination = parts[1];
      const data = await api.getQuotes({
        origin,
        destination,
        advance_window: advanceWindow,
        limit: 200,
      });

      // Calculate stats
      const fares = data.results.map((r) => r.total_fare);
      if (fares.length > 0) {
        fares.sort((a, b) => a - b);
        const med = fares[Math.floor(fares.length / 2)];
        const mean = fares.reduce((a, b) => a + b, 0) / fares.length;
        const min = fares[0];
        const max = fares[fares.length - 1];

        // Airline grouping
        const airlinesMap: Record<string, number[]> = {};
        data.results.forEach((q) => {
          if (!airlinesMap[q.airline]) airlinesMap[q.airline] = [];
          airlinesMap[q.airline].push(q.total_fare);
        });

        const airlineStats = Object.entries(airlinesMap).map(([name, fList]) => {
          fList.sort((a, b) => a - b);
          return {
            airline: name,
            median: fList[Math.floor(fList.length / 2)],
            count: fList.length,
            min: fList[0],
            max: fList[fList.length - 1],
          };
        });

        setRouteStats({
          median: med,
          mean: mean,
          min: min,
          max: max,
          count: fares.length,
          airlineStats,
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchHeatmap = async () => {
    try {
      const data = await api.getHeatmap(heatmapTimeframe);
      setHeatmap(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Sector & Route Intelligence</h2>
        <p className="text-xs text-slate-400 mt-1">
          Detailed price distributions, carrier quotes, and Origin × Destination price movement matrices.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="terminal-card p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
            <Filter className="w-4 h-4 text-indigo-400" />
            <span>Select Sector:</span>
          </div>
          <select
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            {routes.map((r) => (
              <option key={r.route_code} value={r.route_code}>
                {r.route_code} ({r.city_pair})
              </option>
            ))}
          </select>

          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 ml-2">
            <span>Advance Window:</span>
          </div>
          <select
            value={advanceWindow || ''}
            onChange={(e) => setAdvanceWindow(e.target.value ? Number(e.target.value) : undefined)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="">All Windows (T+1 to T+45)</option>
            <option value="1">T+1 (1 Day)</option>
            <option value="7">T+7 (7 Days)</option>
            <option value="15">T+15 (15 Days)</option>
            <option value="30">T+30 (30 Days)</option>
            <option value="45">T+45 (45 Days)</option>
          </select>
        </div>

        <div className="text-xs font-mono text-slate-400">
          Route Weight in APIx: <span className="text-indigo-400 font-bold">{(routes.find((r) => r.route_code === selectedRoute)?.route_weight || 0.1) * 100}%</span>
        </div>
      </div>

      {/* Metric Cards for Selected Route */}
      {routeStats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Median Fare</span>
            <div className="text-2xl font-bold font-mono text-indigo-400 mt-1">₹{routeStats.median.toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">Sample: {routeStats.count} quotes</span>
          </div>
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Mean Fare</span>
            <div className="text-2xl font-bold font-mono text-slate-200 mt-1">₹{Math.round(routeStats.mean).toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">Arithmetic average</span>
          </div>
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Floor Fare (Min)</span>
            <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">₹{routeStats.min.toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">Lowest observed bucket</span>
          </div>
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Ceiling Fare (Max)</span>
            <div className="text-2xl font-bold font-mono text-rose-400 mt-1">₹{routeStats.max.toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">Peak observed bucket</span>
          </div>
          <div className="terminal-card p-4">
            <span className="text-[11px] text-slate-400 uppercase font-medium">Price Spread</span>
            <div className="text-2xl font-bold font-mono text-amber-400 mt-1">₹{(routeStats.max - routeStats.min).toLocaleString()}</div>
            <span className="text-[10px] text-slate-400">Max - Min dispersion</span>
          </div>
        </div>
      )}

      {/* Airline Dispersion Table on Selected Route */}
      {routeStats?.airlineStats && (
        <div className="terminal-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Carrier Pricing Breakdown on {selectedRoute}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Carrier</th>
                  <th className="py-2.5 px-3">Median Fare</th>
                  <th className="py-2.5 px-3">Lowest Fare</th>
                  <th className="py-2.5 px-3">Highest Fare</th>
                  <th className="py-2.5 px-3">Observations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {routeStats.airlineStats.map((a: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-800/40">
                    <td className="py-2 px-3 font-semibold text-slate-300">{a.airline}</td>
                    <td className="py-2 px-3 font-bold text-indigo-400">₹{a.median.toLocaleString()}</td>
                    <td className="py-2 px-3 text-emerald-400">₹{a.min.toLocaleString()}</td>
                    <td className="py-2 px-3 text-rose-400">₹{a.max.toLocaleString()}</td>
                    <td className="py-2 px-3 text-slate-400">{a.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Origin x Destination Heatmap */}
      <div className="terminal-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Origin × Destination Price Movement Heatmap</h3>
            <p className="text-xs text-slate-400">Color intensity reflects percentage fare adjustment across domestic pairs</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Timeframe:</span>
            <div className="flex rounded-lg bg-slate-900 border border-slate-800 p-0.5 text-xs font-mono">
              {['daily', 'weekly', 'monthly'].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setHeatmapTimeframe(tf)}
                  className={`px-2.5 py-1 rounded capitalize transition ${
                    heatmapTimeframe === tf ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
        </div>

        {heatmap && (
          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs font-mono border-collapse">
              <thead>
                <tr className="bg-slate-900 text-slate-400 border-b border-slate-800">
                  <th className="py-2.5 px-3 text-left">Origin \ Dest</th>
                  {heatmap.destinations.map((d) => (
                    <th key={d} className="py-2.5 px-3 font-bold text-slate-300">{d}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {heatmap.matrix.map((row) => (
                  <tr key={row.origin} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-bold text-left text-slate-300 bg-slate-900/50">{row.origin}</td>
                    {heatmap.destinations.map((dest) => {
                      const cell = row.destinations[dest];
                      if (!cell || !cell.active || cell.change_pct === null || cell.change_pct === undefined) {
                        return (
                          <td key={dest} className="py-2.5 px-3 text-slate-600 bg-slate-950/40">
                            —
                          </td>
                        );
                      }
                      const chg = cell.change_pct;
                      const isUp = chg > 0;
                      const isDown = chg < 0;
                      const bgIntensity = Math.min(0.5, Math.abs(chg) / 30);
                      const bgColor = isUp
                        ? `rgba(239, 68, 68, ${bgIntensity})`
                        : isDown
                        ? `rgba(16, 185, 129, ${bgIntensity})`
                        : 'transparent';

                      return (
                        <td
                          key={dest}
                          style={{ backgroundColor: bgColor }}
                          className="py-2.5 px-3 transition-colors cursor-pointer"
                          title={`${row.origin}-${dest}: Median ₹${cell.median_fare?.toLocaleString() || ''}`}
                          onClick={() => cell.route && setSelectedRoute(cell.route)}
                        >
                          <div className={`font-semibold ${isUp ? 'text-rose-300' : isDown ? 'text-emerald-300' : 'text-slate-300'}`}>
                            {chg > 0 ? `+${chg.toFixed(1)}%` : `${chg.toFixed(1)}%`}
                          </div>
                          {cell.median_fare && (
                            <div className="text-[10px] text-slate-400">₹{cell.median_fare.toLocaleString()}</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
