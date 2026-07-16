import { useState, useRef, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { useFarm } from "../context/FarmContext";

const INITIAL_MESSAGES = [
  {
    id: 1,
    role: "assistant",
    content: "Hello! I'm your PolliSync AI agronomist. Ask me anything about pollination, crop health, or weather conditions for your farm.",
    timestamp: new Date(Date.now() - 60000).toISOString(),
  },
];

const SUGGESTIONS = [
  "What are optimal pollination conditions?",
  "How is my crop health (NDVI)?",
  "Should I water my crops today?",
  "When is the next flowering window?",
];

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

function getDemoReply(question, farm) {
  const query = question.toLowerCase();
  const farmName = farm?.name || "your selected farm";
  if (query.includes("water") || query.includes("irrig")) return `For ${farmName}, keep the root zone evenly moist this week. Your latest field record shows healthy moisture after recent rain, so inspect before adding a full irrigation cycle.`;
  if (query.includes("ndvi") || query.includes("health")) return `Crop health is trending upward: the latest NDVI is 0.78, compared with 0.61 three weeks ago. Keep monitoring the lower-west edge, where canopy growth is slightly behind the field average.`;
  if (query.includes("flower") || query.includes("bloom")) return `The strongest flowering window is July 19–29 with 91% confidence. Place or confirm hives before the window begins and avoid spraying during active bee hours.`;
  if (query.includes("pollin") || query.includes("bee")) return `Pollination conditions are favorable today (PSI 82). Four bee species have been recorded near the field; calm mornings between 8–11 AM should have the best activity.`;
  return `Based on the latest data for ${farmName}, conditions are favorable for pollination. The most useful next step is to review the morning weather window and keep pesticide applications outside bee-foraging hours.`;
}

export default function ChatPage() {
  const { user } = useAuth();
  const { selectedFarm } = useFarm();
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [farmData, setFarmData] = useState(null);
  const bottomRef = useRef(null);
  const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (selectedFarm) {
          const f = selectedFarm;
          setFarmData({
            farmer_name: user?.full_name || "Farmer",
            location: f.location_name || f.location || "Unknown",
            crop_name: f.crop_type || f.crop || "Unknown",
            farm_size: f.area_acres?.toString() || "N/A",
            temp_current: "28",
            temp_forecast: "30",
            humidity: "65",
            rainfall_mm: "10",
            wind_speed: "12",
            season: "Kharif",
            ndvi_value: "0.72",
            ndvi_interpretation: "Healthy",
            ndvi_date: new Date().toISOString().split("T")[0],
            flowering_date: "2026-08-15",
            bee_arrival_date: "2026-08-20",
            mismatch_days: "5",
            risk_score: "40",
            risk_level: "MEDIUM",
            avg_flowering_date: "2026-08-12",
            avg_bee_arrival_date: "2026-08-18",
            trend: "Stable",
          });
    } else {
      setFarmData(null);
    }
  }, [user, selectedFarm]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || loading) return;
    const userMsg = {
      id: Date.now(),
      role: "user",
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      if (USE_MOCK) {
        await new Promise((resolve) => setTimeout(resolve, 650));
        setMessages((prev) => [...prev, { id: Date.now() + 1, role: "assistant", content: getDemoReply(text, selectedFarm), timestamp: new Date().toISOString() }]);
        return;
      }
      const conversation = [...messages, userMsg].map((m) => ({
        role: m.role === "assistant" ? "model" : "user",
        content: m.content,
      }));

      const payload = { messages: conversation };
      if (farmData) {
        payload.farm_data = farmData;
      }

      const res = await fetch(`${apiBase}/api/agent/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${window.localStorage.getItem("pollisync_token")}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      const aiMsg = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.reply || "I'm sorry, I couldn't generate a response.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: err.message === "Failed to fetch"
            ? "Could not reach the AI server. Make sure the backend is running (`py -3.12 -m uvicorn app.main:app --reload`)."
            : `Sorry, I encountered an error: ${err.message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [messages, loading, farmData, apiBase, selectedFarm]);

  function handleSubmit(e) {
    e.preventDefault();
    sendMessage(input);
  }

  function formatTime(ts) {
    return new Date(ts).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  }

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] lg:h-[calc(100vh-8rem)] max-w-[800px] mx-auto">
      <div className="mb-lg">
        <h1 className="font-headline-lg text-headline-lg text-on-surface">AI Assistant</h1>
        <p className="font-body-md text-body-md text-on-surface-variant">
          {farmData
            ? `Ask about ${farmData.crop_name} at ${farmData.location}`
            : "Ask questions about your farm and crops."}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto bg-surface border border-outline-variant rounded-xl p-lg space-y-lg mb-md">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl px-lg py-md ${
              msg.role === "user"
                ? "bg-primary text-on-primary"
                : "bg-surface-container-low border border-outline-variant/50 text-on-surface"
            }`}>
              {msg.role === "assistant" && (
                <div className="flex items-center gap-xs mb-xs">
                  <span className="material-symbols-outlined text-primary text-[16px]">smart_toy</span>
                  <span className="font-label-sm text-label-sm text-primary font-medium">AI Agronomist</span>
                </div>
              )}
              <p className="font-body-md text-body-md whitespace-pre-wrap">{msg.content}</p>
              <span className={`font-label-sm text-label-sm block mt-xs ${
                msg.role === "user" ? "text-on-primary/60 text-right" : "text-on-surface-variant"
              }`}>
                {formatTime(msg.timestamp)}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-surface-container-low border border-outline-variant/50 rounded-xl px-lg py-md">
              <div className="flex items-center gap-xs">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="font-body-sm text-body-sm text-on-surface-variant ml-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-sm mb-md">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="px-md py-xs bg-surface-container-high text-on-surface-variant font-body-sm text-body-sm rounded-full hover:bg-surface-container-highest transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-sm">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about pollination, weather, crops..."
          disabled={loading}
          className="flex-1 bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md hover:brightness-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-sm"
        >
          <span className="material-symbols-outlined text-[18px]">send</span>
          Send
        </button>
      </form>
    </div>
  );
}
