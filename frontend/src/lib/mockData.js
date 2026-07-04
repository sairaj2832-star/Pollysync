export const SESSION = {
  access_token: "mock_access_token_pollisync_" + Date.now(),
  refresh_token: "mock_refresh_token_" + Date.now(),
  expires_in: 1800,
  user: { id: 1, email: "farmer@example.com", full_name: "Demo Farmer", created_at: "2026-01-01T00:00:00Z" },
};

export const MOCK_FARM = {
  id: 1,
  name: "North Field",
  crop_type: "Mustard",
  location_lat: 20.011,
  location_lng: 73.79,
  created_at: "2026-06-01T00:00:00Z",
};

export const MOCK_PREDICTION = {
  id: 42,
  farm_id: 1,
  flowering_start: "2026-07-18",
  flowering_end: "2026-07-25",
  flowering_confidence: 0.87,
  psi_score: 78,
  risk_level: "Low",
  weather_summary: { temperature: 28.5, humidity: 62, rainfall: 1.2, wind_speed: 12 },
  pollen_summary: { tree: 3, grass: 2, weed: 1 },
  ndvi_value: 0.72,
  bee_species: ["Apis cerana", "Apis dorsata", "Apis florea"],
  recommendation:
    "## Assessment for Mustard\n\nCurrent conditions are favourable for pollination. " +
    "The temperature of 28°C and humidity at 62% are within optimal ranges.\n\n" +
    "**Recommended Actions:**\n- Ensure adequate irrigation during flowering window\n" +
    "- Monitor for pest activity, especially aphids\n- Consider introducing one additional hive per acre\n\n" +
    "Conditions are favourable. Maintain regular crop management practices.\n\n" +
    "**Confidence:** Moderate — based on seasonal models and local weather data.",
  created_at: "2026-06-30T10:30:00Z",
  model_source: "general_v1",
  data_confidence: "standard",
};

export const MOCK_LOCATIONS = [
  { name: "Nashik", lat: 19.9975, lng: 73.7898 },
  { name: "Punjab", lat: 30.9, lng: 75.8573 },
  { name: "Haryana", lat: 29.0588, lng: 76.0856 },
  { name: "Gujarat", lat: 23.0225, lng: 72.5714 },
  { name: "Madhya Pradesh", lat: 23.2599, lng: 77.4126 },
  { name: "Maharashtra", lat: 19.7515, lng: 75.7139 },
  { name: "Rajasthan", lat: 27.0238, lng: 74.2179 },
  { name: "Uttar Pradesh", lat: 26.8467, lng: 80.9462 },
  { name: "Bihar", lat: 25.0961, lng: 85.3131 },
  { name: "Karnataka", lat: 15.3173, lng: 75.7139 },
  { name: "Andhra Pradesh", lat: 15.9129, lng: 79.7399 },
  { name: "Telangana", lat: 17.1232, lng: 79.2089 },
  { name: "Odisha", lat: 20.9517, lng: 85.0985 },
  { name: "West Bengal", lat: 22.9868, lng: 87.855 },
  { name: "Tamil Nadu", lat: 11.1271, lng: 78.6569 },
  { name: "Kerala", lat: 10.8505, lng: 76.2711 },
  { name: "Assam", lat: 26.2006, lng: 92.9376 },
  { name: "Jharkhand", lat: 23.6102, lng: 85.2799 },
  { name: "Chhattisgarh", lat: 21.2787, lng: 81.8661 },
  { name: "Uttarakhand", lat: 30.0668, lng: 79.0193 },
];

export const MOCK_WEATHER_CURRENT = {
  temperature: 28.5,
  humidity: 62,
  rainfall: 1.2,
  wind_speed: 12,
  timestamp: new Date().toISOString(),
};

export const MOCK_WEATHER_FORECAST = {
  forecast: [
    { date: "2026-07-04", temp_max: 32, temp_min: 22, rainfall: 0.5 },
    { date: "2026-07-05", temp_max: 31, temp_min: 23, rainfall: 1.2 },
    { date: "2026-07-06", temp_max: 30, temp_min: 21, rainfall: 2.8 },
    { date: "2026-07-07", temp_max: 33, temp_min: 24, rainfall: 0 },
    { date: "2026-07-08", temp_max: 34, temp_min: 25, rainfall: 0 },
    { date: "2026-07-09", temp_max: 29, temp_min: 22, rainfall: 5.1 },
    { date: "2026-07-10", temp_max: 28, temp_min: 21, rainfall: 3.4 },
  ],
};

export const MOCK_PREDICTIONS_HISTORY = [
  { ...MOCK_PREDICTION, id: 42, created_at: "2026-06-30T10:30:00Z" },
  { ...MOCK_PREDICTION, id: 41, psi_score: 55, risk_level: "Medium", flowering_confidence: 0.72, created_at: "2026-06-15T08:00:00Z" },
  { ...MOCK_PREDICTION, id: 40, psi_score: 32, risk_level: "High", flowering_confidence: 0.65, ndvi_value: 0.38, created_at: "2026-06-01T06:00:00Z" },
];

export const MOCK_RESPONSES = {
  GET: {
    "/api/health": { status: "ok", service: "pollisync-api" },
    "/api/auth/me": { id: 1, email: "farmer@example.com", full_name: "Demo Farmer", created_at: "2026-01-01T00:00:00Z" },
    "/api/farms": [MOCK_FARM, { ...MOCK_FARM, id: 2, name: "South Orchard", crop_type: "Sunflower" }],
    "/api/weather/current": MOCK_WEATHER_CURRENT,
    "/api/weather/forecast": MOCK_WEATHER_FORECAST,
    "/api/predictions/latest": MOCK_PREDICTION,
    "/api/predictions/dashboard/summary": {
      farm: { id: 1, name: "North Field", crop_type: "Mustard", location_lat: 20.011, location_lng: 73.79 },
      current_weather: MOCK_WEATHER_CURRENT,
      latest_prediction: MOCK_PREDICTION,
      bee_species: ["Apis cerana", "Apis dorsata", "Apis florea"],
    },
    "/api/maps/bees": {
      center: { lat: 20.011, lng: 73.79 },
      occurrences: [
        { species: "Apis cerana", lat: 20.015, lng: 73.792, date: "2026-06-28" },
        { species: "Apis dorsata", lat: 20.008, lng: 73.785, date: "2026-06-27" },
        { species: "Apis florea", lat: 20.012, lng: 73.795, date: "2026-06-29" },
      ],
      species_summary: ["Apis cerana", "Apis dorsata", "Apis florea"],
    },
  },
  POST: {
    "/api/auth/login": SESSION,
    "/api/auth/register": SESSION,
    "/api/farms": MOCK_FARM,
    "/api/predictions": MOCK_PREDICTION,
    "/api/recommendations/generate": { recommendation: MOCK_PREDICTION.recommendation },
  },
};

export function matchMock(method, url) {
  const mockGroup = MOCK_RESPONSES[method];
  if (!mockGroup) return null;

  const exact = mockGroup[url];
  if (exact) return exact;

  for (const [pattern, response] of Object.entries(mockGroup)) {
    const regex = new RegExp("^" + pattern.replace(/:\w+/g, "\\d+").replace(/\?/g, "\\?") + "(\\?.*)?$");
    if (regex.test(url)) return response;
  }

  return null;
}
