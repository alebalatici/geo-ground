import { useEffect, useState } from 'react';
import { fetchExecutiveSummary } from "../../api/intelligenceApi.js";

export default function ExecutiveBriefCard({ siteId }) {
    // retains the text/object from the AI summary
    const [brief, setBrief] = useState(null);
    // when the call to the API is done, this will be set to true --> Generating executive summary
    const [loading, setLoading] = useState(true);
    // retains the error message if it does not find the site
    const [error, setError] = useState(null);

    // executes automatically when the siteId changes
    useEffect(() => {
        // if no site id is selected, return - we don't send any request to the backend
        if (!siteId) return;

        // flag for assurance: prevents the component from rendering after the unmounting
        // before the API call is done
        let isMounted = true;
        setLoading(true);
        setError(null);

        // fetch the AI summary from the backend
        fetchExecutiveSummary(siteId)
            .then((data) => {
                // if the component is still mounted, update the state
                if (isMounted) {
                    setBrief(data);
                    setLoading(false);
                }
            })
            .catch((err) => {
                if (isMounted) {
                    setError(err.message);
                }
            })
            .finally(() => {
                if (isMounted) {
                    setLoading(false);
                }
            });

        // cleanup function: when the component is unmounted, set the flag to false
        return () => {
            isMounted = false;
        };
    }, [siteId]);

    // if no site is selected, show a message
    if (!siteId) {
        return (
            <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 text-sm text-slate-400">
                Select a monitored parcel on the map to generate an institutional EO intelligence brief.
            </div>
        );
    }

    // check if the AI summary is available
    const isAmber = brief?.severity === 'AMBER';

    // if the AI summary is not available, show a message
    return (
    <section className="rounded-lg border border-slate-800 bg-slate-900 p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2.5">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              isAmber ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
          />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            AI Executive Intelligence Brief
          </h3>
        </div>

        {brief && (
          <div className="flex items-center gap-2">
            <span
              className={`rounded border px-2 py-0.5 font-mono text-[11px] font-medium ${
                isAmber
                  ? 'border-amber-500/40 bg-amber-500/10 text-amber-300'
                  : 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
              }`}
            >
              {brief.signal_type}
            </span>
            <span className="font-mono text-[11px] text-slate-500">
              {brief.provider_used}
            </span>
          </div>
        )}
      </div>
        {loading && (
        <div className="space-y-2.5 py-2">
          <div className="h-3.5 w-full animate-pulse rounded bg-slate-800" />
          <div className="h-3.5 w-5/6 animate-pulse rounded bg-slate-800" />
          <div className="h-3.5 w-4/6 animate-pulse rounded bg-slate-800" />
        </div>
      )}

      {error && (
        <div className="rounded border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-300">
          Failed to synthesize executive summary: {error}
        </div>
      )}

      {!loading && !error && brief && (
        <>
          <div className="space-y-3 text-sm leading-relaxed text-slate-300">
            {brief.summary.split('\n\n').map((paragraph, idx) => (
              <p key={idx}>{paragraph}</p>
            ))}
          </div>

          {brief.key_signals?.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-800/80 pt-3">
              {brief.key_signals.map((badge, idx) => (
                <span
                  key={idx}
                  className="rounded border border-slate-700/80 bg-slate-800/70 px-2.5 py-1 font-mono text-xs text-sky-300"
                >
                  {badge}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}