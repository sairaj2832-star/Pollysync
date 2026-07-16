import axios from "axios";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem("pollisync_token");
  if (token) {
    config.headers.Authorization = "Bearer " + token;
  }
  return config;
});

function real(apiFunc) {
  return (...args) => apiFunc(...args);
}

export function getApiErrorMessage(error, fallback = "Request failed") {
  const firebaseCode = error?.code;

  if (typeof firebaseCode === "string" && firebaseCode.startsWith("auth/")) {
    const firebaseMessages = {
      "auth/configuration-not-found":
        "Firebase Authentication is missing provider setup. In Firebase Console, open Authentication > Sign-in method and enable the provider you are trying to use.",
      "auth/operation-not-allowed":
        "This Firebase sign-in method is disabled. Enable it in Firebase Console > Authentication > Sign-in method.",
      "auth/unauthorized-domain":
        "This domain is not authorized for Firebase sign-in. Add localhost to Firebase Console > Authentication > Settings > Authorized domains.",
      "auth/invalid-credential":
        "The Firebase sign-in credentials were rejected. Check that the provider is enabled and try again.",
      "auth/invalid-email":
        "Please enter a valid email address.",
      "auth/user-not-found":
        "No account was found for that email.",
      "auth/wrong-password":
        "The password is incorrect.",
      "auth/email-already-in-use":
        "This email is already registered. Please sign in instead.",
      "auth/popup-closed-by-user":
        "The sign-in popup was closed before authentication finished.",
      "auth/popup-blocked":
        "The browser blocked the sign-in popup. Allow popups for this site and try again.",
      "auth/network-request-failed":
        "Firebase could not reach the network. Check your connection and try again.",
      "auth/too-many-requests":
        "Too many login attempts were made. Please wait a bit and try again.",
      "auth/weak-password":
        "Choose a stronger password with at least 6 characters.",
    };

    return firebaseMessages[firebaseCode] || error?.message || fallback;
  }

  if (error?.code === "ECONNABORTED" || /timeout/i.test(error?.message || "")) {
    return "The request took too long to complete. Please try again in a moment.";
  }

  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          const path = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "";
          return path ? `${path}: ${item.msg}` : item.msg;
        }
        return null;
      })
      .filter(Boolean)
      .join(". ");
  }

  return error?.message || fallback;
}

export async function getHealth() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetHealth();
  }
  const { data } = await api.get("/api/health");
  return data;
}

export async function login(email, password) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockLogin(email, password);
  }
  const { data } = await api.post("/api/auth/login", { email, password });
  return data;
}

export async function register(email, password, full_name) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockRegister(email, password, full_name);
  }
  const { data } = await api.post("/api/auth/register", { email, password, full_name });
  return data;
}

export async function getMe() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetMe();
  }
  const { data } = await api.get("/api/auth/me");
  return data;
}

export async function getFarms() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetFarms();
  }
  const { data } = await api.get("/api/farms");
  return data;
}

export async function createFarm(payload) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockCreateFarm(payload);
  }
  const { data } = await api.post("/api/farms", payload);
  return data;
}

export async function deleteFarm(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockDeleteFarm(farm_id);
  }
  const { data } = await api.delete(`/api/farms/${farm_id}`);
  return data;
}

export async function getWeatherCurrent(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetWeatherCurrent(farm_id);
  }
  const { data } = await api.get("/api/weather/current", { params: { farm_id } });
  return data;
}

export async function getWeatherForecast(farm_id, days = 7) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetWeatherForecast(farm_id, days);
  }
  const { data } = await api.get("/api/weather/forecast", { params: { farm_id, days } });
  return data;
}

export async function createPrediction(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockCreatePrediction(farm_id);
  }
  const { data } = await api.post("/api/predictions", { farm_id }, { timeout: 60000 });
  return data;
}

export async function firebaseAuth(idToken) {
  const { data } = await api.post("/api/auth/firebase", { id_token: idToken });
  return data;
}

export async function logout(refreshToken) {
  if (!refreshToken) {
    return null;
  }
  const { data } = await api.post("/api/auth/logout", { refresh_token: refreshToken });
  return data;
}

export async function getPredictions(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetPredictions(farm_id);
  }
  const { data } = await api.get("/api/predictions", { params: { farm_id } });
  return data;
}

export async function getLatestPrediction(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetLatestPrediction(farm_id);
  }
  const { data } = await api.get("/api/predictions/latest", { params: { farm_id } });
  return data;
}

export async function getDashboardSummary(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetDashboardSummary(farm_id);
  }
  const { data } = await api.get("/api/predictions/dashboard/summary", { params: { farm_id } });
  return data;
}

export async function generateRecommendation(farm_id, prediction_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGenerateRecommendation(farm_id, prediction_id);
  }
  const { data } = await api.post(
    "/api/recommendations/generate",
    { farm_id, prediction_id },
    { timeout: 60000 }
  );
  return data;
}

export async function getBeeOccurrences(farm_id, radius = 10) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetBeeOccurrences(farm_id, radius);
  }
  const { data } = await api.get("/api/maps/bees", { params: { farm_id, radius } });
  return data;
}

export async function getDistricts() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetDistricts();
  }
  const { data } = await api.get("/api/districts");
  return data;
}

export async function getDistrict(slug) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetDistrict(slug);
  }
  const { data } = await api.get(`/api/districts/${slug}`);
  return data;
}

export async function getNotifications() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetNotifications();
  }
  const { data } = await api.get("/api/notifications");
  return data;
}

export async function markNotificationRead(notif_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockMarkNotificationRead(notif_id);
  }
  const { data } = await api.patch(`/api/notifications/${notif_id}/read`);
  return data;
}

export async function updateProfile(payload) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockUpdateProfile(payload);
  }
  const { data } = await api.patch("/api/auth/me", payload);
  return data;
}

export async function updateFarm(farm_id, payload) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockUpdateFarm(farm_id, payload);
  }
  const { data } = await api.patch(`/api/farms/${farm_id}`, payload);
  return data;
}

export async function getNotificationPreferences() {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetNotificationPreferences();
  }
  const { data } = await api.get("/api/notifications/preferences");
  return data;
}

export async function updateNotificationPreferences(payload) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockUpdateNotificationPreferences(payload);
  }
  const { data } = await api.patch("/api/notifications/preferences", payload);
  return data;
}

export async function getTeamMembers(farm_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockGetTeamMembers(farm_id);
  }
  const { data } = await api.get(`/api/farms/${farm_id}/team`);
  return data;
}

export async function inviteTeamMember(farm_id, payload) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockInviteTeamMember(farm_id, payload);
  }
  const { data } = await api.post(`/api/farms/${farm_id}/team`, payload);
  return data;
}

export async function removeTeamMember(farm_id, member_id) {
  if (USE_MOCK) {
    const m = await import("./mockApi");
    return m.mockRemoveTeamMember(farm_id, member_id);
  }
  await api.delete(`/api/farms/${farm_id}/team/${member_id}`);
}

export default api;
