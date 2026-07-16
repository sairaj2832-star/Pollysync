import {
  SESSION,
  MOCK_FARM,
  MOCK_FARMS,
  MOCK_PREDICTION,
  MOCK_WEATHER_CURRENT,
  MOCK_WEATHER_FORECAST,
  MOCK_PREDICTIONS_HISTORY,
  MOCK_LOCATIONS,
  MOCK_DISTRICTS,
  MOCK_NOTIFICATIONS,
} from "./mockData";

const delay = (ms = 500) => new Promise((r) => setTimeout(r, ms));
const clone = (v) => JSON.parse(JSON.stringify(v));

export async function mockLogin(email, password) {
  await delay(600);
  const resp = clone(SESSION);
  resp.user.email = email;
  return resp;
}

export async function mockRegister(email, password, full_name) {
  await delay(600);
  const resp = clone(SESSION);
  resp.user.email = email;
  resp.user.full_name = full_name;
  return resp;
}

export async function mockGetMe() {
  await delay(300);
  return clone(SESSION.user);
}

export async function mockGetFarms() {
  await delay(400);
  return clone(MOCK_FARMS);
}

export async function mockDeleteFarm() {
  await delay(300);
  return { success: true };
}

export async function mockCreateFarm(payload) {
  await delay(400);
  return { ...clone(MOCK_FARM), ...payload, id: Date.now() };
}

export async function mockGetWeatherCurrent(farm_id) {
  await delay(300);
  return clone(MOCK_WEATHER_CURRENT);
}

export async function mockGetWeatherForecast(farm_id, days) {
  await delay(300);
  return { forecast: clone(MOCK_WEATHER_FORECAST.forecast) };
}

export async function mockCreatePrediction(farm_id) {
  await delay(1500);
  return clone(MOCK_PREDICTION);
}

export async function mockGetPredictions(farm_id) {
  await delay(400);
  const farm = MOCK_FARMS.find((item) => String(item.id) === String(farm_id)) || MOCK_FARM;
  const scoreOffset = farm.id === MOCK_FARM.id ? 0 : farm.id.endsWith("002") ? -5 : farm.id.endsWith("003") ? 3 : -8;
  return clone(MOCK_PREDICTIONS_HISTORY.map((prediction) => ({
    ...prediction,
    id: `${farm.id}-${prediction.id}`,
    farm_id: farm.id,
    psi_score: Math.max(25, Math.min(96, prediction.psi_score + scoreOffset)),
    risk_level: prediction.psi_score + scoreOffset >= 70 ? "Low" : prediction.psi_score + scoreOffset >= 45 ? "Medium" : "High",
  })));
}

export async function mockGetLatestPrediction(farm_id) {
  await delay(400);
  return clone(MOCK_PREDICTION);
}

export async function mockGetDashboardSummary(farm_id) {
  await delay(600);
  const farm = MOCK_FARMS.find((item) => String(item.id) === String(farm_id)) || MOCK_FARM;
  const scoreOffset = farm.id === MOCK_FARM.id ? 0 : farm.id.endsWith("002") ? -5 : farm.id.endsWith("003") ? 3 : -8;
  const prediction = { ...MOCK_PREDICTION, farm_id: farm.id, psi_score: MOCK_PREDICTION.psi_score + scoreOffset, risk_level: scoreOffset <= -8 ? "Medium" : "Low" };
  return {
    farm: clone(farm),
    current_weather: clone(MOCK_WEATHER_CURRENT),
    latest_prediction: prediction,
    bee_species: clone(MOCK_PREDICTION.bee_species),
  };
}

export async function mockGenerateRecommendation(farm_id, prediction_id) {
  await delay(800);
  return { recommendation: MOCK_PREDICTION.recommendation };
}

export async function mockGetBeeOccurrences(farm_id, radius) {
  await delay(400);
  return {
    center: { lat: 20.011, lng: 73.79 },
    occurrences: [
      { species: "Apis cerana", lat: 20.015, lng: 73.792, date: "2026-06-28" },
      { species: "Apis dorsata", lat: 20.008, lng: 73.785, date: "2026-06-27" },
      { species: "Apis florea", lat: 20.012, lng: 73.795, date: "2026-06-29" },
    ],
    species_summary: ["Apis cerana", "Apis dorsata", "Apis florea"],
  };
}

export async function mockGetHealth() {
  await delay(200);
  return { status: "ok", service: "pollisync-api" };
}

export async function mockGetNotifications() {
  await delay(300);
  return clone(MOCK_NOTIFICATIONS);
}

export async function mockMarkNotificationRead() {
  await delay(180);
  return { success: true };
}

export async function mockUpdateProfile(payload) {
  await delay(400);
  const user = clone(SESSION.user);
  Object.assign(user, payload);
  return user;
}

export async function mockUpdateFarm(farm_id, payload) {
  await delay(400);
  return { ...clone(MOCK_FARM), ...payload, id: farm_id };
}

export async function mockGetNotificationPreferences() {
  await delay(300);
  return {
    id: 1,
    user_id: 1,
    push_critical: true,
    push_daily: true,
    push_system: false,
    email_weekly: true,
    email_billing: true,
    whatsapp_urgent: false,
    sms_alerts: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

export async function mockUpdateNotificationPreferences(payload) {
  await delay(300);
  const prefs = await mockGetNotificationPreferences();
  Object.assign(prefs, payload);
  return prefs;
}

export async function mockGetTeamMembers(farm_id) {
  await delay(300);
  return [
    { id: "mock-member-id-001", farm_id, email: "elena@pollisync.ag", name: "Elena Rodriguez", role: "admin", status: "active", invited_by: "mock-user-id-001", created_at: new Date().toISOString() },
    { id: "mock-member-id-002", farm_id, email: "james@pollisync.ag", name: "James Carter", role: "editor", status: "active", invited_by: "mock-user-id-001", created_at: new Date().toISOString() },
    { id: "mock-member-id-003", farm_id, email: "priya@pollisync.ag", name: "Priya Sharma", role: "viewer", status: "pending", invited_by: "mock-user-id-001", created_at: new Date().toISOString() },
  ];
}

export async function mockInviteTeamMember(farm_id, payload) {
  await delay(400);
  return { id: "mock-member-id-" + Date.now(), farm_id, ...payload, status: "pending", invited_by: "mock-user-id-001", created_at: new Date().toISOString() };
}

export async function mockRemoveTeamMember(farm_id, member_id) {
  await delay(300);
}

export function getMockLocations() {
  return MOCK_LOCATIONS;
}

export async function mockGetDistricts() {
  await delay(300);
  return clone(MOCK_DISTRICTS);
}

export async function mockGetDistrict(slug) {
  await delay(300);
  const district = MOCK_DISTRICTS.find((d) => d.slug === slug);
  if (!district) {
    throw new Error("District not found");
  }
  return clone(district);
}
