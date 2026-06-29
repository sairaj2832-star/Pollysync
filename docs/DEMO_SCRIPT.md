# PolliSync Demo Script — Hackathon Presentation

## Setup (Before Demo)
1. Ensure backend is deployed: `https://polli-sync-api.onrender.com`
2. Ensure frontend is deployed: `https://polli-sync-web.vercel.app`
3. Seed database with a test user if needed

---

## Demo Flow (3-4 minutes)

### 1. Landing Page (30s)
- Open the app URL
- **Say:** "Welcome to PolliSync — AI-based crop pollination suitability system."
- Highlight: Weather + Bee data + ML models + AI recommendations

### 2. Registration (30s)
- Click "Get Started" → Register page
- Enter: Name, email, password
- **Say:** "Simple registration to save farm profiles"

### 3. Create Farm & Predict (60s)
- Navigate to Predict page
- Select: Crop = Mustard, Location = Nashik
- Click "Run Prediction"
- **Say:** "Backend fetches real weather from Open-Meteo, bee data from GBIF, runs ML models, and generates AI recommendation"
- Show loading states

### 4. Dashboard (90s)
- **PSI Gauge:** "Pollination Suitability Index — 84/100, low risk"
- **Weather cards:** "Real weather data — temperature, humidity, rainfall"
- **Flowering Calendar:** "Predicted window: 18 Jan - 25 Jan, 87% confident"
- **Pollen bars:** "Seasonal pollen index by type"
- **AI Recommendation:** "Actionable advice specific to mustard in Nashik"
- **NDVI Card:** "Crop health from satellite vegetation index"
- **Bee Map:** "OpenStreetMap with bee observations"

### 5. Closing (30s)
- **Say:** "Built with: React + FastAPI + Scikit-learn + free APIs"
- "Repository has CI/CD — every PR auto-tested"
- "Future: Real satellite NDVI, Google Pollen API, mobile app"

---

## Fallback Scenarios

| Scenario | What to Do |
|----------|-----------|
| API is slow (cold start) | "The free tier sleeps after inactivity — give it 30s to wake up" |
| No bee data for location | "GBIF may not have records — showing mock data representative of the region" |
| LLM key not set | "Local fallback recommendation is shown when API key is not configured" |
| Mobile view | Resize browser to show responsive layout |
