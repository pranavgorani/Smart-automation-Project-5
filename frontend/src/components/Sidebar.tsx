import React from 'react';
import {
  LayoutDashboard,
  LineChart,
  Navigation,
  Clock,
  Plane,
  ShieldCheck,
  FlaskConical,
  BrainCircuit,
  Database,
  BookOpen,
  Activity,
  Layers,
} from 'lucide-react';

export type TabKey =
  | 'overview'
  | 'index'
  | 'routes'
  | 'lead-time'
  | 'airlines'
  | 'quality'
  | 'backtest'
  | 'anomalies'
  | 'sources'
  | 'methodology'
  | 'health';

interface SidebarProps {
  activeTab: TabKey;
  onSelectTab: (tab: TabKey) => void;
  isDemo: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, isDemo }) => {
  const menuItems: { key: TabKey; label: string; icon: React.ElementType; badge?: string }[] = [
    { key: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
    { key: 'index', label: 'Airfare Index (APIx)', icon: LineChart },
    { key: 'routes', label: 'Route Explorer & Heatmap', icon: Navigation },
    { key: 'lead-time', label: 'Lead-Time Analytics', icon: Clock },
    { key: 'airlines', label: 'Airline Analytics', icon: Plane },
    { key: 'quality', label: 'Data Quality & Audit', icon: ShieldCheck },
    { key: 'backtest', label: 'Backtesting & CPI', icon: FlaskConical },
    { key: 'anomalies', label: 'AI Insights & Anomalies', icon: BrainCircuit, badge: 'Grounded' },
    { key: 'sources', label: 'Data Sources & Ingestion', icon: Database },
    { key: 'methodology', label: 'Methodology & Specs', icon: BookOpen },
    { key: 'health', label: 'System Health & Admin', icon: Activity },
  ];

  return (
    <aside className="w-64 bg-slate-900/95 border-r border-slate-800 flex flex-col h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-sky-500 flex items-center justify-center shadow-lg shadow-indigo-600/30">
            <Plane className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-tight text-white font-mono flex items-center gap-1.5">
              AIRFARE-X <span className="text-indigo-400 font-sans text-xs font-semibold px-1 py-0.5 rounded bg-indigo-950/60 border border-indigo-700/50">INDIA</span>
            </h1>
            <p className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">
              MoSPI / DIID Prototype
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Analytics & Intelligence
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.key;
          return (
            <button
              key={item.key}
              onClick={() => onSelectTab(item.key)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25 font-semibold'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300 border border-indigo-700/50">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 text-[11px] text-slate-400 flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <span>Engine Status</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-mono text-[10px]">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Operational
          </span>
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-400">
          <span>Mode</span>
          <span className="font-mono">{isDemo ? 'SYNTHETIC_MOCK' : 'LIVE_API'}</span>
        </div>
        <div className="text-[9px] text-slate-400 pt-1 border-t border-slate-800/50 mt-1">
          v1.0.0 • Smart Automation Theme
        </div>
      </div>
    </aside>
  );
};
