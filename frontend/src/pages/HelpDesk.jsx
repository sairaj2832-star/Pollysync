import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useToast } from "../context/ToastContext";

const FAQS = [
  {
    icon: "calculate",
    color: "primary",
    title: "How is PSI calculated?",
    desc: "Understand the algorithm behind our Pollination Success Index and historical weightings.",
  },
  {
    icon: "sensors",
    color: "secondary",
    title: "Integrating weather sensors",
    desc: "Step-by-step guide on connecting LoRaWAN and 4G environmental sensors.",
  },
  {
    icon: "api",
    color: "tertiary",
    title: "API Access & Keys",
    desc: "How to generate secret keys and use our REST API for custom farm management software.",
  },
  {
    icon: "group",
    color: "on-secondary-container",
    title: "User Management",
    desc: "Setting permissions for agronomists, farm workers, and seasonal analysts.",
  },
];

const ICON_COLORS = {
  primary: "bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white",
  secondary: "bg-secondary/10 text-secondary group-hover:bg-secondary group-hover:text-white",
  tertiary: "bg-tertiary/10 text-tertiary group-hover:bg-tertiary group-hover:text-white",
  "on-secondary-container":
    "bg-on-secondary-container/10 text-on-secondary-container group-hover:bg-on-secondary-container group-hover:text-white",
};

export default function HelpDesk() {
  const toast = useToast();
  const [search, setSearch] = useState("");
  const [sending, setSending] = useState(false);

  const [contact, setContact] = useState({
    name: "",
    category: "technical",
    subject: "",
    message: "",
  });

  useEffect(() => {
    function handleKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        document.getElementById("help-search")?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const filteredFAQs = FAQS.filter(
    (faq) =>
      faq.title.toLowerCase().includes(search.toLowerCase()) ||
      faq.desc.toLowerCase().includes(search.toLowerCase())
  );

  function updateContact(field, value) {
    setContact((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSending(true);
    // TODO: connect to backend
    await new Promise((r) => setTimeout(r, 1500));
    setSending(false);
    toast.success("Message sent successfully. We'll get back to you soon.");
    setContact({ name: "", category: "technical", subject: "", message: "" });
  }

  return (
    <div className="pb-2xl">
      {/* Hero Search */}
      <section className="relative py-3xl overflow-hidden flex flex-col items-center justify-center text-center">
        <div className="relative z-10 max-w-2xl w-full">
          <h2 className="text-display font-display text-on-surface mb-md">Help & Support</h2>
          <p className="text-body-lg text-on-surface-variant mb-xl">
            Knowledge hub and direct access to our technical experts.
          </p>
          <div className="relative group">
            <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline text-xl transition-colors group-focus-within:text-primary">
              search
            </span>
            <input
              id="help-search"
              className="w-full pl-3xl pr-xl py-lg bg-surface border border-outline-variant rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary text-body-md transition-all"
              placeholder="How can we help you today?"
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="absolute right-sm top-1/2 -translate-y-1/2 flex gap-xs pointer-events-none">
              <kbd className="px-sm py-xs bg-surface-container-high rounded text-label-sm border border-outline-variant">⌘</kbd>
              <kbd className="px-sm py-xs bg-surface-container-high rounded text-label-sm border border-outline-variant">K</kbd>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Bento Grid */}
      <section className="mb-2xl">
        <div className="flex items-center justify-between mb-lg">
          <h3 className="text-headline-sm font-headline-sm">Common Questions</h3>
          <a className="text-primary font-label-md flex items-center gap-xs hover:underline" href="#">
            View All Documentation{" "}
            <span className="material-symbols-outlined text-base">arrow_forward</span>
          </a>
        </div>
        {filteredFAQs.length === 0 ? (
          <div className="text-center py-xl text-on-surface-variant font-body-md">
            No results found for "{search}"
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
            {filteredFAQs.map((faq) => (
              <div
                key={faq.title}
                className="bg-surface border border-outline-variant p-lg rounded-xl hover:shadow-md transition-all group cursor-pointer"
              >
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center mb-md transition-colors ${ICON_COLORS[faq.color]}`}
                >
                  <span className="material-symbols-outlined">{faq.icon}</span>
                </div>
                <h4 className="text-body-md font-bold mb-sm">{faq.title}</h4>
                <p className="text-body-sm text-on-surface-variant">{faq.desc}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
