export interface CurrentIndexResponse {
  index_name: string;
  index_code: string;
  value: number;
  daily_change_pct: number;
  weekly_change_pct: number;
  monthly_change_pct: number;
  base_period: string;
  routes: number;
  observations: number;
  quality_score: number;
  methodology_version: string;
  as_of_date?: string;
}

export interface HistoricalIndexPoint {
  id: number;
  index_date: string;
  index_value: number;
  daily_change: number;
  weekly_change: number;
  monthly_change: number;
  base_period: string;
  route_count: number;
  observation_count: number;
  confidence_score: number;
}

export interface RouteMetadata {
  id?: number;
  origin: string;
  destination: string;
  route_code: string;
  city_pair: string;
  passenger_weight?: number;
  route_weight: number;
  active: boolean;
}

export interface AirlineMetadata {
  airline_code: string;
  name: string;
  market_share: number;
  active: boolean;
}

export interface AirfareQuote {
  id: number;
  source: string;
  source_type: string;
  source_reference?: string;
  origin: string;
  destination: string;
  route: string;
  airline: string;
  flight_number?: string;
  departure_date: string;
  departure_time: string;
  arrival_time: string;
  search_timestamp: string;
  advance_purchase_days: number;
  fare_class: string;
  fare_family: string;
  base_fare: number;
  taxes: number;
  user_development_fee: number;
  convenience_fee: number;
  other_charges: number;
  total_fare: number;
  currency: string;
  availability: number;
  stops: number;
  refundability: string;
  data_quality_score: number;
  is_outlier: boolean;
  outlier_method?: string;
  outlier_score?: number;
}

export interface LeadTimeData {
  route_filter: string;
  disclaimer: string;
  baseline_window: string;
  empirical_elasticity: number;
  interpretation: string;
  curve: {
    advance_window: string;
    advance_days: number;
    median_fare: number;
    mean_fare: number;
    p25: number;
    p75: number;
    relative_index: number;
    observations: number;
  }[];
}

export interface AirlineAnalytic {
  airline: string;
  median_fare: number;
  average_fare: number;
  fare_volatility_pct: number;
  routes_covered: number;
  observations: number;
  data_quality_score: number;
}

export interface AnomalyRecord {
  route: string;
  date: string;
  current_median: number;
  previous_median: number;
  change_pct: number;
  anomaly_type: string;
  severity: string;
  ai_explanation: {
    summary: string;
    grounded_factors: string[];
    observed_metrics: {
      day_of_week: string;
      short_lead_window_ratio_pct: number;
      observations_sampled: number;
    };
  };
}

export interface ExecutiveSummary {
  headline: string;
  as_of_date?: string;
  takeaways: string[];
  full_briefing: string;
}

export interface HeatmapResponse {
  timeframe: string;
  as_of_date: string;
  comparison_date: string;
  origins: string[];
  destinations: string[];
  matrix: {
    origin: string;
    destinations: Record<
      string,
      {
        route?: string;
        change_pct?: number | null;
        median_fare?: number | null;
        index_value?: number;
        active: boolean;
      }
    >;
  }[];
}

export interface BacktestResults {
  validation_label: string;
  disclaimer: string;
  period: {
    start_date: string;
    end_date: string;
    days_evaluated: number;
  };
  metrics: {
    mae: number;
    rmse: number;
    mape: number;
    correlation: number;
    directional_accuracy_pct: number;
    data_coverage_pct: number;
    routes_covered: number;
    total_observations: number;
  };
  series: {
    date: string;
    apix: number;
    dgca_reference: number;
    spread: number;
  }[];
}

export interface SystemHealth {
  status: string;
  app_name: string;
  environment: string;
  demo_mode: boolean;
  demo_banner: string | null;
  database: {
    status: string;
    latency_ms: number;
    engine: string;
  };
  connectors: Record<string, string>;
  compliance: Record<string, boolean>;
  server_time: string;
}

export interface QualityMetrics {
  source: string;
  quality_score: number;
  completeness_score: number;
  validity_score: number;
  timeliness_score: number;
  uniqueness_score: number;
  consistency_score: number;
  records_collected: number;
  records_valid: number;
  records_rejected: number;
  duplicates: number;
  outliers: number;
}
