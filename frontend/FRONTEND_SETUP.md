# Frontend React Development - Setup Complete ✅

This document summarizes what's been set up for PolliSync frontend development and how to use the resources.

---

## 📋 What Has Been Created

### 1. **`.instructions.md`** - Comprehensive Team Guide
**Location**: `frontend/.instructions.md`
**Purpose**: Main documentation for frontend development
**Contains**:
- Design system architecture (colors, typography, spacing)
- Complete list of 10 design screens to implement
- Data structures and fake data patterns
- Implementation guidelines and component structure
- Development workflow (4 phases)
- Code examples (Button, mock data usage)
- Testing checklist
- Backend integration instructions

**Who Should Read**: All frontend team members, QA, project managers

---

### 2. **`.agent.md`** - AI Frontend Agent Instructions
**Location**: `frontend/.agent.md`
**Purpose**: Detailed instructions for AI/automated frontend agent
**Contains**:
- Concise role & context
- Quick design system reference (colors, typography, spacing)
- 10 design screens with specific components needed
- Implementation priority (7 phases)
- Mock data integration pattern
- Code structure examples
- Important rules (DO's and DON'Ts)
- File organization
- Debugging tips
- Testing checklist

**Who Should Use**: Running frontend development with an AI agent/LLM

**How to Use with an Agent**:
```
You have a `.agent.md` file in the frontend directory that contains
all the specifications. Use it to understand what to build, in what order,
and follow the guidelines for React components.
```

---

### 3. **`DESIGN_SYSTEM.md`** - Design Reference & Component Specs
**Location**: `frontend/DESIGN_SYSTEM.md`
**Purpose**: Quick reference for developers
**Contains**:
- Complete color palette with hex values
- Typography system with usage guidelines
- Spacing scale
- Border radius specifications
- Component specifications (Button, Input, Card, etc.)
- Layout patterns
- Common patterns (empty state, loading, error, success)
- Responsive breakpoints (mobile-first approach)
- Accessibility guidelines (WCAG AA)
- Animation guidelines
- Component checklist
- Implementation order (7 weeks)

**Who Should Use**: Frontend developers building components
**How to Use**: Bookmark it! Reference while building components to ensure consistency.

---

### 4. **`src/data/mockData.js`** - Fake Data for Development
**Location**: `frontend/src/data/mockData.js`
**Purpose**: Realistic mock data for UI preview and testing
**Contains**:
- Mock user object
- Functions to generate mock metrics, predictions, chart data
- Historical prediction data
- Reference data (locations, crops, chat messages)
- Complete `dataService` with methods for all operations
  - `getUser()`, `login()`, `register()`, `logout()`
  - `getMetrics()`, `getPredictions()`
  - `createPrediction()`, `getChatMessages()`
  - `sendChatMessage()`

**Key Feature**: Built with network delay simulation (300-2000ms) for realistic testing

**How to Use**:
```jsx
// In any component
import { metricsService } from "../services/api";

// Automatically uses mock data in development
const metrics = await metricsService.getCurrent();
// Returns: { psi: 0.78, ndvi: 0.65, pollenCount: 2450, ... }
```

---

### 5. **`src/services/api.js`** - API Integration Layer
**Location**: `frontend/src/services/api.js`
**Purpose**: Bridge between components and backend API (ready for switching from mock to real)
**Contains**:
- `authService`: login, register, logout, getCurrentUser, verifyToken
- `predictionsService`: list, getById, create, delete, getHistory
- `metricsService`: getCurrent, getHistorical, getByLocation
- `chatService`: getHistory, sendMessage
- `referenceService`: getLocations, getCrops

**Smart Switching**:
```jsx
// Checks REACT_APP_USE_MOCK_DATA environment variable
if (USE_MOCK_DATA) {
  return dataService.getUser();  // Uses fake data
} else {
  // Calls real API endpoint
  fetch(`${API_BASE_URL}/auth/me`)
}
```

**How to Use**:
```jsx
import { authService, predictionsService, metricsService } from "../services/api";

// Same code works with both mock and real data!
const user = await authService.getCurrentUser();
const predictions = await predictionsService.list({ date: "2026-07-04" });
```

---

## 🚀 How to Use These Resources

### For Frontend Developers

1. **Start Here**: Read `DESIGN_SYSTEM.md` for quick reference
2. **Build**: Use `.instructions.md` for comprehensive guidance
3. **Code**: Reference component specifications in `DESIGN_SYSTEM.md`
4. **Test**: Use mock data from `mockData.js` during development
5. **Verify**: Check against the Stitch design files (`stitch_pollisync_saas_design_system/*/screen.png`)

### For AI Agent/Automated Development

1. **Read**: `.agent.md` contains all specifications
2. **Reference**: `.instructions.md` for detailed guidelines
3. **Code**: Use component specifications from `DESIGN_SYSTEM.md`
4. **Data**: Use `mockData.js` for fake data in components
5. **API**: Use `api.js` service layer for data fetching

### For Switching to Real Backend

**When backend is ready**:
```bash
# Set environment variable
export REACT_APP_USE_MOCK_DATA=false
export REACT_APP_API_URL=http://backend-url/api

npm run dev
```

The **same components and code** will automatically use real API endpoints instead of mock data!

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│   React Components (pages/          │
│   components/)                      │
└────────────┬────────────────────────┘
             │ imports
             ▼
┌─────────────────────────────────────┐
│   API Service Layer                 │
│   (src/services/api.js)             │
└────────────┬────────────────────────┘
             │ 
      ┌──────┴──────┐
      ▼             ▼
  Mock Data    Real API
  (dev)        (production)
```

### Data Flow Example: Fetching Dashboard Metrics

**With Mock Data (Development)**:
```
DashboardPage component
  → metricsService.getCurrent()
    → api.js checks USE_MOCK_DATA = true
      → returns mockData.getMockMetrics()
        → { psi: 0.78, ndvi: 0.65, ... }
```

**With Real API (Production)**:
```
DashboardPage component
  → metricsService.getCurrent()
    → api.js checks USE_MOCK_DATA = false
      → fetch(${API_BASE_URL}/metrics/current)
        → backend returns { psi: 0.78, ndvi: 0.65, ... }
```

**Same component code works for both!** ✨

---

## 📊 Design Screens to Implement (10 Total)

| # | Screen | File Location | Priority | Status |
|---|--------|---|----------|--------|
| 1 | Landing Page | `pollisync_landing_page_light_mode/` | High | Ready |
| 2 | Registration | `pollisync_registration_light_mode/` | High | Ready |
| 3 | Login | `pollisync_login_light_mode/` | High | Ready |
| 4 | Dashboard (Analytics) | `pollisync_analytics_dashboard_light_mode/` | High | Ready |
| 5 | Dashboard Empty | `dashboard_empty_state_light_mode/` | Medium | Ready |
| 6 | Prediction Step 1 | `new_prediction_step_1_light_mode/` | Medium | Ready |
| 7 | Prediction Step 2 | `new_prediction_step_2_light_mode/` | Medium | Ready |
| 8 | Prediction Step 3 | `new_prediction_step_3_light_mode/` | Medium | Ready |
| 9 | Prediction History | `prediction_history_light_mode/` | Medium | Ready |
| 10 | Prediction Loading | `prediction_loading_state_light_mode/` | Medium | Ready |
| 11 | AI Assistant | `pollisync_ai_assistant_light_mode/` | Low | Ready |
| 12 | Design Reference | `pollisync_design_system_reference_board/` | Reference | - |

**Each screen has**:
- `code.html` - Design code with Tailwind CSS configuration
- `screen.png` - Visual preview to match

---

## 🎯 Implementation Priority

### Phase 1: Foundation (Week 1)
- [ ] UI Primitives: Button, Input, Select, Card, Container
- [ ] Forms: FormField, Checkbox, Radio, Toggle
- [ ] Typography & Colors: Apply design system

### Phase 2: Authentication (Week 2)
- [ ] LoginPage
- [ ] RegisterPage
- [ ] ProtectedRoute
- [ ] Auth Context

### Phase 3: Public Pages (Week 3)
- [ ] HomePage (Landing)
- [ ] Navigation Header
- [ ] Footer

### Phase 4: Dashboard (Week 4)
- [ ] DashboardPage
- [ ] MetricCard components
- [ ] TrendChart
- [ ] FilterBar

### Phase 5: Predictions (Week 5)
- [ ] PredictionWizard (3 steps)
- [ ] PredictionHistory
- [ ] PredictionLoader

### Phase 6: AI Assistant (Week 6)
- [ ] ChatInterface
- [ ] ChatMessage

### Phase 7: Polish (Week 7)
- [ ] Empty states
- [ ] Error handling
- [ ] Responsive design
- [ ] Performance optimization
- [ ] Accessibility audit

---

## 🔧 Development Setup

### Prerequisites
```bash
# Node.js 18+
# npm or yarn
```

### Quick Start
```bash
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev

# The app will run with MOCK DATA by default
# http://localhost:5173
```

### Use Mock Data (Default)
```bash
npm run dev
# Uses: REACT_APP_USE_MOCK_DATA=true (default)
```

### Switch to Real Backend
```bash
# Set environment variable
REACT_APP_USE_MOCK_DATA=false npm run dev

# Or update .env file:
# REACT_APP_USE_MOCK_DATA=false
# REACT_APP_API_URL=http://localhost:8000/api
```

### Build for Production
```bash
npm run build

# Backend integration required before productionizing
```

---

## 📚 File Reference

### Documentation Files (You Are Here!)
```
frontend/
├── .instructions.md      ← Main development guide
├── .agent.md             ← AI agent instructions
├── DESIGN_SYSTEM.md      ← Component & design reference
└── FRONTEND_SETUP.md     ← This file
```

### Code Files (Ready to Use)
```
frontend/src/
├── data/
│   └── mockData.js       ← Fake data generators
├── services/
│   └── api.js            ← API integration layer
├── components/           ← Where to build components
│   ├── common/           ← UI primitives
│   ├── forms/            ← Form components
│   └── dashboard/        ← Dashboard components
├── pages/                ← Page components (existing)
├── context/              ← React Context (existing)
├── hooks/                ← Custom hooks (existing)
└── App.jsx               ← Main app component
```

### Design Reference
```
frontend/stitch_pollisync_saas_design_system/
├── pollisync_landing_page_light_mode/
│   ├── code.html         ← Design code (reference)
│   └── screen.png        ← Visual design (reference)
├── pollisync_login_light_mode/
├── pollisync_registration_light_mode/
├── pollisync_analytics_dashboard_light_mode/
├── ... (10 more screens)
```

---

## ✅ Checklist Before Starting

- [ ] Read `.agent.md` or `.instructions.md`
- [ ] Review `DESIGN_SYSTEM.md` for color/typography
- [ ] Check corresponding Stitch `screen.png` files
- [ ] Verify Tailwind config has theme colors
- [ ] Test mock data works: `npm run dev`
- [ ] Test component creation with mock data
- [ ] Verify no console errors
- [ ] Check responsive behavior (mobile, tablet, desktop)

---

## 🔄 Workflow for Building a Component

### Example: Building MetricCard Component

1. **Find Design**: Check `stitch_pollisync_saas_design_system/pollisync_analytics_dashboard_light_mode/screen.png`
2. **Extract Code**: Look at `code.html` for the metric card HTML/CSS
3. **Reference Specs**: Check `DESIGN_SYSTEM.md` for MetricCard specs
4. **Create Component**:
   ```jsx
   // components/MetricCard.jsx
   export function MetricCard({ title, value, benchmark }) {
     return (
       <div className="bg-white rounded-xl p-lg shadow-sm">
         <h3 className="text-label-md text-on-surface-variant">{title}</h3>
         <p className="text-headline-md text-primary font-bold">{value}</p>
         <p className="text-body-small text-on-surface-variant">
           Benchmark: {benchmark}
         </p>
       </div>
     );
   }
   ```
5. **Add to Page**:
   ```jsx
   // pages/DashboardPage.jsx
   import { metricsService } from "../services/api";
   import { MetricCard } from "../components/MetricCard";
   
   export default function DashboardPage() {
     const [metrics, setMetrics] = useState(null);
     useEffect(() => {
       metricsService.getCurrent().then(setMetrics);
     }, []);
     
     return (
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
         <MetricCard title="PSI" value={metrics?.psi} benchmark={0.65} />
         {/* More cards... */}
       </div>
     );
   }
   ```
6. **Test**: 
   - Check if it matches `screen.png` visually
   - Verify responsive behavior (375px, 768px, 1280px)
   - Check no console errors
   - Verify mock data displays correctly
7. **Move to Next**: Once matching, move to next component

---

## 🎓 Learning Resources

### Tailwind CSS
- Official docs: https://tailwindcss.com
- Color system: https://tailwindcss.com/docs/customizing-colors
- Responsive design: https://tailwindcss.com/docs/responsive-design

### React Best Practices
- Hooks: https://react.dev/reference/react/hooks
- Context: https://react.dev/reference/react/useContext
- Performance: https://react.dev/reference/react/memo

### Accessibility
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- ARIA: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA

---

## 🆘 Troubleshooting

### Colors Not Matching Design?
- Check Tailwind config has the exact hex values
- Use Chrome DevTools color picker to verify
- Ensure no CSS overrides in `index.css`

### Mock Data Not Showing?
- Verify `REACT_APP_USE_MOCK_DATA` is not set to false
- Check import path: `import { metricsService } from "../services/api"`
- Check browser console for import/runtime errors

### Responsive Design Broken?
- Use mobile-first approach: default styles, then `md:`, `lg:` overrides
- Test in Chrome DevTools device emulation
- Check grid/flex columns for different breakpoints

### Component Doesn't Match Design?
- Compare pixel-by-pixel with `screen.png`
- Check spacing: should match 4px, 8px, 16px, 24px grid
- Verify colors use correct hex values
- Check typography: size, weight, line-height

### Backend Integration Issues Later?
- Set `REACT_APP_USE_MOCK_DATA=false`
- Set `REACT_APP_API_URL=http://backend-url/api`
- Verify auth token in localStorage
- Check Network tab for API requests
- Verify CORS configuration on backend

---

## 📞 Need Help?

1. **Visual Mismatch**: Compare with `screen.png`, check `DESIGN_SYSTEM.md`
2. **Component Specs**: Refer to `DESIGN_SYSTEM.md` component sections
3. **Data Structure**: Check `mockData.js` examples
4. **API Integration**: Read `api.js` and `.instructions.md` backend section
5. **React Issues**: Check `.instructions.md` guidelines and examples

---

## 🎉 Ready to Build!

You now have:
- ✅ Complete design system documentation
- ✅ Mock data ready to use
- ✅ API service layer prepared
- ✅ Component specifications
- ✅ Implementation priority
- ✅ AI agent instructions
- ✅ Design files as reference

**Next Step**: Open `.agent.md` or `.instructions.md` and start building! 🚀

---

**Last Updated**: July 4, 2026
**Frontend Stack**: React 18 + Vite + Tailwind CSS
**Status**: Ready for Development ✅
