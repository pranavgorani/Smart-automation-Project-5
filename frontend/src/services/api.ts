import {
  CurrentIndexResponse,
  HistoricalIndexPoint,
  RouteMetadata,
  AirlineMetadata,
  AirfareQuote,
  LeadTimeData,
  AirlineAnalytic,
  AnomalyRecord,
  ExecutiveSummary,
  HeatmapResponse,
  BacktestResults,
  SystemHealth,
  QualityMetrics,
} from '../types';

const API_BASE = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchJson<SystemHealth>(`${API_BASE}/api/health`),
  getCurrentIndex: () => fetchJson<CurrentIndexResponse>(`${API_BASE}/api/index/current`),
  getIndexHistory: (days: number = 30) =>
    fetchJson<HistoricalIndexPoint[]>(`${API_BASE}/api/index/history?days=${days}`),
  getRouteIndex: (route: string, days: number = 30) =>
    fetchJson<any[]>(`${API_BASE}/api/index/route/${route}?days=${days}`),
  getRoutes: () => fetchJson<RouteMetadata[]>(`${API_BASE}/api/routes`),
  getAirlines: () => fetchJson<AirlineMetadata[]>(`${API_BASE}/api/airlines`),
  getQuotes: (params: Record<string, string | number | boolean | undefined>) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    return fetchJson<{ total: number; results: AirfareQuote[] }>(
      `${API_BASE}/api/flights?${query.toString()}`
    );
  },
  getRouteFares: (route?: string) =>
    fetchJson<any>(`${API_BASE}/api/fares${route ? `?route=${route}` : ''}`),
  getLeadTime: (route?: string) =>
    fetchJson<LeadTimeData>(`${API_BASE}/api/analytics/lead-time${route ? `?route=${route}` : ''}`),
  getAirlineAnalytics: () => fetchJson<AirlineAnalytic[]>(`${API_BASE}/api/analytics/airlines`),
  getAnomalies: (threshold: number = 25) =>
    fetchJson<AnomalyRecord[]>(`${API_BASE}/api/analytics/anomalies?threshold_pct=${threshold}`),
  getSummary: () => fetchJson<ExecutiveSummary>(`${API_BASE}/api/analytics/summary`),
  getForecast: (days: number = 7) => fetchJson<any>(`${API_BASE}/api/analytics/forecast?days=${days}`),
  getHeatmap: (timeframe: string = 'daily') =>
    fetchJson<HeatmapResponse>(`${API_BASE}/api/analytics/heatmap?timeframe=${timeframe}`),
  getSources: () => fetchJson<any[]>(`${API_BASE}/api/sources`),
  getQuality: () => fetchJson<QualityMetrics>(`${API_BASE}/api/quality`),
  getQualityHistory: () => fetchJson<any[]>(`${API_BASE}/api/quality/history`),
  getBacktest: (days: number = 30) => fetchJson<BacktestResults>(`${API_BASE}/api/backtest?days=${days}`),
  getMethodology: () => fetchJson<any>(`${API_BASE}/api/methodology`),
  triggerCollect: () => fetchJson<any>(`${API_BASE}/api/collect/run`, { method: 'POST' }),
  triggerDemoSeed: () => fetchJson<any>(`${API_BASE}/api/admin/demo/seed`, { method: 'POST' }),
  updateWeights: (weights: Record<string, number>) =>
    fetchJson<any>(`${API_BASE}/api/admin/weights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(weights),
    }),
  uploadCsv: (file: File, datasetType: string = 'QUOTES') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);
    return fetchJson<any>(`${API_BASE}/api/data/upload`, {
      method: 'POST',
      body: formData,
    });
  },
};
