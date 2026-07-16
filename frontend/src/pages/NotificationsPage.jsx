import { useEffect, useState } from "react";
import { getNotifications, markNotificationRead } from "../lib/api";
import { useToast } from "../context/ToastContext";
import Card from "../components/Card";
import { EmptyState, DashboardSkeleton } from "../components/LoadingSkeleton";

const NOTIFICATION_ICONS = {
  weather: "cloud",
  bloom: "local_florist",
  pollinator: "pets",
  alert: "warning",
  info: "info",
};

const NOTIFICATION_COLORS = {
  weather: "bg-primary-container/15 text-primary border-primary/20",
  bloom: "bg-primary-container/15 text-primary border-primary/20",
  pollinator: "bg-secondary-container/20 text-secondary border-secondary/20",
  alert: "bg-tertiary-container/20 text-tertiary border-tertiary/20",
  info: "bg-surface-container-high text-on-surface-variant border-outline-variant",
};

export default function NotificationsPage() {
  const toast = useToast();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [error, setError] = useState("");

  useEffect(() => {
    loadNotifications();
  }, []);

  async function loadNotifications() {
    try {
      setLoading(true);
      const data = await getNotifications();
      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      // If endpoint doesn't exist, show demo data
      setNotifications(getDemoNotifications());
    } finally {
      setLoading(false);
    }
  }

  function getDemoNotifications() {
    return [
      {
        id: 1,
        type: "weather",
        title: "Heavy rainfall expected",
        message: "Your Nashik farm may experience 45-50mm rainfall in next 48 hours",
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        read: false,
      },
      {
        id: 2,
        type: "bloom",
        title: "Blooming window approaching",
        message: "Mustard crop on South Plot expected to bloom in 5-7 days",
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        read: false,
      },
      {
        id: 3,
        type: "pollinator",
        title: "Bee activity increasing",
        message: "7 bee species observed in Maharashtra region this week",
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        read: true,
      },
      {
        id: 4,
        type: "alert",
        title: "Temperature alert",
        message: "Unseasonably high temps (38°C) may stress pollination on Sun Belt farm",
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        read: true,
      },
    ];
  }

  async function handleMarkAsRead(notifId) {
    try {
      await markNotificationRead(notifId);
      setNotifications(
        notifications.map((n) => (n.id === notifId ? { ...n, read: true } : n))
      );
    } catch (err) {
      // Silently fail for mock
      setNotifications(
        notifications.map((n) => (n.id === notifId ? { ...n, read: true } : n))
      );
    }
  }

  async function handleMarkAllAsRead() {
    try {
      // Try to mark all as read
      await Promise.all(
        notifications.filter((n) => !n.read).map((n) => markNotificationRead(n.id))
      );
    } catch (err) {
      // Silently fail
    }
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
    toast.success("All notifications marked as read");
  }

  const filtered =
    filter === "all"
      ? notifications
      : filter === "unread"
        ? notifications.filter((n) => !n.read)
        : notifications.filter((n) => n.type === filter);

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="space-y-lg">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-display text-display text-on-surface">Notifications</h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-xs">
            Stay updated on weather, blooms, and pollinator activity
          </p>
        </div>
        {notifications.some((n) => !n.read) && (
          <button
            onClick={handleMarkAllAsRead}
            className="px-lg py-sm rounded-lg bg-surface-container text-on-surface font-label-md text-label-md font-bold hover:bg-surface-container/80 transition"
          >
            Mark all as read
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-md overflow-x-auto pb-md">
        {[
          { label: "All", value: "all" },
          { label: "Unread", value: "unread", badge: notifications.filter((n) => !n.read).length },
          { label: "Weather", value: "weather" },
          { label: "Blooming", value: "bloom" },
          { label: "Pollinators", value: "pollinator" },
          { label: "Alerts", value: "alert" },
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value)}
            className={`px-md py-sm rounded-lg font-label-md text-label-md font-bold whitespace-nowrap transition flex items-center gap-xs ${
              filter === tab.value
                ? "bg-primary text-on-primary"
                : "bg-surface-container text-on-surface hover:bg-surface-container/80"
            }`}
          >
            {tab.label}
            {tab.badge ? (
              <span className="ml-xs px-xs py-0 bg-white/20 rounded-full text-xs">
                {tab.badge}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      {filtered.length === 0 ? (
        <EmptyState
          icon="notifications_off"
          title={filter === "all" ? "No notifications yet" : "No notifications in this category"}
          description={
            filter === "all"
              ? "You're all caught up! Check back later."
              : "Switch to another filter to see more."
          }
        />
      ) : (
        <div className="space-y-md">
          {filtered.map((notif) => (
            <Card
              key={notif.id}
              className={`cursor-pointer transition ${notif.read ? "" : "border-primary border-l-4"}`}
            >
              <div className="flex gap-md">
                {/* Icon */}
                <div
                  className={`${NOTIFICATION_COLORS[notif.type] || NOTIFICATION_COLORS.info} p-md rounded-lg flex-shrink-0 w-fit`}
                >
                  <span className="material-symbols-outlined">
                    {NOTIFICATION_ICONS[notif.type] || NOTIFICATION_ICONS.info}
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start gap-md mb-xs">
                    <h3 className="font-headline-sm text-headline-sm text-on-surface">
                      {notif.title}
                    </h3>
                    <span className="text-label-xs text-on-surface-variant whitespace-nowrap flex-shrink-0">
                      {formatTime(new Date(notif.created_at))}
                    </span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mb-md">
                    {notif.message}
                  </p>

                  {/* Action Button */}
                  {!notif.read ? (
                    <button
                      onClick={() => handleMarkAsRead(notif.id)}
                      className="px-md py-xs rounded-lg bg-primary/10 text-primary font-label-sm text-label-sm font-bold hover:bg-primary/20 transition"
                    >
                      Mark as read
                    </button>
                  ) : (
                    <span className="font-label-xs text-on-surface-variant">✓ Read</span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function formatTime(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}
