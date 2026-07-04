import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { getMe } from "../lib/api";

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

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text) {
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
      await getMe();

      await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200));

      const responses = [
        "Based on current conditions, pollination suitability is high. Temperature (28C) and humidity (65%) are within optimal ranges for most crops. I recommend maintaining current irrigation schedules.",
        "Your NDVI index of 0.72 indicates healthy crop growth. The vegetation is well-established. Continue monitoring for any signs of stress, especially during the flowering window.",
        "Soil moisture is at a good level (65%). With current humidity at 72%, additional watering is not immediately necessary. Light irrigation in early morning would be beneficial if temperatures rise above 32C.",
        "The predicted flowering window is July 18-25. Current weather models show favorable conditions. I recommend preparing hive placements and ensuring adequate pollinator activity during this period.",
        "Wind speeds are moderate at 12 km/h. This is acceptable for most crops but may slightly reduce bee activity. Consider positioning hives in sheltered areas if wind increases.",
        "Risk assessment shows low concern. However, monitor for sudden weather changes. The 7-day forecast indicates stable conditions with intermittent rainfall, which is beneficial for crop health.",
      ];

      const aiMsg = {
        id: Date.now() + 1,
        role: "assistant",
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: "Sorry, I encountered an error processing your request. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    sendMessage(input);
  }

  function formatTime(ts) {
    return new Date(ts).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-[800px] mx-auto">
      <div className="mb-lg">
        <h1 className="font-headline-lg text-headline-lg text-on-surface">AI Assistant</h1>
        <p className="font-body-md text-body-md text-on-surface-variant">Ask questions about your farm and crops.</p>
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
          className="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md hover:bg-[#005a3c] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-sm"
        >
          <span className="material-symbols-outlined text-[18px]">send</span>
          Send
        </button>
      </form>
    </div>
  );
}
