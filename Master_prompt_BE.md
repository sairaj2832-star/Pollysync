PolliSync Backend Engineer Master Prompt

Objective
Implement or extend the backend API so the new frontend pages work end-to-end and support the latest frontend/next feature contract.

Frontend pages requiring backend support
FarmManagementPage.jsx
NotificationsPage.jsx
CropSuitabilityPage.jsx
AnalyticsPage.jsx
Plus existing dashboard/prediction flows

Existing backend architecture
FastAPI app entrypoint: main.py
Router registry: router.py
Route modules:
auth.py
farms.py
health.py
maps.py
predictions.py
recommendations.py
weather.py
Data layer: SQLAlchemy with SQLite
DB init and migration helper: database.py
Models: backend/app/models/*.py
Schemas: backend/app/schemas/*.py

Required new API contract
1. Farm management
GET /api/farms

returns list of farms for current user
should include:
id, name, crop_type, location or location_name
location_lat, location_lng
area_acres, soil_type
latest_psi
created_at

POST /api/farms

request body should accept:
name: string
crop_type: string
location: string or location_name: string
area_acres: number
soil_type: string
optional lat/lng if available
if frontend only sends location name, backend must handle it gracefully

DELETE /api/farms/{farm_id}

delete the farm and all related dependent records if appropriate

Optional: PATCH /api/farms/{farm_id}

update farm metadata

2. Notifications
GET /api/notifications

returns list of notification objects
each object:
id
type in [weather, bloom, pollinator, alert, info]
title
message
created_at
read: bool
optional farm_id

PATCH /api/notifications/{notification_id}/read

marks the notification read
returns status 200/204

3. Prediction / analytics
Existing endpoints already support most needs:
POST /api/predictions
GET /api/predictions?farm_id=...
GET /api/predictions/latest?farm_id=...
GET /api/predictions/dashboard/summary?farm_id=...
Ensure DashboardSummary returns:
farm metadata
current weather summary
latest prediction
bee species

4. Crop guide (optional backend support)
Frontend currently uses static crop metadata.
For a complete backend-backed experience, add:
GET /api/crops
GET /api/crops/suitability?location=...

5. Existing integrations
GET /api/weather/current?farm_id=...
GET /api/weather/forecast?farm_id=...&days=...
GET /api/maps/bees?farm_id=...&radius=...
POST /api/recommendations/generate

Data flow notes
Farm creation flow
Frontend collects name, crop, location string, area_acres, soil_type
Backend should normalize this into farm model
If available, associate location_lat/location_lng
Persist the farm and return the new FarmRead object

Analytics flow
Frontend uses GET /api/predictions?farm_id=...
It computes:
average PSI
max/min PSI
risk counts by level
crop performance averages
Backend should ensure prediction response includes psi_score, risk_level, crop, and created_at

Notification flow
Frontend loads GET /api/notifications
Displays types and unread badge counts
Mark as read triggers PATCH /api/notifications/{id}/read
Mark all as read calls the patch endpoint for each unread item

Farm list display
Frontend expects each farm item to include:

name
crop
location
area_acres
soil_type
latest_psi
id

If the backend can return a full farm response with these fields, the UI will render correctly.

File change list for backend implementation
Required files to add / update
farms.py
backend/app/api/routes/notifications.py (new)
router.py
farm.py
backend/app/models/notification.py (new)
__init__.py
farm.py
backend/app/schemas/notification.py (new)
database.py
Optionally backend/app/api/routes/crops.py

Existing files to review
predictions.py
weather.py
maps.py
recommendations.py
bee_service.py
prediction_service.py
config.py
auth.py

Important implementation notes
Backend currently uses SQLite + SQLAlchemy + Base.metadata.create_all()
Existing reconcile_sqlite_schema() only migrates user columns
You must add schema reconciliation for new fields/tables if the DB already exists
FarmManagementPage.jsx uses a location string and field names not present in current backend farm schema
Notifications should likely be scoped to authenticated user via current_user from auth
The backend is already set up with CORS and auth; new endpoints should reuse get_db() and current_user where appropriate

Priority work items
Highest priority
Add DELETE /api/farms/{farm_id} and support new farm fields
Add notifications backend support
Ensure farm list returns area_acres, soil_type, and latest_psi

Secondary priority
Add optional PATCH /api/farms/{farm_id}
Add backend crop guide endpoint
Add analytics aggregation endpoint if desired

Notes for the backend engineer
The frontend already has the UI for farms and notifications
The notification page will currently fall back to mock/demo data if backend fails
For full product readiness, implement the backend APIs instead of relying on fallback data
Keep auth on all new routes as needed
Ensure the backend returns JSON with stable field names used in frontend props
