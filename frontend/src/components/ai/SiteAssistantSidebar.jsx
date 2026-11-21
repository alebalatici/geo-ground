import { useEffect, useRef, useState } from "react";
import { sendSiteChatMessage } from "../../api/intelligenceApi.js";

const QUICK_PROMPTS = [
  "Summarize physical ground changes on this parcel.",
  "How do optical NDVI and SAR radar signals correlate here?",
  "Compare current activity against the 2000–2015 baseline.",
];

export default function SiteAssistantSidebar({ activeSite, activeYear = null }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!activeSite) {
      setMessages([]);
      return;
    }
    const location = activeSite.city || activeSite.region || "Romania";
    setMessages([
      {
        role: "assistant",
        content: `Connected to ${activeSite.name} (${location}). How can I help you?`,
        metrics: null,
      },
    ]);
  }, [activeSite?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  async function handleSend(textToSend) {
    const trimmed = textToSend.trim();
    if (!trimmed || !activeSite || isSending) return;

    const userMessage = { role: "user", content: trimmed };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsSending(true);

    const apiHistory = updatedMessages
      .slice(1, -1)
      .map(({ role, content }) => ({ role, content }));

    try {
      const response = await sendSiteChatMessage(activeSite.id, {
        message: trimmed,
        activeYear,
        history: apiHistory,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.reply,
          metrics: response.referenced_metrics,
          provider: response.provider_used,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Telemetry query error: ${error.message}. Make sure the FastAPI backend is running on port 8000.`,
          isError: true,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    handleSend(input);
  }

  return (
    <aside className="flex h-full w-full flex-col border-l border-slate-800 bg-slate-900">
      {/* Header ancorat */}
      <div className="border-b border-slate-800 bg-slate-950/60 px-4 py-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="h-4 w-4 text-amber-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.8}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
              />
            </svg>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              GeoGround Site Analyst
            </h2>
          </div>

          {activeYear && (
            <span className="rounded border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 font-mono text-[11px] text-sky-300">
              Focus: {activeYear}
            </span>
          )}
        </div>

        <p className="mt-1 truncate text-xs text-slate-400">
          {activeSite
            ? `Active Context: ${activeSite.name}`
            : "No parcel selected"}
        </p>
      </div>

      {/* Zona de mesaje */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {!activeSite ? (
          <div className="flex h-full items-center justify-center text-center text-xs text-slate-500">
            Select a parcel from the map or portfolio list to activate contextual telemetry Q&amp;A.
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${
                msg.role === "user" ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`max-w-[90%] rounded-lg px-3.5 py-2.5 text-xs leading-relaxed ${
                  msg.role === "user"
                    ? "border border-amber-500/30 bg-amber-500/15 text-slate-100"
                    : msg.isError
                    ? "border border-red-500/30 bg-red-950/40 text-red-300"
                    : "border border-slate-800 bg-slate-800/70 text-slate-200"
                }`}
              >
                <p className="whitespace-pre-line">{msg.content}</p>

                {msg.metrics && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5 border-t border-slate-700/70 pt-2">
                    {msg.metrics.ndvi_delta != null && (
                      <span className="rounded bg-slate-900 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
                        NDVI {Number(msg.metrics.ndvi_delta) >= 0 ? "+" : ""}
                        {Number(msg.metrics.ndvi_delta).toFixed(2)}
                      </span>
                    )}
                    {msg.metrics.sar_vv_delta_db != null && (
                      <span className="rounded bg-slate-900 px-1.5 py-0.5 font-mono text-[10px] text-sky-300">
                        VV {Number(msg.metrics.sar_vv_delta_db) >= 0 ? "+" : ""}
                        {Number(msg.metrics.sar_vv_delta_db).toFixed(2)} dB
                      </span>
                    )}
                    {msg.metrics.confidence_score != null && (
                      <span className="rounded bg-slate-900 px-1.5 py-0.5 font-mono text-[10px] text-amber-300">
                        Conf {(Number(msg.metrics.confidence_score) * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isSending && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="h-2 w-2 animate-ping rounded-full bg-amber-400" />
            Synthesizing satellite telemetry...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Întrebări rapide */}
      {activeSite && messages.length <= 2 && (
        <div className="border-t border-slate-800/80 bg-slate-950/40 px-4 py-2.5">
          <p className="mb-1.5 text-[10px] font-medium uppercase tracking-wider text-slate-500">
            Suggested Queries
          </p>
          <div className="flex flex-col gap-1.5">
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                disabled={isSending}
                onClick={() => handleSend(prompt)}
                className="rounded border border-slate-800 bg-slate-900 px-2.5 py-1.5 text-left text-[11px] text-slate-300 transition hover:border-amber-500/40 hover:text-amber-200 disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input formular */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-slate-800 bg-slate-950/70 p-3"
      >
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!activeSite || isSending}
            placeholder={
              activeSite
                ? "Ask about NDVI, SAR radar, or history..."
                : "Select a site first..."
            }
            className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-amber-500/60 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!activeSite || !input.trim() || isSending}
            className="rounded border border-amber-500/50 bg-amber-500/20 px-3 py-2 text-xs font-medium text-amber-200 transition hover:bg-amber-500/30 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Ask
          </button>
        </div>
      </form>
    </aside>
  );
}