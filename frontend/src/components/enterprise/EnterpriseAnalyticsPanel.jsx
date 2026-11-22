export default function EnterpriseAnalyticsPanel({ site, activeYear }) {
  return (
    <div className="flex min-h-[380px] flex-1 flex-col items-center justify-center rounded-lg border border-dashed border-border-subtle p-4 text-center text-sm text-text-muted">
      <p className="font-medium text-text-primary">
        Enterprise Analytics {site ? `— ${site.name}` : ""}
      </p>
      <p className="mt-1 text-xs">
        Correlation Charts, Coordinate Table &amp; CSV Export (Focus year: {activeYear})
      </p>
    </div>
  );
}