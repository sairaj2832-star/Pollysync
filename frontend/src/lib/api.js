import axios from "axios";

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

export async function getHealth() {
  const { data } = await api.get("/api/health");
  return data;
}

export async function login(email, password) {
  const { data } = await api.post("/api/auth/login", { email, password });
  return data;
}

export async function register(email, password, full_name) {
  const { data } = await api.post("/api/auth/register", { email, password, full_name });
  return data;
}

export async function getMe() {
  const { data } = await api.get("/api/auth/me");
  return data;
}

export async function getFarms() {
  const { data } = await api.get("/api/farms");
  return data;
}

export async function createFarm(payload) {
  const { data } = await api.post("/api/farms", payload);
  return data;
}

export async function getWeatherCurrent(farm_id) {
  const { data } = await api.get("/api/weather/current", { params: { farm_id } });
  return data;
}

export async function getWeatherForecast(farm_id, days = 7) {
  const { data } = await api.get("/api/weather/forecast", { params: { farm_id, days } });
  return data;
}

export async function createPrediction(farm_id) {
  const { data } = await api.post("/api/predictions", { farm_id });
  return data;
}

export async function getPredictions(farm_id) {
  const { data } = await api.get("/api/predictions", { params: { farm_id } });
  return data;
}

export async function getLatestPrediction(farm_id) {
  const { data } = await api.get("/api/predictions/latest", { params: { farm_id } });
  return data;
}

export async function getDashboardSummary(farm_id) {
  const { data } = await api.get("/api/dashboard/summary", { params: { farm_id } });
  return data;
}

export async function generateRecommendation(farm_id, prediction_id) {
  const { data } = await api.post("/api/recommendations/generate", { farm_id, prediction_id });
  return data;
}

export async function getBeeOccurrences(farm_id, radius = 10) {
  const { data } = await api.get("/api/maps/bees", { params: { farm_id, radius } });
  return data;
}

export default api;
