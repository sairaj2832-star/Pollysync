<!-- Design System Documentation & Component Checklist -->

# PolliSync Design System & Component Reference

## 🎨 Color System

### Main Palette
| Color Name | Hex Value | Usage |
|-----------|-----------|-------|
| Primary | `#006c49` | Main actions, primary buttons, active states |
| Primary Fixed | `#6ffbbe` | Light highlights, active backgrounds |
| Primary Container | `#10b981` | Secondary surfaces, cards |
| Secondary | `#855300` | Secondary actions, badges |
| Secondary Fixed | `#ffddb8` | Light secondary backgrounds |
| Secondary Container | `#fea619` | Secondary accent backgrounds |
| Tertiary | `#b91a24` | Errors, alerts, warnings |
| Tertiary Fixed | `#ffdad7` | Light error backgrounds |
| Background | `#fff8f5` | Page backgrounds |
| Surface | `#fff8f5` | Card backgrounds |
| Surface Variant | `#eae1da` | Disabled states |
| Outline | `#6c7a71` | Borders, dividers |
| Outline Variant | `#bbcabf` | Secondary borders |
| On-Surface | `#1f1b17` | Primary text color |
| On-Surface Variant | `#3c4a42` | Secondary text color |
| Error | `#ba1a1a` | Error states |
| On-Error | `#ffffff` | Text on error backgrounds |

### Text Colors
- **Primary Text**: `#1f1b17` (on-surface)
- **Secondary Text**: `#3c4a42` (on-surface-variant)
- **Disabled Text**: `#ccc` or on-surface with 50% opacity
- **Inverse Text**: `#f9efe8` (for dark backgrounds)

### Background Colors
- **Page**: `#fff8f5`
- **Cards**: `#fff8f5` (same as page or `#fcf2eb` for definition)
- **Button Hover**: Use 10-15% darker primary color
- **Button Disabled**: `#eae1da`

---

## 📝 Typography System

### Font Families
- **Headings**: Geist Sans (100-900 weights)
- **Body**: Inter (400, 500, 600 weights)
- **Labels**: Geist Sans

### Type Scale

| Style | Font | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|------|--------|-------------|---|----------|
| Display | Geist Sans | 48px | 700 | 56px | -0.02em | Hero headings |
| Headline Large | Geist Sans | 24px | 600 | 32px | -0.01em | Page titles |
| Headline Medium | Geist Sans | 20px | 600 | 28px | 0em | Section headers |
| Headline Small | Geist Sans | 20px | 600 | 28px | 0em | Card titles |
| Label Medium | Geist Sans | 14px | 500 | 20px | 0.1em | Labels, buttons |
| Label Small | Geist Sans | 12px | 500 | 16px | 0.5em | Mini labels |
| Body Large | Inter | 16px | 400 | 24px | 0em | Main content |
| Body Medium | Inter | 14px | 400 | 20px | 0.25em | Secondary content |
| Body Small | Inter | 12px | 400 | 16px | 0.4em | Captions, hints |

### Tailwind Implementation
```css
@layer components {
  .text-display {
    @apply font-headline-lg text-[48px] font-bold leading-[56px] -tracking-widest;
  }
  .text-headline-lg {
    @apply font-headline-lg text-[24px] font-semibold leading-[32px] -tracking-tight;
  }
  .text-headline-md {
    @apply font-headline-md text-[20px] font-semibold leading-[28px];
  }
  .text-body-lg {
    @apply font-body-lg text-[16px] font-normal leading-[24px];
  }
  .text-body-md {
    @apply font-body-md text-[14px] font-normal leading-[20px] tracking-[0.25px];
  }
  .text-label-md {
    @apply font-label-md text-[14px] font-medium leading-[20px] tracking-[0.1em];
  }
}
```

---

## 📏 Spacing System

### Spacing Scale
| Token | Value | Tailwind Class |
|-------|-------|---|
| xs | 4px | `p-xs`, `m-xs` |
| sm | 8px | `p-sm`, `m-sm` |
| base | 4px | `p-base`, `m-base` |
| md | 16px | `p-md`, `m-md` |
| lg | 24px | `p-lg`, `m-lg` |
| xl | 32px | `p-xl`, `m-xl` |
| 2xl | 48px | `p-2xl`, `m-2xl` |
| 3xl | 64px | `p-3xl`, `m-3xl` |

### Common Spacing Patterns
- **Component Padding**: 16px (md) to 24px (lg)
- **Section Spacing**: 48px (2xl) to 64px (3xl)
- **Grid Gap**: 16px (md) to 24px (lg)
- **Card Padding**: 24px (lg)

---

## 🎯 Border Radius

| Value | Size | Tailwind Class |
|-------|------|---|
| DEFAULT | 4px | `rounded` |
| lg | 8px | `rounded-lg` |
| xl | 12px | `rounded-xl` |
| full | 9999px | `rounded-full` |

**Usage**:
- **Buttons**: `rounded-xl` (12px)
- **Cards**: `rounded-xl` (12px)
- **Inputs**: `rounded-lg` (8px)
- **Pills/Badges**: `rounded-full`

---

## 🔘 Component Specifications

### Button Component

#### Variants
```
Primary: bg-primary text-white hover:bg-green-700
Secondary: bg-secondary text-white hover:bg-orange-700
Outline: border-2 border-outline text-on-surface hover:bg-surface-variant
Error: bg-error text-white hover:bg-red-700
Ghost: text-primary hover:bg-surface-variant (no bg)
```

#### Sizes
```
Small (sm): px-md py-xs text-sm
Medium (md): px-lg py-md text-body-md ← default
Large (lg): px-xl py-lg text-body-lg
```

#### States
```
Default: Normal styling
Hover: 10-15% darker background
Active: 20% darker background
Disabled: bg-surface-variant text-on-surface-variant cursor-not-allowed
Loading: Show spinner, disable interaction
```

#### Code Template
```jsx
<button className="rounded-xl px-lg py-md bg-primary text-white font-label-md hover:bg-green-700 disabled:bg-surface-variant transition-colors">
  Click me
</button>
```

### Input Component

#### Styling
```
Border: 1px solid outline
Padding: 12px (md)
Border-radius: 8px (lg)
Font: body-md
Placeholder: on-surface-variant at 60% opacity
```

#### States
```
Default: border-outline
Focus: border-2 border-primary
Error: border-2 border-error
Disabled: bg-surface-variant border-outline cursor-not-allowed
```

#### Code Template
```jsx
<input
  type="text"
  placeholder="Enter value"
  className="w-full border border-outline rounded-lg px-md py-xs text-body-md focus:outline-none focus:border-primary focus:border-2 disabled:bg-surface-variant"
/>
```

### Card Component

#### Structure
```
Padding: 24px (lg)
Border-radius: 12px (xl)
Background: surface (#fff8f5)
Border: 1px solid surface-variant or none
Shadow: subtle shadow or none
```

#### Code Template
```jsx
<div className="bg-white rounded-xl p-lg shadow-sm border border-surface-variant">
  {/* Card content */}
</div>
```

### Form Field Component

#### Structure
- Label (14px, 500 weight, gray text)
- Input field (border, padding)
- Helper text (12px, secondary color)
- Error message (12px, red color, only shown on error)

#### Code Template
```jsx
<div className="flex flex-col gap-xs">
  <label className="text-label-md text-on-surface font-medium">Email</label>
  <input
    type="email"
    className="border border-outline rounded-lg px-md py-xs focus:border-primary"
  />
  {error && <span className="text-body-small text-error">{error}</span>}
  {helperText && <span className="text-body-small text-on-surface-variant">{helperText}</span>}
</div>
```

### Metric Card Component

#### Layout
```
Icon (top-left, 24x24px)
Title (14px, secondary color)
Value (24px, bold, primary color)
Benchmark (12px, secondary color)
Optional: Trend indicator (↑/↓ with color)
```

#### Code Template
```jsx
<div className="bg-white rounded-xl p-lg">
  {icon && <div className="mb-md text-3xl">{icon}</div>}
  <h3 className="text-label-md text-on-surface-variant mb-xs">{title}</h3>
  <p className="text-headline-md font-bold text-primary">{value}</p>
  <p className="text-body-small text-on-surface-variant">
    Benchmark: {benchmark}
  </p>
</div>
```

---

## 📊 Chart Components

### Line Chart (for trends)
- **X-axis**: Dates (every 5 days)
- **Y-axis**: Metric values (PSI: 0-1, NDVI: 0-1)
- **Line color**: Primary (#006c49)
- **Area fill**: Primary at 10% opacity
- **Grid lines**: Subtle, outline-variant color
- **Tooltip**: Show on hover with metric value

### Progress Bar
- **Background**: surface-variant
- **Filled**: Primary color
- **Height**: 8px
- **Border-radius**: full (rounded)

### Gauge Chart (for PSI)
- **Background circle**: 360-degree circle
- **Filled arc**: Primary color, diameter 150px
- **Center text**: Large number (0.78)
- **Label**: Subtitle below

---

## 🏗️ Layout Patterns

### Page Layout
```
Header (navigation, 64px height)
  └─ Content area (with gutter: 24px)
    ├─ Page title
    ├─ Filters/Controls (if applicable)
    └─ Main content
Footer (if applicable)
```

### Dashboard Layout
```
Sidebar (optional, 280px width)
Main content
  ├─ Top metrics (4-6 cards in grid)
  ├─ Filter bar
  ├─ Charts section
  └─ Data table/list
```

### Modal/Dialog
```
Overlay: Black 40% opacity
Modal box:
  ├─ Header (title + close button)
  ├─ Content (scrollable if long)
  └─ Actions (buttons aligned right)
```

---

## 🎭 Common Patterns

### Empty State
```
Icon/Illustration
Headline: "No data yet"
Description: Helpful text
CTA Button: "Create first item"
```

### Loading State
```
Skeleton cards or spinner
Placeholder content with pulse animation
"Loading..." text
```

### Error State
```
Error icon (red, #b91a24)
Headline: "Something went wrong"
Error message details
Retry button
```

### Success State
```
Success icon (green, #006c49)
Headline: "Success!"
Confirmation message
Close button
```

---

## 📱 Responsive Breakpoints

### Tailwind Breakpoints
| Breakpoint | Min Width | Tailwind Prefix | Usage |
|-----------|-----------|---|-------|
| Mobile | 0px | (none) | Default styles |
| Tablet | 768px | `md:` | Tablets, small laptops |
| Desktop | 1024px | `lg:` | Large screens |
| Wide | 1280px | `xl:` | Extra wide screens |

### Mobile-First Approach
```jsx
// Default (mobile)
<div className="grid grid-cols-1 gap-md p-md">
  {/* Mobile: 1 column */}
  
  {/* Tablet up */}
  <div className="md:grid md:grid-cols-2 md:gap-lg md:p-lg">
    {/* Tablet: 2 columns */}
    
    {/* Desktop up */}
    <div className="lg:grid lg:grid-cols-4">
      {/* Desktop: 4 columns */}
    </div>
  </div>
</div>
```

---

## ♿ Accessibility Guidelines

### WCAG AA Compliance
- **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Focus Indicators**: Visible focus state on all interactive elements
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Semantic HTML**: Use proper heading hierarchy, `<label>` for inputs, `<button>` for actions

### Implementation
```jsx
// Proper label association
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// ARIA for complex components
<div role="alert" aria-live="polite">
  Error message here
</div>

// Keyboard focus management
<button
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      // Handle action
    }
  }}
  className="focus:outline-none focus:ring-2 focus:ring-primary"
>
  Click or press Enter
</button>
```

---

## 🔄 Animation & Transitions

### Standard Transitions
```css
@layer components {
  .transition-smooth {
    @apply transition-all duration-200 ease-in-out;
  }
}
```

**Usage**:
- Button hover/active states: 200ms ease-in-out
- Modal open/close: 300ms ease-out
- Page navigation: 300ms ease-in-out
- Loading spinners: Continuous rotation

### Disable Animations for Reduced Motion
```jsx
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 📦 Component Checklist

### High Priority (Core UI)
- [ ] Button
- [ ] Input (text, email, password)
- [ ] Select/Dropdown
- [ ] Checkbox
- [ ] Radio Button
- [ ] Card
- [ ] Container/Wrapper

### Medium Priority (Forms)
- [ ] FormField (with label + error)
- [ ] FormGroup
- [ ] Form Validation
- [ ] Switch/Toggle
- [ ] DatePicker

### Medium Priority (Navigation)
- [ ] Navigation Header
- [ ] Footer
- [ ] Breadcrumb
- [ ] Tabs

### Medium Priority (Data Display)
- [ ] Table
- [ ] List
- [ ] Badge
- [ ] Pill/Tag
- [ ] Progress Bar

### Low Priority (Complex)
- [ ] Modal
- [ ] Tooltip
- [ ] Toast/Notification
- [ ] Drawer/Sidebar
- [ ] Carousel

---

## 🚀 Implementation Order

1. **Week 1**: UI Primitives (Button, Input, Select, Card)
2. **Week 2**: Forms (FormField, validation, LoginForm, RegistrationForm)
3. **Week 3**: Pages (HomePage, LoginPage, RegisterPage)
4. **Week 4**: Dashboard (MetricCard, Charts, Filters)
5. **Week 5**: Predictions (PredictionWizard, PredictionHistory)
6. **Week 6**: AI Assistant (ChatInterface)
7. **Week 7**: Polish (Empty states, error handling, responsive)

---

## 🔗 Resources

- **Stitch Files**: `frontend/stitch_pollisync_saas_design_system/`
- **Current Code**: `frontend/src/`
- **Mock Data**: `frontend/src/data/mockData.js`
- **API Service**: `frontend/src/services/api.js`
- **Tailwind Config**: `frontend/tailwind.config.js`
- **Fonts**: Google Fonts (Geist Sans, Inter)

---

## 📞 Support

When building components:
1. Reference the Stitch screen.png for visual design
2. Check code.html for exact styling details
3. Use mockData.js for realistic data
4. Match colors/spacing exactly
5. Test responsive behavior
6. Verify accessibility

**Goal**: Pixel-perfect React implementation of Stitch designs, ready for backend integration.
