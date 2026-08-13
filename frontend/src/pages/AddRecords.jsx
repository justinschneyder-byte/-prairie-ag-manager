import { useRef, useState, useEffect } from "react";
import { api } from "../api.js";

const ACTION_LABELS = {
  field: "Field",
  machine: "Machine",
  rain: "Rainfall",
  frost: "Frost event",
  hail: "Hail event",
  crop: "Crop record",
  spray: "Spray record",
  input: "Input record",
  maint: "Maintenance record",
  none: null,
};

export default function AddRecords() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Tell me what happened, in your own words — e.g. \"sprayed the north field with roundup today, light wind\" or \"got 14mm of rain last night\".",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    setError("");
    try {
      const result = await api.chat(text);
      const label = ACTION_LABELS[result.action];
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: result.message,
          badge: label,
        },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((m) => [...m, { role: "assistant", content: "Something went wrong saving that — try again?" }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="card">
      <h2>Add Records</h2>
      <div className="chat-log" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.content}
            {m.badge && (
              <div style={{ marginTop: "0.35rem" }}>
                <span className="badge">Saved: {m.badge}</span>
              </div>
            )}
          </div>
        ))}
        {sending && <div className="chat-bubble assistant">Thinking…</div>}
      </div>
      {error && <p className="error-text">{error}</p>}
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type what happened…"
          disabled={sending}
        />
        <button className="btn" type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
