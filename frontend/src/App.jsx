import { useEffect, useState } from "react";
import { fetchSites } from "./api/endpoints";
import MapPanel from "./components/MapPanel";

function App() {
  const [viewMode, setViewMode] = useState("executive");
  const [sites, setSites] = useState([]);
  const [dataSource, setDataSource] = useState("mock");
  const [selectedSiteId, setSelectedSiteId] = useState(null);
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
    <div className="flex min-h-screen flex-col bg-surface-base text-text-primary">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border-subtle bg-surface-elevated px-6 py-3">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-accent-amber">
              GeoGround
            </h1>
            <p className="text-xs text-text-muted">
              Commercial Real Estate &amp; Site Intelligence
            </p>
          </div>

          <span className="rounded-md border border-border-subtle bg-surface-base px-2 py-0.5 text-[11px] text-text-secondary">
            Source: {loadingSites ? "loading..." : dataSource}
          </span>
        </div>

        <div className="flex rounded-lg border border-border-subtle bg-surface-base p-1 text-xs">
          <button
            type="button"
            onClick={() => setViewMode("executive")}
            className={`rounded-md px-3 py-1.5 font-medium transition ${
              viewMode === "executive"
                ? "bg-accent-amber text-slate-950"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Executive
          </button>
          <button
            type="button"
            onClick={() => setViewMode("enterprise")}
            className={`rounded-md px-3 py-1.5 font-medium transition ${
              viewMode === "enterprise"
                ? "bg-accent-amber text-slate-950"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Enterprise
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12">
        <section className="flex flex-col justify-between rounded-xl border border-border-subtle bg-surface-card p-4 lg:col-span-8">
          {viewMode === "executive" ? (
            <MapPanel
              sites={sites}
              selectedSiteId={selectedSiteId}
              onSelectSite={setSelectedSiteId}
              recenterSignal={recenterSignal}
              onRecenter={handleRecenter}
            />
          ) : (
            <div className="flex min-h-[380px] flex-col items-center justify-center rounded-lg border border-dashed border-border-subtle p-4 text-center text-sm text-text-muted">
              Enterprise Analytics: Correlation Charts, Coordinate Table &amp; CSV Export
            </div>
          )}

          <div className="mt-4 rounded-lg border border-border-subtle bg-surface-elevated px-4 py-3 text-xs text-text-secondary">
            Timeline Slider (2000 – Present)
          </div>
        </section>

        <aside className="flex flex-col gap-4 lg:col-span-4">
          <div className="rounded-xl border border-border-subtle bg-surface-card p-4">
            <h2 className="text-sm font-semibold text-text-primary">
              Site Details &amp; Alerts
            </h2>

            {loadingSites ? (
              <p className="mt-2 text-xs text-text-muted">Loading sites...</p>
            ) : selectedSite ? (
              <div className="mt-2 space-y-2 text-xs">
                <p className="font-medium text-text-primary">{selectedSite.name}</p>
                <p className="text-text-muted">
                  Region: {selectedSite.region || "—"} • Status: {selectedSite.status || "—"}
                </p>
                {Array.isArray(selectedSite.alerts) && selectedSite.alerts.length > 0 && (
                  <div className="space-y-1 pt-1">
                    {selectedSite.alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className="rounded-md border border-border-subtle bg-surface-elevated p-2 text-text-secondary"
                      >
                        <p className="font-medium text-amber-400">{alert.title}</p>
                        <p className="mt-0.5 text-[11px] text-text-muted">
                          {alert.confirmed_by_radar ? "Confirmed by Radar" : "Unconfirmed"} •{" "}
                          {alert.duration_months} months active
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="mt-1 text-xs text-text-muted">
                Select a site polygon on the map to inspect alerts and telemetry.
              </p>
            )}
          </div>

          <div className="flex-1 rounded-xl border border-border-subtle bg-surface-card p-4">
            <h2 className="text-sm font-semibold text-text-primary">
              AI Summary &amp; Contextual Chat
            </h2>
            <p className="mt-1 text-xs text-text-muted">
              Connected to backend telemetry summary &amp; chat endpoints.
            </p>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;