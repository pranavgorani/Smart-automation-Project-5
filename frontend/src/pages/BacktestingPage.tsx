import React, { useState, useEffect } from 'react';
import { FlaskConical, Download, Info, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';
import { BacktestResults } from '../types';
import { api } from '../services/api';
import { TrendLineChart } from '../components/Charts';

export const BacktestingPage: React.FC = () => {
  const [results, setResults] = useState<BacktestResults | null>(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBacktest();
  }, [days]);

  const fetchBacktest = async () => {
    setLoading(true);
    try {
      const res = await api.getBacktest(days);
      setResults(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const chartPoints = (results?.series || []).map((s) => ({
    date: s.date,
    value: s.apix,
    reference: s.dgca_reference,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">Prototype Validation / Back-Testing</h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-700/50">
              MoSPI DIID Benchmark
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Empirical validation comparing the high-frequency APIx index against monthly published DGCA reference series.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Horizon:</span>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="15">15 Days</option>
            <option value="30">30 Days</option>
            <option value="60">60 Days</option>
          </select>
        </div>
      </div>

      {/* Compliance Disclaimer */}
      <div className="p-4 rounded-lg bg-indigo-950/40 border border-indigo-800/60 text-xs text-indigo-200 flex items-start gap-3">
        <Info className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-white uppercase tracking-wider text-[11px] block">Methodological Note</span>
          {results?.disclaimer ||
            'Prototype validation only. Demonstrates tracking correlation with DGCA reference series; does not constitute official MoSPI / DIID statistical validation.'}
        </div>
      </div>

      {/* Validation Metrics Grid */}
      {results?.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 font-mono">
          <div className="terminal-card p-4">
            <span className="text-[10px] text-slate-400 uppercase">Mean Absolute Error (MAE)</span>
            <div className="text-2xl font-bold text-slate-100 mt-1">{results.metrics.mae.toFixed(2)}</div>
            <span className="text-[10px] text-slate-400">Points deviation</span>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[10px] text-slate-400 uppercase">Root Mean Sq Error (RMSE)</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">{results.metrics.rmse.toFixed(2)}</div>
            <span className="text-[10px] text-slate-400">Quadratic tracking error</span>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[10px] text-slate-400 uppercase">Mean Abs % Error (MAPE)</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{results.metrics.mape.toFixed(2)}%</div>
            <span className="text-[10px] text-slate-400">Relative divergence</span>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[10px] text-slate-400 uppercase">Pearson Correlation (r)</span>
            <div className="text-2xl font-bold text-sky-400 mt-1">{results.metrics.correlation.toFixed(3)}</div>
            <span className="text-[10px] text-slate-400">Series co-movement</span>
          </div>

          <div className="terminal-card p-4">
            <span className="text-[10px] text-slate-400 uppercase">Directional Accuracy</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">
              {results.metrics.directional_accuracy_pct.toFixed(1)}%
            </div>
            <span className="text-[10px] text-slate-400">Sign of change match</span>
          </div>
        </div>
      )}

      {/* Comparison Chart */}
      <div className="terminal-card p-6">
        <TrendLineChart
          data={chartPoints}
          title="APIx vs DGCA Monthly Benchmark Reference Series"
          subtitle="Real-time daily APIx demonstrates responsive dynamic shifts while tracking the underlying DGCA reference trend"
          showReference={true}
          referenceLabel="DGCA Benchmark Series"
          height={300}
        />
      </div>

      {/* Spread Table */}
      {results?.series && (
        <div className="terminal-card p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Daily Series Comparison & Basis Spread</h3>
          <div className="overflow-x-auto max-h-80">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">APIx Value</th>
                  <th className="py-2.5 px-3">DGCA Benchmark</th>
                  <th className="py-2.5 px-3">Basis Spread</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {results.series.map((s, i) => (
                  <tr key={i} className="hover:bg-slate-800/40">
                    <td className="py-2 px-3 text-slate-300">{s.date}</td>
                    <td className="py-2 px-3 text-indigo-400 font-bold">{s.apix.toFixed(2)}</td>
                    <td className="py-2 px-3 text-emerald-400 font-semibold">{s.dgca_reference.toFixed(2)}</td>
                    <td className="py-2 px-3 text-slate-300">{s.spread > 0 ? `+${s.spread.toFixed(2)}` : s.spread.toFixed(2)}</td>
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
