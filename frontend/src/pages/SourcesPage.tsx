import React, { useState, useEffect } from 'react';
import { Database, ShieldCheck, CheckCircle2, AlertCircle, Upload, Play, RefreshCw, FileUp } from 'lucide-react';
import { api } from '../services/api';

export const SourcesPage: React.FC = () => {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [demoRunning, setDemoRunning] = useState(false);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const res = await api.getSources();
      setSources(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDemo = async () => {
    setDemoRunning(true);
    try {
      await api.triggerDemoSeed();
      alert('✓ Demo dataset successfully generated, cleaned, and indexed for 30 historical days!');
      fetchSources();
    } catch (e: any) {
      alert(`Error running demo seed: ${e.message}`);
    } finally {
      setDemoRunning(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, type: 'QUOTES' | 'DGCA') => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const res = await api.uploadCsv(file, type);
      setUploadStatus(`✓ Upload successful: ${res.quotes_accepted || res.records_saved} records ingested.`);
      setTimeout(() => setUploadStatus(null), 5000);
    } catch (err: any) {
      setUploadStatus(`✗ Upload failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Data Sources & Provenance Architecture</h2>
          <p className="text-xs text-slate-400 mt-1">
            Multi-source ingestion channels with strict compliance safeguards. Distinguishes LIVE_API, PERMITTED_WEB, MOCK, and CSV_IMPORT.
          </p>
        </div>

        <button
          onClick={handleRunDemo}
          disabled={demoRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
        >
          <Play className={`w-4 h-4 fill-current ${demoRunning ? 'animate-spin' : ''}`} />
          <span>{demoRunning ? 'Generating 10,000+ Observations...' : 'Run One-Click Demo Pipeline'}</span>
        </button>
      </div>

      {uploadStatus && (
        <div className="p-3 rounded-lg bg-slate-900 border border-indigo-500 text-xs text-indigo-300 font-mono">
          {uploadStatus}
        </div>
      )}

      {/* Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((s, idx) => {
          const isMock = s.type === 'MOCK';
          const isLive = s.type === 'LIVE_API';
          const isWeb = s.type === 'PERMITTED_WEB';

          return (
            <div key={idx} className="terminal-card p-5 border border-slate-700/80 relative">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                        isLive
                          ? 'bg-sky-950 text-sky-300 border-sky-700/50'
                          : isMock
                          ? 'bg-amber-950 text-amber-300 border-amber-700/50'
                          : isWeb
                          ? 'bg-teal-950 text-teal-300 border-teal-700/50'
                          : 'bg-slate-800 text-slate-300 border-slate-700'
                      }`}
                    >
                      {s.type}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      Rate Limit: {s.rate_limit_seconds || 0}s
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-1.5">{s.name}</h3>
                </div>

                <span
                  className={`flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded-full ${
                    s.status === 'ACTIVE'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${s.status === 'ACTIVE' ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                  {s.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-800 text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[10px] block">SUCCESS RATE</span>
                  <span className="text-slate-200 font-bold">{s.success_rate || 100.0}%</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block">COMPLIANCE</span>
                  <span className="text-emerald-400 font-bold">{s.compliance_status || 'COMPLIANT'}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Manual CSV Upload Fallback Panel */}
      <div className="terminal-card p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-1 flex items-center gap-2">
          <Upload className="w-4 h-4 text-indigo-400" />
          <span>Manual CSV Ingestion Fallback (Section 19 & 54)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Upload verified domestic airfare observation CSVs or official DGCA monthly reports when automated connectors are offline.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold text-slate-200 block mb-1">Airfare Quotes CSV</span>
              <p className="text-[11px] text-slate-400 mb-3">
                Expected columns: origin, destination, airline, departure_date, total_fare, advance_purchase_days
              </p>
            </div>
            <label className="cursor-pointer inline-flex items-center justify-center gap-2 px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition">
              <FileUp className="w-3.5 h-3.5 text-indigo-400" />
              <span>Select Quotes CSV</span>
              <input type="file" accept=".csv" className="hidden" onChange={(e) => handleFileUpload(e, 'QUOTES')} />
            </label>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold text-slate-200 block mb-1">DGCA Monthly Benchmark CSV</span>
              <p className="text-[11px] text-slate-400 mb-3">
                Expected columns: month, route, airline, passengers, average_fare, fuel_surcharge
              </p>
            </div>
            <label className="cursor-pointer inline-flex items-center justify-center gap-2 px-3 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition">
              <FileUp className="w-3.5 h-3.5 text-emerald-400" />
              <span>Select DGCA Benchmark CSV</span>
              <input type="file" accept=".csv" className="hidden" onChange={(e) => handleFileUpload(e, 'DGCA')} />
            </label>
          </div>
        </div>
      </div>

      {/* Ethical Safeguards Audit Checklist */}
      <div className="terminal-card p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>MoSPI Ethical Scraping & Legal Safeguards Compliance Checklist</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Strict robots.txt parsing before every HTTP request</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Respectful exponential backoff (1s, 2s, 4s, 8s)</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Zero CAPTCHA solving or access control circumvention</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Zero stealth browser fingerprint spoofing or proxy rotation</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Source-specific domain allowlist configuration</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Unambiguous source attribution (LIVE_API, MOCK, CSV_IMPORT)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
