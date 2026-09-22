import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  subtitle?: string;
  icon: LucideIcon;
  iconColor?: string;
  badge?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  change,
  changeLabel = '24h change',
  subtitle,
  icon: Icon,
  iconColor = 'text-indigo-400',
  badge,
}) => {
  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;

  return (
    <div className="terminal-card p-5 relative overflow-hidden group transition-all duration-300 hover:shadow-xl hover:shadow-indigo-950/20">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">
              {title}
            </span>
            {badge && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">
                {badge}
              </span>
            )}
          </div>
          <div className="text-2xl font-bold font-mono tracking-tight text-white mt-1">
            {value}
          </div>
        </div>

        <div className={`p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/60 ${iconColor} group-hover:scale-110 transition-transform`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs">
        {change !== undefined ? (
          <div className="flex items-center gap-1.5 font-medium">
            <span
              className={`flex items-center px-1.5 py-0.5 rounded text-[11px] font-mono ${
                isPositive
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  : isNegative
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-slate-800 text-slate-400'
              }`}
            >
              {isPositive && <TrendingUp className="w-3 h-3 mr-0.5" />}
              {isNegative && <TrendingDown className="w-3 h-3 mr-0.5" />}
              {change > 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`}
            </span>
            <span className="text-slate-400">{changeLabel}</span>
          </div>
        ) : subtitle ? (
          <span className="text-slate-400">{subtitle}</span>
        ) : null}
      </div>
    </div>
  );
};
