import { useEffect, useState } from "react";
import { fetchSites } from "./api/endpoints";
import ExecutiveBriefCard from "./components/ai/ExecutiveBriefCard";
import SiteAssistantSidebar from "./components/ai/SiteAssistantSidebar";
import EnterpriseAnalyticsPanel from "./components/enterprise/EnterpriseAnalyticsPanel";
import MapPanel from "./components/MapPanel";
import SiteDetailsCard from "./components/SiteDetailsCard";
import TimelineSlider from "./components/TimelineSlider";
import TopNavbar from "./features/header/TopNavbar.jsx";
import HeroSection from "./features/hero/HeroSection.jsx";

function App() {
  const [viewMode, setViewMode] = useState("executive");
  const [sites, setSites] = useState([]);
  const [dataSource, setDataSource] = useState("mock");
  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [activeYear, setActiveYear] = useState(2026);
  const [loadingSites, setLoadingSites] = useState(true);
  const [recenterSignal, setRecenterSignal] = useState(0);

  useEffect(() => {
    let active = true;

    setLoadingSites(true);
    fetchSites()
      .then(({ data, source }) => {
        if (!active) return;
        setSites(data);
        setDataSource(source);
        if (data.length > 0) {
          setSelectedSiteId((prev) => prev ?? data[0].id);
        }
      })
      .finally(() => {
        if (active) setLoadingSites(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const selectedSite = sites.find((site) => site.id === selectedSiteId) || null;

  const handleRecenter = () => {
    setRecenterSignal((prev) => prev + 1);
  };

  return (
    <div className="app-shell">
      <TopNavbar
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        dataSource={dataSource}
        isLoading={loadingSites}
      />

      <HeroSection />

      <main
        id="platform"
        className="platform-workspace grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12"
      >
        <section className="flex flex-col justify-between gap-4 rounded-xl border border-border-subtle bg-surface-card p-4 lg:col-span-8">
          {viewMode === "executive" ? (
            <>
              <MapPanel
                sites={sites}
                selectedSiteId={selectedSiteId}
                onSelectSite={setSelectedSiteId}
                recenterSignal={recenterSignal}
                onRecenter={handleRecenter}
              />
              <ExecutiveBriefCard siteId={selectedSite?.id} />
            </>
          ) : (
            <EnterpriseAnalyticsPanel
              site={selectedSite}
              activeYear={activeYear}
            />
          )}

          <TimelineSlider
            activeYear={activeYear}
            onChangeYear={setActiveYear}
          />
        </section>

        <aside className="flex flex-col gap-4 lg:col-span-4">
          <SiteDetailsCard
            site={selectedSite}
            loading={loadingSites}
          />

          <div className="flex min-h-[420px] flex-1 overflow-hidden rounded-xl border border-border-subtle">
            <SiteAssistantSidebar
              activeSite={selectedSite}
              activeYear={activeYear}
            />
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;