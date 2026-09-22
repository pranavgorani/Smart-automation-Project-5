import React from 'react';
import { Plane, ShieldCheck, Activity, Layers, Info } from 'lucide-react';
import { AirlineAnalytic } from '../types';

interface AirlineAnalyticsPageProps {
  airlines: AirlineAnalytic[];
}

export const AirlineAnalyticsPage: React.FC<AirlineAnalyticsPageProps> = ({ airlines }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">
          Airline Comparative Analytics
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Neutral comparative metrics across domestic scheduled airlines. Section 28 Compliance: Carriers are presented objectively without ranking.
        </p>
      </div>

      <div className="terminal-card p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Carrier</th>
                <th className="py-2.5 px-3">Median Airfare</th>
                <th className="py-2.5 px-3">Average Airfare</th>
                <th className="py-2.5 px-3">Volatility (CV %)</th>
                <th className="py-2.5 px-3">Sectors Covered</th>
                <th className="py-2.5 px-3">Quotes Sampled</th>
                <th className="py-2.5 px-3">Data Quality</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {airlines.map((a) => (
                <tr key={a.airline} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-3 font-semibold text-slate-200 flex items-center gap-2">
                    <Plane className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{a.airline}</span>
                  </td>
                  <td className="py-3 px-3 font-bold text-indigo-400">
                    ₹{a.median_fare.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    ₹{Math.round(a.average_fare).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {a.fare_volatility_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{a.routes_covered} of 13</td>
                  <td className="py-3 px-3 text-slate-400">{a.observations.toLocaleString()}</td>
                  <td className="py-3 px-3">
                    <span className="text-emerald-400 font-semibold">{a.data_quality_score.toFixed(1)}%</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Carrier Profiles & Operational Focus */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="terminal-card p-4">
          <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">Market Share Distribution</div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            IndiGo constitutes ~61.8% of domestic passenger volume across trunk routes, followed by Air India Group (~21.7%), Akasa Air (~5.4%), and SpiceJet (~4.6%).
          </p>
        </div>
        <div className="terminal-card p-4">
          <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">Fare Dispersion Profile</div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Full-service operations reflect bundled checked baggage and meal inclusions, while Low-Cost Carriers (LCCs) emphasize unbundled ancillary pricing.
          </p>
        </div>
        <div className="terminal-card p-4">
          <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">Regional Connectivity</div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Regional operators such as Alliance Air maintain essential connectivity on specialized Tier-2/Tier-3 sectors and leisure corridors (e.g. Goa).
          </p>
        </div>
      </div>
    </div>
  );
};
