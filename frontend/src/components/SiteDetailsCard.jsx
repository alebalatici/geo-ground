export default function SiteDetailsCard({ site, loading }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-card p-4">
      <h2 className="text-sm font-semibold text-text-primary">
        Site Details &amp; Alerts
      </h2>

      {loading ? (
        <p className="mt-2 text-xs text-text-muted">Loading sites...</p>
      ) : site ? (
        <div className="mt-2 space-y-2 text-xs">
          <p className="font-medium text-text-primary">{site.name}</p>
          <p className="text-text-muted">
            Region: {site.city || site.region || "—"} • Status:{" "}
            {site.latest_alert?.signal_type || site.status || "—"}
          </p>
          {Array.isArray(site.alerts) && site.alerts.length > 0 && (
            <div className="space-y-1 pt-1">
              {site.alerts.map((alert) => (
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
  );
}