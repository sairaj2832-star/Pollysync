import {
  SESSION,
  MOCK_FARM,
  MOCK_PREDICTION,
  MOCK_WEATHER_CURRENT,
  MOCK_WEATHER_FORECAST,
  MOCK_PREDICTIONS_HISTORY,
  MOCK_LOCATIONS,
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
  return [clone(MOCK_FARM)];
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
  return clone(MOCK_PREDICTIONS_HISTORY);
}

export async function mockGetLatestPrediction(farm_id) {
  await delay(400);
  return clone(MOCK_PREDICTION);
}

export async function mockGetDashboardSummary(farm_id) {
  await delay(600);
  return {
    farm: { id: 1, name: "North Field", crop_type: "Mustard", location_lat: 20.011, location_lng: 73.79 },
    current_weather: clone(MOCK_WEATHER_CURRENT),
    latest_prediction: clone(MOCK_PREDICTION),
    bee_species: ["Apis cerana", "Apis dorsata", "Apis florea"],
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

export function getMockLocations() {
  return MOCK_LOCATIONS;
}
