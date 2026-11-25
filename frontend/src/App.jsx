import { createContext, useContext, useEffect, useRef, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { fetchSites } from "./api/endpoints";
import ExecutiveBriefCard from "./components/ai/ExecutiveBriefCard";
import SiteAssistantSidebar from "./components/ai/SiteAssistantSidebar";
import EnterpriseAnalyticsPanel from "./components/enterprise/EnterpriseAnalyticsPanel";
import MapPanel from "./components/MapPanel";
import SiteDetailsCard from "./components/SiteDetailsCard";
import TimelineSlider from "./components/TimelineSlider";
import TopNavbar from "./features/header/TopNavbar.jsx";
import HeroSection from "./features/hero/HeroSection.jsx";
import LandingPage from "./features/landing/LandingPage.jsx";
import LoginModal from "./components/auth/LoginModal.jsx";

const DashboardContext = createContext(null);

function DashboardPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const viewMode = location.pathname === "/enterprise" ? "enterprise" : "executive";
  const { sites, dataSource, selectedSiteId, setSelectedSiteId, activeYear, setActiveYear, loadingSites, recenterSignal, setRecenterSignal, onSignIn } = useContext(DashboardContext);
  const selectedSite = sites.find((site) => site.id === selectedSiteId) || null;
  return (
    <div className="app-shell">
      <TopNavbar viewMode={viewMode} onViewModeChange={(mode) => navigate(`/${mode}`)} dataSource={dataSource} isLoading={loadingSites} sites={sites} selectedSiteId={selectedSiteId} onSelectSite={(id) => { setSelectedSiteId(id); setRecenterSignal((previous) => previous + 1); }} onSignIn={onSignIn} />
      <HeroSection missionHref="/#mission" />
      <main id="platform" className="platform-workspace grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12">
        <section className="flex flex-col justify-between gap-4 rounded-xl border border-border-subtle bg-surface-card p-4 lg:col-span-8">
          {viewMode === "executive" ? <><MapPanel sites={sites} selectedSiteId={selectedSiteId} onSelectSite={setSelectedSiteId} recenterSignal={recenterSignal} onRecenter={() => setRecenterSignal((previous) => previous + 1)} /><ExecutiveBriefCard siteId={selectedSite?.id} /></> : <EnterpriseAnalyticsPanel site={selectedSite} activeYear={activeYear} />}
          <TimelineSlider activeYear={activeYear} onChangeYear={setActiveYear} />
        </section>
        <aside className="flex flex-col gap-4 lg:col-span-4">
          <SiteDetailsCard site={selectedSite} loading={loadingSites} />
          <div className="flex min-h-[420px] flex-1 overflow-hidden rounded-xl border border-border-subtle"><SiteAssistantSidebar activeSite={selectedSite} activeYear={activeYear} /></div>
        </aside>
      </main>
    </div>
  );
}

function AppRoutes() {
  const location = useLocation();
  const [sites, setSites] = useState([]);
  const [dataSource, setDataSource] = useState('mock');
  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [activeYear, setActiveYear] = useState(2026);
  const [loadingSites, setLoadingSites] = useState(true);
  const [recenterSignal, setRecenterSignal] = useState(0);
  const [loginOpen, setLoginOpen] = useState(false);
  const loadedSites = useRef(false);

  useEffect(() => {
    if (!location.pathname.startsWith('/executive') && !location.pathname.startsWith('/enterprise')) return;
    if (loadedSites.current) return;
    loadedSites.current = true;
    fetchSites().then(({ data, source }) => {
      setSites(data);
      setDataSource(source);
      setSelectedSiteId((previous) => previous ?? data[0]?.id ?? null);
    }).finally(() => setLoadingSites(false));
  }, [location.pathname]);

  return <DashboardContext.Provider value={{ sites, dataSource, selectedSiteId, setSelectedSiteId, activeYear, setActiveYear, loadingSites, recenterSignal, setRecenterSignal, onSignIn: () => setLoginOpen(true) }}><Routes>
    <Route path="/" element={<LandingPage onSignIn={() => setLoginOpen(true)} />} />
    <Route path="/executive" element={<DashboardPage />} />
    <Route path="/enterprise" element={<DashboardPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes><LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} /></DashboardContext.Provider>;
}

export default function App() { return <BrowserRouter><AppRoutes /></BrowserRouter>; }
