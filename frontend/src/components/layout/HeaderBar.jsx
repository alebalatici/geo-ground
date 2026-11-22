export default function HeaderBar({
  viewMode,
  onChangeViewMode,
  dataSource,
  loadingSites,
}) {
  return (
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
          onClick={() => onChangeViewMode("executive")}
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
          onClick={() => onChangeViewMode("enterprise")}
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
  );
}