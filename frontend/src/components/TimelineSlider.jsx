export default function TimelineSlider({ activeYear, onChangeYear }) {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border-subtle bg-surface-elevated px-4 py-3 text-xs text-text-secondary sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-2">
        <span className="font-medium text-text-primary">
          Timeline Slider (2000 – Present)
        </span>
        <span className="rounded border border-border-subtle bg-surface-base px-2 py-0.5 font-mono text-[11px] text-accent-amber">
          {activeYear}
        </span>
      </div>

      <div className="flex flex-1 items-center gap-3 sm:max-w-md">
        <span className="font-mono text-[11px] text-text-muted">2000</span>
        <input
          type="range"
          min={2000}
          max={2026}
          value={activeYear}
          onChange={(e) => onChangeYear(Number(e.target.value))}
          className="h-1.5 w-full cursor-pointer accent-amber-500"
        />
        <span className="font-mono text-[11px] text-text-muted">2026</span>
      </div>
    </div>
  );
}