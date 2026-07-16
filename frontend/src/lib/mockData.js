export const SESSION = {
  access_token: "mock_access_token_pollisync_" + Date.now(),
  refresh_token: "mock_refresh_token_" + Date.now(),
  expires_in: 1800,
  user: { id: "mock-user-id-001", email: "ananya@greenridge.farm", full_name: "Ananya Deshmukh", phone: "+91 98765 43210", role: "Farm manager", organization: "Green Ridge Farms", language: "en", has_onboarded: true, created_at: "2025-08-14T00:00:00Z" },
};

export const MOCK_FARM = {
  id: "mock-farm-id-001",
  name: "Sinnar Mustard Block",
  crop_type: "Mustard",
  district_slug: "nashik",
  location_lat: 19.9975,
  location_lng: 73.7898,
  is_default: true,
  area_acres: 18.5,
  soil_type: "loamy",
  location_name: "Sinnar, Nashik",
  planting_date: "2026-06-02",
  created_at: "2025-10-12T00:00:00Z",
};

export const MOCK_PREDICTION = {
  id: "mock-prediction-id-001",
  farm_id: "mock-farm-id-001",
  flowering_start: "2026-07-19",
  flowering_end: "2026-07-29",
  flowering_confidence: 0.91,
  psi_score: 82,
  risk_level: "Low",
  weather_summary: { temperature: 28.5, humidity: 62, rainfall: 1.2, wind_speed: 12 },
  pollen_summary: { tree: 3, grass: 2, weed: 1 },
  ndvi_value: 0.78,
  bee_species: ["Apis cerana", "Apis dorsata", "Apis florea", "Xylocopa latipes"],
  recommendation:
    "## Assessment for Mustard\n\nCurrent conditions are favourable for pollination. " +
    "The temperature of 28°C and humidity at 62% are within optimal ranges.\n\n" +
    "**Recommended Actions:**\n- Ensure adequate irrigation during flowering window\n" +
    "- Monitor for pest activity, especially aphids\n- Consider introducing one additional hive per acre\n\n" +
    "Conditions are favourable. Maintain regular crop management practices.\n\n" +
    "**Confidence:** Moderate — based on seasonal models and local weather data.",
  created_at: "2026-07-15T06:45:00Z",
  model_source: "general_v1",
  data_confidence: "standard",
};

export const MOCK_FARMS = [
  MOCK_FARM,
  { id: "mock-farm-id-002", name: "Niphad Sunflower Estate", crop_type: "Sunflower", district_slug: "nashik", location_lat: 20.0833, location_lng: 74.1083, location_name: "Niphad, Nashik", area_acres: 24, soil_type: "sandy loam", planting_date: "2026-05-18", is_default: false, created_at: "2025-09-08T00:00:00Z" },
  { id: "mock-farm-id-003", name: "Dindori Pomegranate Orchard", crop_type: "Pomegranate", district_slug: "nashik", location_lat: 20.2042, location_lng: 73.8333, location_name: "Dindori, Nashik", area_acres: 12.75, soil_type: "well-drained loam", planting_date: "2024-07-01", is_default: false, created_at: "2024-07-01T00:00:00Z" },
  { id: "mock-farm-id-004", name: "Igatpuri Vegetable Patch", crop_type: "Tomato", district_slug: "nashik", location_lat: 19.6954, location_lng: 73.5626, location_name: "Igatpuri, Nashik", area_acres: 8.25, soil_type: "silty loam", planting_date: "2026-06-21", is_default: false, created_at: "2026-01-17T00:00:00Z" },
];

export const MOCK_DISTRICTS = [
  { slug: "amaravati", name: "Amaravati", state: "Maharashtra", centroid_lat: 16.2348, centroid_lng: 79.7433, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "aurangabad", name: "Aurangabad", state: "Maharashtra", centroid_lat: 19.8762, centroid_lng: 75.3433, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "jalgaon", name: "Jalgaon", state: "Maharashtra", centroid_lat: 21.0078, centroid_lng: 75.9928, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "kolhapur", name: "Kolhapur", state: "Maharashtra", centroid_lat: 16.7050, centroid_lng: 74.2433, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "latur", name: "Latur", state: "Maharashtra", centroid_lat: 18.4088, centroid_lng: 76.5602, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "nagpur", name: "Nagpur", state: "Maharashtra", centroid_lat: 21.1458, centroid_lng: 79.0882, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "nashik", name: "Nashik", state: "Maharashtra", centroid_lat: 19.9975, centroid_lng: 73.7898, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "pune", name: "Pune", state: "Maharashtra", centroid_lat: 18.5204, centroid_lng: 73.8567, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "satara", name: "Satara", state: "Maharashtra", centroid_lat: 17.6868, centroid_lng: 73.9997, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "solapur", name: "Solapur", state: "Maharashtra", centroid_lat: 17.6599, centroid_lng: 75.9064, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "mumbai", name: "Mumbai", state: "Maharashtra", centroid_lat: 19.0760, centroid_lng: 72.8777, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "ahmednagar", name: "Ahmednagar", state: "Maharashtra", centroid_lat: 19.0952, centroid_lng: 74.7496, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "amravati", name: "Amravati", state: "Maharashtra", centroid_lat: 20.9374, centroid_lng: 77.7796, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "chandrapur", name: "Chandrapur", state: "Maharashtra", centroid_lat: 19.9615, centroid_lng: 79.3032, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "dhule", name: "Dhule", state: "Maharashtra", centroid_lat: 20.9040, centroid_lng: 74.7748, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "gadchiroli", name: "Gadchiroli", state: "Maharashtra", centroid_lat: 20.1809, centroid_lng: 80.0883, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "gondia", name: "Gondia", state: "Maharashtra", centroid_lat: 21.4602, centroid_lng: 80.1883, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "hingoli", name: "Hingoli", state: "Maharashtra", centroid_lat: 19.7150, centroid_lng: 77.1310, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "nanded", name: "Nanded", state: "Maharashtra", centroid_lat: 19.1388, centroid_lng: 77.3218, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "parbhani", name: "Parbhani", state: "Maharashtra", centroid_lat: 19.2686, centroid_lng: 76.7708, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "wardha", name: "Wardha", state: "Maharashtra", centroid_lat: 20.7453, centroid_lng: 78.6023, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "washim", name: "Washim", state: "Maharashtra", centroid_lat: 20.1117, centroid_lng: 77.1330, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
  { slug: "yavatmal", name: "Yavatmal", state: "Maharashtra", centroid_lat: 20.3897, centroid_lng: 78.1308, radius_km: 5.0, created_at: "2026-01-01T00:00:00Z" },
];

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
    { date: "2026-07-15", temp_max: 29, temp_min: 21, rainfall: 3.4 },
    { date: "2026-07-16", temp_max: 30, temp_min: 22, rainfall: 1.2 },
    { date: "2026-07-17", temp_max: 31, temp_min: 22, rainfall: 0.4 },
    { date: "2026-07-18", temp_max: 30, temp_min: 23, rainfall: 0 },
    { date: "2026-07-19", temp_max: 29, temp_min: 22, rainfall: 1.8 },
    { date: "2026-07-20", temp_max: 28, temp_min: 21, rainfall: 4.6 },
    { date: "2026-07-21", temp_max: 29, temp_min: 21, rainfall: 2.1 },
  ],
};

export const MOCK_PREDICTIONS_HISTORY = [
  { ...MOCK_PREDICTION, id: "pred-001", created_at: "2026-07-15T06:45:00Z" },
  { ...MOCK_PREDICTION, id: "pred-002", psi_score: 79, risk_level: "Low", flowering_confidence: 0.89, ndvi_value: 0.76, created_at: "2026-07-11T07:20:00Z" },
  { ...MOCK_PREDICTION, id: "pred-003", psi_score: 74, risk_level: "Low", flowering_confidence: 0.85, ndvi_value: 0.73, created_at: "2026-07-07T06:55:00Z" },
  { ...MOCK_PREDICTION, id: "pred-004", psi_score: 68, risk_level: "Medium", flowering_confidence: 0.81, ndvi_value: 0.69, created_at: "2026-07-02T08:10:00Z" },
  { ...MOCK_PREDICTION, id: "pred-005", psi_score: 61, risk_level: "Medium", flowering_confidence: 0.77, ndvi_value: 0.65, created_at: "2026-06-27T07:35:00Z" },
  { ...MOCK_PREDICTION, id: "pred-006", psi_score: 57, risk_level: "Medium", flowering_confidence: 0.75, ndvi_value: 0.61, created_at: "2026-06-22T06:40:00Z" },
  { ...MOCK_PREDICTION, id: "pred-007", psi_score: 49, risk_level: "Medium", flowering_confidence: 0.70, ndvi_value: 0.56, created_at: "2026-06-17T07:15:00Z" },
  { ...MOCK_PREDICTION, id: "pred-008", psi_score: 38, risk_level: "High", flowering_confidence: 0.66, ndvi_value: 0.48, created_at: "2026-06-12T08:25:00Z" },
  { ...MOCK_PREDICTION, id: "pred-009", psi_score: 44, risk_level: "High", flowering_confidence: 0.68, ndvi_value: 0.51, created_at: "2026-06-07T06:30:00Z" },
  { ...MOCK_PREDICTION, id: "pred-010", psi_score: 53, risk_level: "Medium", flowering_confidence: 0.72, ndvi_value: 0.58, created_at: "2026-06-02T07:50:00Z" },
  { ...MOCK_PREDICTION, id: "pred-011", psi_score: 64, risk_level: "Medium", flowering_confidence: 0.78, ndvi_value: 0.64, created_at: "2026-05-27T06:20:00Z" },
  { ...MOCK_PREDICTION, id: "pred-012", psi_score: 71, risk_level: "Low", flowering_confidence: 0.82, ndvi_value: 0.68, created_at: "2026-05-21T07:40:00Z" },
];

export const MOCK_NOTIFICATIONS = [
  { id: "notif-001", type: "bloom", title: "Peak bloom begins this week", message: "Sinnar Mustard Block is entering its strongest flowering window. Confirm hive placement by Friday.", created_at: "2026-07-15T05:30:00Z", read: false },
  { id: "notif-002", type: "weather", title: "Ideal pollinator weather ahead", message: "Three calm, dry mornings are forecast for Nashik — a strong window for bee activity.", created_at: "2026-07-14T12:10:00Z", read: false },
  { id: "notif-003", type: "pollinator", title: "New bee activity recorded", message: "Four pollinator species were recorded near your mustard block this week, up from three last week.", created_at: "2026-07-13T08:20:00Z", read: false },
  { id: "notif-004", type: "alert", title: "Wind advisory for Niphad", message: "Wind may exceed 18 km/h on Wednesday afternoon. Avoid spraying while pollinators are active.", created_at: "2026-07-12T10:00:00Z", read: true },
  { id: "notif-005", type: "info", title: "Weekly field report is ready", message: "Your July week-two report shows PSI improving by 14 points across your active farms.", created_at: "2026-07-11T06:00:00Z", read: true },
  { id: "notif-006", type: "weather", title: "Rainfall recorded", message: "6.4 mm rainfall was logged at Sinnar Mustard Block. Soil moisture remains in the healthy range.", created_at: "2026-07-09T17:40:00Z", read: true },
  { id: "notif-007", type: "bloom", title: "Orchard inspection due", message: "Schedule a flower-set check for Dindori Pomegranate Orchard within the next five days.", created_at: "2026-07-08T08:15:00Z", read: true },
];

export const MOCK_RESPONSES = {
  GET: {
    "/api/health": { status: "ok", service: "pollisync-api" },
    "/api/auth/me": SESSION.user,
    "/api/farms": MOCK_FARMS,
    "/api/districts": MOCK_DISTRICTS,
    "/api/weather/current": MOCK_WEATHER_CURRENT,
    "/api/weather/forecast": MOCK_WEATHER_FORECAST,
    "/api/predictions/latest": MOCK_PREDICTION,
    "/api/predictions/dashboard/summary": {
      farm: { id: "mock-farm-id-001", name: "North Field", crop_type: "Mustard", location_lat: 19.9975, location_lng: 73.7898 },
      current_weather: MOCK_WEATHER_CURRENT,
      latest_prediction: MOCK_PREDICTION,
      bee_species: ["Apis cerana", "Apis dorsata", "Apis florea"],
    },
    "/api/maps/bees": {
      center: { lat: 19.9975, lng: 73.7898 },
      occurrences: [
        { species: "Apis cerana", lat: 20.0, lng: 73.792, date: "2026-06-28" },
        { species: "Apis dorsata", lat: 19.995, lng: 73.785, date: "2026-06-27" },
        { species: "Apis florea", lat: 19.998, lng: 73.795, date: "2026-06-29" },
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
