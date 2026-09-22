import React, { useState, useEffect } from 'react';
import { Sidebar, TabKey } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { DemoBanner } from './components/DemoBanner';
import { OverviewPage } from './pages/OverviewPage';
import { AirfareIndexPage } from './pages/AirfareIndexPage';
import { RouteExplorerPage } from './pages/RouteExplorerPage';
import { LeadTimePage } from './pages/LeadTimePage';
import { AirlineAnalyticsPage } from './pages/AirlineAnalyticsPage';
import { DataQualityPage } from './pages/DataQualityPage';
import { BacktestingPage } from './pages/BacktestingPage';
import { AnomaliesPage } from './pages/AnomaliesPage';
import { SourcesPage } from './pages/SourcesPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { SystemHealthPage } from './pages/SystemHealthPage';

import {
  CurrentIndexResponse,
  HistoricalIndexPoint,
  RouteMetadata,
  AirlineMetadata,
  LeadTimeData,
  AirlineAnalytic,
  ExecutiveSummary,
} from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [isDemo, setIsDemo] = useState(true);
  const [currentIndex, setCurrentIndex] = useState<CurrentIndexResponse | null>(null);
  const [history, setHistory] = useState<HistoricalIndexPoint[]>([]);
  const [routes, setRoutes] = useState<RouteMetadata[]>([]);
  const [airlines, setAirlines] = useState<AirlineAnalytic[]>([]);
  const [leadTime, setLeadTime] = useState<LeadTimeData | null>(null);
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setIsRefreshing(true);
    try {
      const [currRes, histRes, routeRes, airRes, ltRes, sumRes, healthRes] = await Promise.allSettled([
        api.getCurrentIndex(),
        api.getIndexHistory(30),
        api.getRoutes(),
        api.getAirlineAnalytics(),
        api.getLeadTime(),
        api.getSummary(),
        api.getHealth(),
      ]);

      if (currRes.status === 'fulfilled') setCurrentIndex(currRes.value);
      if (histRes.status === 'fulfilled') setHistory(histRes.value);
      if (routeRes.status === 'fulfilled') setRoutes(routeRes.value);
      if (airRes.status === 'fulfilled') setAirlines(airRes.value);
      if (ltRes.status === 'fulfilled') setLeadTime(ltRes.value);
      if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
      if (healthRes.status === 'fulfilled') setIsDemo(healthRes.value.demo_mode);
    } catch (e) {
      console.error('Error loading dashboard data:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRunDemo = async () => {
    setIsSeeding(true);
    try {
      await api.triggerDemoSeed();
      await loadAllData();
    } catch (e: any) {
      alert(`Demo workflow notice: ${e.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Fixed Sidebar */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} isDemo={isDemo} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          currentDate={currentIndex?.as_of_date || '2026-03-22'}
          onRefresh={loadAllData}
          isRefreshing={isRefreshing}
        />

        <main className="p-6 md:p-8 flex-1 overflow-y-auto max-w-7xl w-full mx-auto">
          {/* Prominent Demo Mode Banner */}
          <DemoBanner isDemo={isDemo} onRunDemo={handleRunDemo} isLoading={isSeeding} />

          {/* Active Tab View */}
          {activeTab === 'overview' && (
            <OverviewPage
              currentIndex={currentIndex}
              history={history}
              leadTime={leadTime}
              airlines={airlines}
              summary={summary}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'index' && <AirfareIndexPage history={history} />}

          {activeTab === 'routes' && <RouteExplorerPage routes={routes} />}

          {activeTab === 'lead-time' && <LeadTimePage routes={routes} />}

          {activeTab === 'airlines' && <AirlineAnalyticsPage airlines={airlines} />}

          {activeTab === 'quality' && <DataQualityPage />}

          {activeTab === 'backtest' && <BacktestingPage />}

          {activeTab === 'anomalies' && <AnomaliesPage />}

          {activeTab === 'sources' && <SourcesPage />}

          {activeTab === 'methodology' && <MethodologyPage />}

          {activeTab === 'health' && (
            <SystemHealthPage routes={routes} onRefreshRoutes={loadAllData} />
          )}
        </main>
      </div>
    </div>
  );
};
