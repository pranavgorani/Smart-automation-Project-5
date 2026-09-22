import React, { useState, useEffect } from 'react';
import { BookOpen, Calculator, Layers, FileCode, CheckCircle2, ExternalLink, Info } from 'lucide-react';
import { api } from '../services/api';

export const MethodologyPage: React.FC = () => {
  const [spec, setSpec] = useState<any>(null);

  useEffect(() => {
    api.getMethodology().then(setSpec).catch(console.error);
  }, []);

  const pipelineSteps = [
    { title: '1. Acquisition', desc: 'Permitted APIs & ethical web fetching checking robots.txt' },
    { title: '2. Validation', desc: 'Schema, airport code, currency, and date range verification' },
    { title: '3. Normalization', desc: 'Base fare + taxes + UDF + convenience fee decomposition' },
    { title: '4. Deduplication', desc: 'Deterministic SHA-256 fingerprint matching' },
    { title: '5. Outlier Flagging', desc: 'Non-destructive IQR & MAD statistical tagging' },
    { title: '6. Route Relatives', desc: 'R(r,t) = P(r,t) / P(r,base) median ratio computation' },
    { title: '7. Laspeyres Aggregation', desc: 'APIx = 100 × Σ [w_r × R(r,t)] across trunk routes' },
    { title: '8. Quality Audit', desc: '5-dimension scoring and validation publishing' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Statistical Methodology & Formula Specifications</h2>
        <p className="text-xs text-slate-400 mt-1">
          Formal mathematical framework for the Experimental Real-Time Airfare Price Index (APIx) developed for MoSPI / DIID.
        </p>
      </div>

      {/* Disclaimers */}
      <div className="p-4 rounded-lg bg-amber-950/30 border border-amber-800/60 text-xs text-amber-200 flex items-start gap-3">
        <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-white uppercase tracking-wider text-[11px] block">MoSPI Governance Disclaimer</span>
          {spec?.disclaimer ||
            'This index is an experimental research prototype intended to explore the feasibility of augmenting the official Consumer Price Index (CPI) Transport/Airfare subgroup with high-frequency automated web-scraped data. It does NOT constitute official Government of India CPI statistics.'}
        </div>
      </div>

      {/* Pipeline Flowchart */}
      <div className="terminal-card p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>End-to-End Data Processing Pipeline</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {pipelineSteps.map((step, idx) => (
            <div key={idx} className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 relative">
              <span className="text-xs font-bold text-indigo-300 block mb-1">{step.title}</span>
              <p className="text-[11px] text-slate-400 leading-snug">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Mathematical Formulas Card */}
      <div className="terminal-card p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Calculator className="w-4 h-4 text-emerald-400" />
          <span>Core Mathematical Formulas</span>
        </h3>

        <div className="space-y-4 font-mono text-xs">
          <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800">
            <span className="text-slate-400 text-[11px] block mb-1">1. Elementary Route Median Fare</span>
            <div className="text-indigo-300 font-bold text-sm">P(r, d, t) = Median [ TotalFare_i ] for flight i in route r, window d, day t</div>
            <p className="text-[10px] text-slate-400 mt-1 font-sans">
              Median is statistically preferred over arithmetic mean to prevent skewness from dynamic surge pricing spikes.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800">
            <span className="text-slate-400 text-[11px] block mb-1">2. Price Relative Formula</span>
            <div className="text-emerald-300 font-bold text-sm">R(r, t) = P(r, t) / P(r, base)</div>
            <p className="text-[10px] text-slate-400 mt-1 font-sans">
              Compares the current observed route composite price against the established base period price (2026-01-01 = 100.0).
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800">
            <span className="text-slate-400 text-[11px] block mb-1">3. Laspeyres-Type Route-Weighted Index (APIx)</span>
            <div className="text-sky-300 font-bold text-sm">APIx(t) = 100 × Σ [ w_r × R(r, t) ]  where Σ w_r = 1.0</div>
            <p className="text-[10px] text-slate-400 mt-1 font-sans">
              Aggregates across all 13 domestic trunk pairs utilizing passenger volume expenditure weights derived from DGCA annual statistics.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800">
            <span className="text-slate-400 text-[11px] block mb-1">4. Lead-Time Empirical Elasticity Estimate</span>
            <div className="text-amber-300 font-bold text-sm">Elasticity = (% Δ Fare) / (% Δ Advance Purchase Days)</div>
            <p className="text-[10px] text-slate-400 mt-1 font-sans">
              Measures the empirical pricing gradient between advance planning (T+45) and emergency/short-horizon booking (T+1).
            </p>
          </div>
        </div>
      </div>

      {/* Advance Purchase Window Specification */}
      <div className="terminal-card p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Advance Purchase Window Treatment</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded bg-slate-900 border border-slate-800">
            <span className="font-bold text-indigo-400 block">T+1 (1 Day)</span>
            <span className="text-slate-400 text-[11px]">Emergency & immediate business demand</span>
          </div>
          <div className="p-3 rounded bg-slate-900 border border-slate-800">
            <span className="font-bold text-indigo-400 block">T+7 (7 Days)</span>
            <span className="text-slate-400 text-[11px]">Short-horizon commercial travel</span>
          </div>
          <div className="p-3 rounded bg-slate-900 border border-slate-800">
            <span className="font-bold text-indigo-400 block">T+15 (15 Days)</span>
            <span className="text-slate-400 text-[11px]">Standard domestic leisure planning</span>
          </div>
          <div className="p-3 rounded bg-slate-900 border border-slate-800">
            <span className="font-bold text-indigo-400 block">T+30 (30 Days)</span>
            <span className="text-slate-400 text-[11px]">Baseline domestic planning horizon</span>
          </div>
          <div className="p-3 rounded bg-slate-900 border border-slate-800">
            <span className="font-bold text-indigo-400 block">T+45 (45 Days)</span>
            <span className="text-slate-400 text-[11px]">Promotional early-booking baseline</span>
          </div>
        </div>
      </div>
    </div>
  );
};
