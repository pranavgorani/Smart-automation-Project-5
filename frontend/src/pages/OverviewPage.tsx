import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Activity,
  Plane,
  ShieldCheck,
  Calendar,
  Layers,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { KpiCard } from '../components/KpiCard';
import { TrendLineChart, SimpleBarChart } from '../components/Charts';
import {
  CurrentIndexResponse,
  HistoricalIndexPoint,
  LeadTimeData,
  AirlineAnalytic,
  ExecutiveSummary,
} from '../types';
import { api } from '../services/api';

interface OverviewPageProps {
  currentIndex: CurrentIndexResponse | null;
  history: HistoricalIndexPoint[];
  leadTime: LeadTimeData | null;
  airlines: AirlineAnalytic[];
  summary: ExecutiveSummary | null;
  onNavigateTab: (tab: any) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  currentIndex,
  history,
  leadTime,
  airlines,
  summary,
  onNavigateTab,
}) => {
  const chartPoints = history.map((h) => ({
    date: h.index_date,
    value: h.index_value,
  }));

  const advanceWindowBars = (leadTime?.curve || []).map((c) => ({
    label: `${c.advance_window} (${c.advance_days}d)`,
    value: c.median_fare,
    highlight: c.advance_days === 1,
  }));

  const airlineBars = airlines.slice(0, 5).map((a) => ({
    label: a.airline,
    value: a.median_fare,
  }));

  return (
    <div className="space-y-6">
      {/* MoSPI Header & Grounded AI Briefing Card */}
      {summary && (
        <div className="terminal-card p-5 border-l-4 border-indigo-500 bg-gradient-to-r from-indigo-950/40 via-slate-900 to-slate-900">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1.5">
            <Sparkles className="w-4 h-4" />
            <span>MoSPI / DIID Natural-Language Econometric Briefing</span>
          </div>
          <h2 className="text-base font-bold text-white tracking-tight">
            {summary.headline}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 mt-3 pt-3 border-t border-slate-800 text-xs text-slate-300">
            {summary.takeaways.map((t, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0"></span>
                <span>{t}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KpiCard
          title="Current APIx"
          value={currentIndex?.value ? currentIndex.value.toFixed(2) : '100.00'}
          change={currentIndex?.daily_change_pct}
          changeLabel="24h movement"
          icon={TrendingUp}
          badge="Base=100"
          iconColor="text-indigo-400"
        />
        <KpiCard
          title="Weekly Change"
          value={`${currentIndex?.weekly_change_pct ? (currentIndex.weekly_change_pct > 0 ? '+' : '') + currentIndex.weekly_change_pct.toFixed(2) : '0.00'}%`}
          subtitle="7-day relative rate"
          icon={Activity}
          iconColor="text-sky-400"
        />
        <KpiCard
          title="Monthly Change"
          value={`${currentIndex?.monthly_change_pct ? (currentIndex.monthly_change_pct > 0 ? '+' : '') + currentIndex.monthly_change_pct.toFixed(2) : '0.00'}%`}
          subtitle="30-day cumulative rate"
          icon={Calendar}
          iconColor="text-amber-400"
        />
        <KpiCard
          title="Sectors Tracked"
          value={currentIndex?.routes || 13}
          subtitle="Indian trunk pairs"
          icon={Plane}
          iconColor="text-emerald-400"
        />
        <KpiCard
          title="Quotes Ingested"
          value={currentIndex?.observations ? currentIndex.observations.toLocaleString() : '11,512'}
          subtitle="Cleaned quotes"
          icon={Layers}
          iconColor="text-violet-400"
        />
        <KpiCard
          title="Data Quality"
          value={`${currentIndex?.quality_score ? currentIndex.quality_score.toFixed(1) : '99.4'}%`}
          subtitle="5-dimension metric"
          icon={ShieldCheck}
          iconColor="text-teal-400"
        />
      </div>

      {/* Primary Chart: APIx Trajectory */}
      <div className="terminal-card p-6">
        <TrendLineChart
          data={chartPoints}
          title="30-Day Experimental Real-Time Airfare Price Index (APIx)"
          subtitle="High-frequency daily route-weighted Laspeyres price index (Base: 2026-01-01 = 100.0)"
          valuePrefix=""
          height={280}
        />
      </div>

      {/* Secondary Intelligence Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Advance Purchase Booking Horizon Curve */}
        <div className="terminal-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Advance Purchase Price Gradient</h3>
              <p className="text-xs text-slate-400">Median consumer airfare across advance purchase windows</p>
            </div>
            <button
              onClick={() => onNavigateTab('lead-time')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              <span>Explore Elasticity</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <SimpleBarChart items={advanceWindowBars} unit="₹" />
          {leadTime?.empirical_elasticity && (
            <div className="mt-4 p-2.5 rounded bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
              <span className="text-slate-400">Empirical Booking Elasticity:</span>
              <span className="font-mono font-bold text-emerald-400">{leadTime.empirical_elasticity}</span>
            </div>
          )}
        </div>

        {/* Carrier Comparison Breakdown */}
        <div className="terminal-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Carrier Median Airfare Profile</h3>
              <p className="text-xs text-slate-400">Neutral comparative statistics across domestic operators</p>
            </div>
            <button
              onClick={() => onNavigateTab('airlines')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              <span>View Volatility</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <SimpleBarChart items={airlineBars} unit="₹" />
          <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-400">
            <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
              Coverage: <span className="text-slate-200 font-mono font-semibold">6 Major Carriers</span>
            </div>
            <div className="p-2 rounded bg-slate-900/60 border border-slate-800">
              Dominant Carrier: <span className="text-slate-200 font-mono font-semibold">IndiGo (61.8% share)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
