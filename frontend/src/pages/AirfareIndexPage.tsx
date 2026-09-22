import React, { useState } from 'react';
import { Download, Search, Filter, Calendar, Info } from 'lucide-react';
import { HistoricalIndexPoint } from '../types';
import { TrendLineChart } from '../components/Charts';

interface AirfareIndexPageProps {
  history: HistoricalIndexPoint[];
}

export const AirfareIndexPage: React.FC<AirfareIndexPageProps> = ({ history }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = history.filter((h) =>
    h.index_date.includes(searchTerm)
  );

  const chartPoints = history.map((h) => ({
    date: h.index_date,
    value: h.index_value,
  }));

  const handleDownloadCsv = () => {
    if (!history.length) return;
    const headers = 'index_date,index_value,daily_change,weekly_change,monthly_change,route_count,observation_count,confidence_score\n';
    const rows = history
      .map(
        (h) =>
          `${h.index_date},${h.index_value},${h.daily_change},${h.weekly_change},${h.monthly_change},${h.route_count},${h.observation_count},${h.confidence_score}`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `apix_index_series_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Experimental Real-Time Airfare Price Index (APIx)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Aggregated Laspeyres-type daily price relative index across 13 Indian domestic trunk routes.
          </p>
        </div>

        <button
          onClick={handleDownloadCsv}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow transition"
        >
          <Download className="w-4 h-4" />
          <span>Export Index Series (CSV)</span>
        </button>
      </div>

      {/* Primary Historical Chart */}
      <div className="terminal-card p-6">
        <TrendLineChart
          data={chartPoints}
          title="Daily Trajectory of Experimental Airfare Price Index"
          subtitle="Relative price movement against fixed base period (2026-01-01 = 100.0)"
          height={260}
        />
      </div>

      {/* Historical Data Table */}
      <div className="terminal-card p-5 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Calendar className="w-4 h-4 text-indigo-400" />
            <span>Daily Index Observations ({filteredHistory.length})</span>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter by date (YYYY-MM-DD)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg pl-8 pr-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">APIx Value</th>
                <th className="py-2.5 px-3">24h Change</th>
                <th className="py-2.5 px-3">7d Change</th>
                <th className="py-2.5 px-3">30d Change</th>
                <th className="py-2.5 px-3">Sectors</th>
                <th className="py-2.5 px-3">Quotes Sampled</th>
                <th className="py-2.5 px-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filteredHistory.map((h, i) => {
                const isPositive = h.daily_change > 0;
                const isNegative = h.daily_change < 0;
                return (
                  <tr key={i} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-3 font-semibold text-slate-300">{h.index_date}</td>
                    <td className="py-2.5 px-3 font-bold text-indigo-400">{h.index_value.toFixed(2)}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[11px] ${
                          isPositive
                            ? 'bg-rose-500/10 text-rose-400'
                            : isNegative
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'text-slate-400'
                        }`}
                      >
                        {h.daily_change > 0 ? `+${h.daily_change.toFixed(2)}%` : `${h.daily_change.toFixed(2)}%`}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">{h.weekly_change > 0 ? `+${h.weekly_change.toFixed(2)}%` : `${h.weekly_change.toFixed(2)}%`}</td>
                    <td className="py-2.5 px-3 text-slate-400">{h.monthly_change > 0 ? `+${h.monthly_change.toFixed(2)}%` : `${h.monthly_change.toFixed(2)}%`}</td>
                    <td className="py-2.5 px-3 text-slate-400">{h.route_count}</td>
                    <td className="py-2.5 px-3 text-slate-400">{h.observation_count.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-semibold">{h.confidence_score.toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
