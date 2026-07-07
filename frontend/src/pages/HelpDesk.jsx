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

      {/* Contact Section */}
      <section>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-2xl">
          {/* Contact Form */}
          <div className="lg:col-span-7 bg-surface-container-low p-xl rounded-2xl border border-outline-variant">
            <h3 className="text-headline-md font-headline-md mb-xl">Send a Message</h3>
            <form onSubmit={handleSubmit} className="space-y-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
                <div className="space-y-sm">
                  <label className="text-label-md font-label-md text-on-surface">Full Name</label>
                  <input
                    className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                    placeholder="John Doe"
                    type="text"
                    value={contact.name}
                    onChange={(e) => updateContact("name", e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-sm">
                  <label className="text-label-md font-label-md text-on-surface">Category</label>
                  <select
                    className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                    value={contact.category}
                    onChange={(e) => updateContact("category", e.target.value)}
                  >
                    <option value="technical">Technical Support</option>
                    <option value="billing">Billing & Subscription</option>
                    <option value="general">General Inquiry</option>
                    <option value="data">Data Partnership</option>
                  </select>
                </div>
              </div>
              <div className="space-y-sm">
                <label className="text-label-md font-label-md text-on-surface">Subject</label>
                <input
                  className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                  placeholder="I need help with..."
                  type="text"
                  value={contact.subject}
                  onChange={(e) => updateContact("subject", e.target.value)}
                  required
                />
              </div>
              <div className="space-y-sm">
                <label className="text-label-md font-label-md text-on-surface">Message</label>
                <textarea
                  className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none"
                  placeholder="Describe your issue in detail..."
                  rows="5"
                  value={contact.message}
                  onChange={(e) => updateContact("message", e.target.value)}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={sending}
                className="bg-primary text-white px-xl py-md rounded-lg font-label-md hover:bg-on-primary-container transition-all flex items-center gap-sm group disabled:opacity-60"
              >
                {sending ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Sending...
                  </>
                ) : (
                  <>
                    Send Message
                    <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">send</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Right Column */}
          <div className="lg:col-span-5 space-y-lg">
            {/* Agronomist Card */}
            <div className="bg-primary-container text-on-primary-container p-xl rounded-2xl relative overflow-hidden group shadow-lg">
              <div className="relative z-10">
                <div className="flex items-center gap-md mb-md">
                  <div className="w-12 h-12 rounded-full border-2 border-white/30 overflow-hidden bg-white/20 flex items-center justify-center">
                    <span className="material-symbols-outlined text-2xl">person</span>
                  </div>
                  <div>
                    <h4 className="font-bold text-body-lg">Talk to an Agronomist</h4>
                    <p className="text-label-sm opacity-90 flex items-center gap-xs">
                      <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                      Available now for Live Chat
                    </p>
                  </div>
                </div>
                <p className="text-body-sm mb-lg">
                  Get specialized advice on bee activity and crop health from our in-house biological team.
                </p>
                <Link
                  to="/chat"
                  className="block w-full bg-white text-primary py-md rounded-xl font-bold hover:bg-surface-container-lowest transition-colors text-center flex items-center justify-center gap-md"
                >
                  <span className="material-symbols-outlined">chat</span>
                  Start Live Chat
                </Link>
              </div>
              <div className="absolute top-0 right-0 p-lg opacity-10 pointer-events-none group-hover:scale-110 transition-transform duration-700">
                <span className="material-symbols-outlined text-[120px]">psychiatry</span>
              </div>
            </div>

            {/* Contact Details */}
            <div className="bg-surface-container-high p-xl rounded-2xl border border-outline-variant space-y-xl">
              <div className="flex items-start gap-md">
                <div className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-primary border border-outline-variant">
                  <span className="material-symbols-outlined">mail</span>
                </div>
                <div>
                  <h5 className="text-label-md font-bold text-on-surface">Email Support</h5>
                  <p className="text-body-sm text-on-surface-variant">support@pollisync.com</p>
                  <p className="text-label-sm text-outline mt-xs">Avg. response: 2 hours</p>
                </div>
              </div>
              <div className="flex items-start gap-md">
                <div className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-tertiary border border-outline-variant">
                  <span className="material-symbols-outlined">emergency</span>
                </div>
                <div>
                  <h5 className="text-label-md font-bold text-on-surface">Emergency Hotline</h5>
                  <p className="text-body-sm font-bold text-tertiary">+1 (888) BEE-HELP</p>
                  <p className="text-label-sm text-outline mt-xs">Critical equipment failure only</p>
                </div>
              </div>
              <div className="flex items-start gap-md">
                <div className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-secondary border border-outline-variant">
                  <span className="material-symbols-outlined">location_on</span>
                </div>
                <div>
                  <h5 className="text-label-md font-bold text-on-surface">Headquarters</h5>
                  <p className="text-body-sm text-on-surface-variant">124 Innovation Way, Tech Valley</p>
                  <p className="text-label-sm text-outline mt-xs">San Jose, CA 95110</p>
                </div>
              </div>
            </div>

            {/* Resource Card */}
            <div className="p-lg bg-surface border border-outline-variant border-dashed rounded-2xl flex items-center justify-between group cursor-pointer hover:bg-surface-container-low transition-colors">
              <div className="flex items-center gap-md">
                <span className="material-symbols-outlined text-primary text-3xl">menu_book</span>
                <div>
                  <p className="text-label-md font-bold">Training Academy</p>
                  <p className="text-label-sm text-outline">Interactive video tutorials</p>
                </div>
              </div>
              <span className="material-symbols-outlined text-outline group-hover:text-primary transition-colors">open_in_new</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
