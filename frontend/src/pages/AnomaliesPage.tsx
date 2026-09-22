import React, { useState, useEffect } from 'react';
import { BrainCircuit, AlertTriangle, Sparkles, TrendingUp, RefreshCw, Info, Calendar } from 'lucide-react';
import { AnomalyRecord, ExecutiveSummary } from '../types';
import { api } from '../services/api';

export const AnomaliesPage: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [threshold, setThreshold] = useState(25);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [threshold]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [anomRes, sumRes, foreRes] = await Promise.all([
        api.getAnomalies(threshold),
        api.getSummary(),
        api.getForecast(7),
      ]);
      setAnomalies(anomRes);
      setSummary(sumRes);
      setForecast(foreRes);
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
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">AI Insights & Grounded Anomaly Detection</h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-violet-950 text-violet-300 border border-violet-700/50">
              Econometric AI
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Rule-grounded econometric explanations for significant fare volatility. Section 57 Compliance: Explanations are derived exclusively from observed database variables.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Anomaly Threshold:</span>
          <select
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="15">±15% Movement</option>
            <option value="25">±25% Movement</option>
            <option value="35">±35% Surge/Drop</option>
          </select>
        </div>
      </div>

      {/* MoSPI Leadership Executive Briefing */}
      {summary && (
        <div className="terminal-card p-6 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border-l-4 border-indigo-500">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Official MoSPI / DIID Natural-Language Executive Briefing</span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight leading-snug">{summary.headline}</h3>
          <div className="mt-4 space-y-2 text-xs text-slate-300">
            {summary.takeaways.map((t, idx) => (
              <div key={idx} className="flex items-start gap-2.5">
                <span className="w-2 h-2 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0"></span>
                <span>{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detected Sector Anomalies with AI Grounded Explanations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Detected Sector Movements Exceeding ±{threshold}% ({anomalies.length})</span>
          </h3>
          <span className="text-xs text-slate-400 font-mono">Real-time scan across 13 trunk routes</span>
        </div>

        {anomalies.length === 0 ? (
          <div className="terminal-card p-8 text-center text-slate-400 text-xs">
            No sector movements exceeded the ±{threshold}% threshold in the most recent observation cycle.
          </div>
        ) : (
          anomalies.map((anom, idx) => (
            <div key={idx} className="terminal-card p-5 border border-slate-700/80 hover:border-indigo-500/50 transition">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <span className="text-base font-bold font-mono text-white bg-slate-800 px-2.5 py-1 rounded">
                    {anom.route}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                      anom.change_pct > 0 ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                    }`}
                  >
                    {anom.change_pct > 0 ? `+${anom.change_pct.toFixed(1)}%` : `${anom.change_pct.toFixed(1)}%`}
                  </span>
                  <span className="text-xs text-slate-400">
                    ₹{anom.previous_median.toLocaleString()} → <span className="text-slate-100 font-bold">₹{anom.current_median.toLocaleString()}</span>
                  </span>
                </div>

                <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                  <span>Cycle Date: {anom.date}</span>
                </div>
              </div>

              {/* Grounded Econometric Explanation */}
              <div className="mt-3 pt-1">
                <div className="text-xs font-bold text-indigo-300 flex items-center gap-1.5 mb-1.5">
                  <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Grounded Econometric Attribution</span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  {anom.ai_explanation.summary}
                </p>

                <div className="mt-2.5 flex flex-wrap gap-2 text-[11px]">
                  {anom.ai_explanation.grounded_factors.map((factor, fIdx) => (
                    <span key={fIdx} className="px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Experimental Forecast Preview */}
      {forecast?.forecast_points && (
        <div className="terminal-card p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Experimental 7-Day Forward Scenario Projection</h3>
              <p className="text-xs text-slate-400">{forecast.disclaimer}</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
              Holt Double Exponential Smoothing
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-7 gap-3 font-mono text-xs">
            {forecast.forecast_points.map((p: any, i: number) => (
              <div key={i} className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 text-center">
                <div className="text-[10px] text-slate-400">{p.date.split('-').slice(1).join('/')}</div>
                <div className="text-base font-bold text-indigo-400 mt-1">{p.forecast_value.toFixed(2)}</div>
                <div className="text-[9px] text-slate-400 mt-1">
                  [{p.confidence_lower.toFixed(1)} - {p.confidence_upper.toFixed(1)}]
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
