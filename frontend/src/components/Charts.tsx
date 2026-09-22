import React, { useState } from 'react';

// ==============================================================================
// 1. TrendLineChart (Responsive SVG Line Chart)
// ==============================================================================
interface Point {
  date: string;
  value: number;
  reference?: number;
}

interface TrendLineChartProps {
  data: Point[];
  title?: string;
  subtitle?: string;
  height?: number;
  showReference?: boolean;
  valuePrefix?: string;
  referenceLabel?: string;
}

export const TrendLineChart: React.FC<TrendLineChartProps> = ({
  data,
  title,
  subtitle,
  height = 240,
  showReference = false,
  valuePrefix = '',
  referenceLabel = 'DGCA Reference',
}) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return <div className="h-48 flex items-center justify-center text-slate-500 text-xs">No chart observations available</div>;
  }

  const values = data.map((d) => d.value);
  const refValues = showReference ? data.filter((d) => d.reference !== undefined).map((d) => d.reference!) : [];
  const allValues = [...values, ...refValues, 100.0];

  const minVal = Math.floor(Math.min(...allValues) - 2);
  const maxVal = Math.ceil(Math.max(...allValues) + 2);
  const valRange = maxVal - minVal || 1;

  const width = 800;
  const paddingX = 40;
  const paddingY = 30;
  const chartW = width - paddingX * 2;
  const chartH = height - paddingY * 2;

  const getX = (idx: number) => paddingX + (idx / (data.length - 1 || 1)) * chartW;
  const getY = (val: number) => height - paddingY - ((val - minVal) / valRange) * chartH;

  // Generate SVG path for APIx series
  const linePoints = data.map((d, i) => `${getX(i)},${getY(d.value)}`).join(' ');
  const areaPoints = `${getX(0)},${height - paddingY} ${linePoints} ${getX(data.length - 1)},${height - paddingY}`;

  // Generate SVG path for reference series if requested
  const refPoints = showReference
    ? data
        .filter((d) => d.reference !== undefined)
        .map((d, i) => `${getX(i)},${getY(d.reference!)}`)
        .join(' ')
    : '';

  const baseY = getY(100.0);

  return (
    <div className="w-full">
      {(title || subtitle) && (
        <div className="flex items-center justify-between mb-3">
          <div>
            {title && <h3 className="text-sm font-semibold text-slate-200">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-indigo-500"></span>
              <span className="text-slate-300">APIx Index</span>
            </div>
            {showReference && (
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 border-t border-emerald-400 border-dashed"></span>
                <span className="text-slate-300">{referenceLabel}</span>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="relative w-full overflow-hidden">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible select-none">
          <defs>
            <linearGradient id="apixGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366F1" stopOpacity="0.35" />
              <stop offset="100%" stopColor="#6366F1" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((ratio, idx) => {
            const y = paddingY + ratio * chartH;
            const labelVal = maxVal - ratio * valRange;
            return (
              <g key={idx}>
                <line x1={paddingX} y1={y} x2={width - paddingX} y2={y} stroke="#334155" strokeDasharray="3 3" strokeOpacity="0.5" />
                <text x={paddingX - 8} y={y + 3} fill="#64748B" fontSize="9" textAnchor="end" fontFamily="monospace">
                  {labelVal.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Base 100 Reference line */}
          {baseY >= paddingY && baseY <= height - paddingY && (
            <line x1={paddingX} y1={baseY} x2={width - paddingX} y2={baseY} stroke="#94A3B8" strokeDasharray="4 4" strokeWidth="1.2" opacity="0.6" />
          )}

          {/* Shaded Area */}
          <polygon points={areaPoints} fill="url(#apixGradient)" />

          {/* Reference Line */}
          {showReference && refPoints && (
            <polyline fill="none" stroke="#10B981" strokeWidth="2" strokeDasharray="4 3" points={refPoints} />
          )}

          {/* Main APIx Line */}
          <polyline fill="none" stroke="#6366F1" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={linePoints} />

          {/* Interactive Hover Nodes */}
          {data.map((d, i) => (
            <circle
              key={i}
              cx={getX(i)}
              cy={getY(d.value)}
              r={hoverIndex === i ? 5 : 2.5}
              fill={hoverIndex === i ? '#818CF8' : '#4F46E5'}
              stroke="#0F172A"
              strokeWidth="2"
              className="cursor-pointer transition-all"
              onMouseEnter={() => setHoverIndex(i)}
              onMouseLeave={() => setHoverIndex(null)}
            />
          ))}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoverIndex !== null && data[hoverIndex] && (
          <div
            className="absolute top-2 right-4 bg-slate-900/90 border border-slate-700 px-3 py-2 rounded shadow-xl text-xs font-mono z-20 pointer-events-none"
          >
            <div className="text-slate-400 text-[10px]">{data[hoverIndex].date}</div>
            <div className="text-indigo-400 font-bold">
              APIx: {valuePrefix}{data[hoverIndex].value.toFixed(2)}
            </div>
            {data[hoverIndex].reference !== undefined && (
              <div className="text-emerald-400">
                DGCA Ref: {valuePrefix}{data[hoverIndex].reference!.toFixed(2)}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Date ticks on bottom */}
      <div className="flex justify-between text-[10px] text-slate-400 font-mono px-3 mt-1">
        <span>{data[0]?.date}</span>
        <span>{data[Math.floor(data.length / 2)]?.date}</span>
        <span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  );
};

// ==============================================================================
// 2. BarChart (Horizontal or Vertical Bars)
// ==============================================================================
interface BarItem {
  label: string;
  value: number;
  secondaryValue?: number;
  highlight?: boolean;
}

export const SimpleBarChart: React.FC<{
  items: BarItem[];
  title?: string;
  unit?: string;
  horizontal?: boolean;
}> = ({ items, title, unit = '', horizontal = false }) => {
  if (!items || items.length === 0) return null;
  const maxVal = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="w-full">
      {title && <h3 className="text-sm font-semibold text-slate-200 mb-3">{title}</h3>}
      <div className="space-y-2.5">
        {items.map((item, idx) => {
          const pct = Math.min(100, Math.max(5, (item.value / maxVal) * 100));
          return (
            <div key={idx} className="text-xs">
              <div className="flex justify-between text-slate-300 font-medium mb-1">
                <span className="font-mono">{item.label}</span>
                <span className="font-mono text-slate-200">
                  {unit}
                  {item.value.toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden border border-slate-700/50">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.highlight ? 'bg-gradient-to-r from-amber-500 to-amber-400' : 'bg-gradient-to-r from-indigo-600 to-sky-400'
                  }`}
                  style={{ width: `${pct}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
