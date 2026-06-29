import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem("pollisync_token");
  if (token) {
    config.headers.Authorization = "Bearer " + token;
  }
  return config;
});

export async function getHealth() {
  const response = await api.get("/api/health");
  return response.data;
}

export default api;
