Backend Engineer Task Summary
I reviewed the current backend and frontend integration points. Your backend must now support the new frontend pages and data fields added in FarmManagementPage.jsx, NotificationsPage.jsx, CropSuitabilityPage.jsx, and AnalyticsPage.jsx.

Missing / Updated Backend APIs
Existing backend endpoints
GET /api/health
POST /api/auth/register
POST /api/auth/login
POST /api/auth/token
POST /api/auth/refresh
POST /api/auth/logout
GET /api/auth/me
POST /api/auth/oauth/google
GET /api/farms
POST /api/farms
GET /api/weather/current?farm_id=...
GET /api/weather/forecast?farm_id=...&days=...
POST /api/predictions
GET /api/predictions?farm_id=...
GET /api/predictions/latest?farm_id=...
GET /api/predictions/dashboard/summary?farm_id=...
POST /api/recommendations/generate
GET /api/maps/bees?farm_id=...&radius=...
New backend endpoints required
DELETE /api/farms/{farm_id}
GET /api/notifications
PATCH /api/notifications/{notification_id}/read
Optional / recommended backend endpoints for full experience
PATCH /api/farms/{farm_id} — update farm metadata
GET /api/crops or GET /api/crops/suitability — serve crop guide metadata from backend instead of frontend static data
GET /api/analytics/summary?farm_id=... — optional, if you want analytics aggregation backend-side
Backend data contract and field notes
Farm creation / storage
Frontend currently sends this payload from FarmManagementPage.jsx:

name
crop
location (string name)
area_acres
soil_type
But backend currently expects FarmCreate:

name
crop_type
location_lat
location_lng
Required backend model/schema updates
Update backend to support the frontend’s farm fields:

area_acres: float
soil_type: str
location or location_name: str
optionally preserve location_lat, location_lng if you want geospatial/weather integration
optionally add latest_psi to farm responses for UI convenience
Prediction API
The existing prediction model and schema appear correct:

request body: { farm_id: int, region?: string }
response includes psi_score, risk_level, weather_summary, pollen_summary, ndvi_value, bee_species, recommendation
Notifications
New backend data contract:

id
type = weather | bloom | pollinator | alert | info
title
message
created_at
read: bool
optional: farm_id, user_id
Important backend/frontend contract mismatches
1. Farm endpoint mismatch
Current backend FarmCreate schema uses location_lat / location_lng, while frontend sends location string, area_acres, and soil_type.

Action:

update backend schema/model to accept the frontend payload,
or sync frontend to send lat/lng and proper field names.
2. No notification backend exists
Frontend NotificationsPage.jsx uses:

GET /api/notifications
PATCH /api/notifications/{id}/read
Currently backend has no notification route or model, so this page must be backed by new API support for full experience.

3. Farm list response enrichment
Frontend expects farm objects to include:

location
area_acres
soil_type
latest_psi
Backend GET /api/farms should return those fields, and may compute latest_psi from the latest prediction.

Backend file updates needed
Must modify / add
farms.py

add DELETE /api/farms/{farm_id}
optionally add PATCH /api/farms/{farm_id}
update request/response models to support additional farm fields
farm.py

add area_acres
add soil_type
add location_name or location
keep location_lat / location_lng if weather/maps need them
farm.py

update FarmCreate
update FarmRead
backend/app/api/routes/notifications.py (new)

implement GET /api/notifications
implement PATCH /api/notifications/{notification_id}/read
backend/app/models/notification.py (new)

create notification model
include user_id if notifications should be scoped per user
backend/app/schemas/notification.py (new)

define NotificationRead
router.py

register the new notifications router
__init__.py

export the new Notification model
database.py

update reconcile_sqlite_schema() to handle schema changes for existing SQLite DB if needed
Recommended backend improvement files
predictions.py
compute and return farm summary/metadata if needed
weather.py
already exists and can be left as-is
maps.py
already exists and can be left as-is
backend/app/services/...
if you want to move notification creation into service logic
Master prompt for Backend Engineer
Below is the exact content to save into Master_prompt_BE.md. If file creation is not available in this environment, copy/paste it manually into the repo root.

Master_prompt_BE.md
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
