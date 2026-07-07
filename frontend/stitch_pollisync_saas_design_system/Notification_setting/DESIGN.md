---
name: Agro-Precision Narrative
colors:
  surface: '#fff8f5'
  surface-dim: '#e2d8d2'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fcf2eb'
  surface-container: '#f6ece6'
  surface-container-high: '#f0e6e0'
  surface-container-highest: '#eae1da'
  on-surface: '#1f1b17'
  on-surface-variant: '#3c4a42'
  inverse-surface: '#342f2b'
  inverse-on-surface: '#f9efe8'
  outline: '#6c7a71'
  outline-variant: '#bbcabf'
  surface-tint: '#006c49'
  primary: '#006c49'
  on-primary: '#ffffff'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#4edea3'
  secondary: '#855300'
  on-secondary: '#ffffff'
  secondary-container: '#fea619'
  on-secondary-container: '#684000'
  tertiary: '#b91a24'
  on-tertiary: '#ffffff'
  tertiary-container: '#ff7a73'
  on-tertiary-container: '#79000e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#ffddb8'
  secondary-fixed-dim: '#ffb95f'
  on-secondary-fixed: '#2a1700'
  on-secondary-fixed-variant: '#653e00'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#fff8f5'
  on-background: '#1f1b17'
  surface-variant: '#eae1da'
typography:
  display:
    fontFamily: Geist Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Geist Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  label-md:
    fontFamily: Geist Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style
The design system for this product is built on the intersection of agricultural vitality and high-performance data science. It balances a premium, reliable SaaS aesthetic with an approachable warmth that resonates with modern growers and agricultural analysts.

The visual style is a blend of **Modern Corporate** and **Minimalism**, heavily influenced by the high-craft execution of industry leaders like Linear and Stripe. It utilizes a restrained color palette, purposeful whitespace, and precision-engineered components to ensure complex pollination data remains legible and actionable. The emotional goal is to evoke a sense of calm authority—transforming volatile environmental data into predictable, trustworthy insights.

## Colors
This design system employs a functional color strategy that prioritizes readability and status indication.

- **Primary (Emerald):** Represents growth, health, and high pollination success. Used for primary actions, success states, and positive growth trends.
- **Accent (Amber):** Used for cautionary data points, active forecasting states, and warnings.
- **Danger (Red):** Reserved for critical risks, pollination failure alerts, and destructive actions.
- **Neutral (Stone/Slate):** Provides the structural framework. In light mode, we use warm Stone tones to feel organic; in dark mode, we transition to cool Slate to maintain high-tech precision.

**Color Application:**
- **Light Mode:** Backgrounds use `#FAFAF9` (Stone-50) with surfaces on `#F5F5F4` (Stone-100).
- **Dark Mode:** Backgrounds use `#0F172A` (Slate-900) with surfaces on `#1E293B` (Slate-800).

## Typography
The typography system uses a dual-font approach to maximize both character and clarity. 

**Geist Sans** is utilized for headlines, labels, and UI elements where precision and a "technical" feel are required. It features a slightly condensed aesthetic that works well for data-dense dashboards.
**Inter** is the workhorse for all body copy and descriptive text, chosen for its unparalleled readability at various scales.

**Scale Usage:**
- Use **Display** for landing page heroes and major dashboard metrics.
- Use **Headline-LG** for page titles.
- Use **Label-SM** for secondary metadata, chart legends, and small badges.

## Layout & Spacing
The spacing system is built on a 4px baseline grid to ensure mathematical harmony across all components. 

**Grid System:**
- **Desktop:** 12-column fluid grid with 24px gutters and 32px margins. 
- **Tablet:** 8-column grid with 16px gutters and 24px margins.
- **Mobile:** 4-column grid with 12px gutters and 16px margins.

**Layout Logic:**
Content is organized in "Slabs" or "Sections" that utilize `spacing-2xl` for vertical separation. Cards within a dashboard should use a consistent `spacing-md` (16px) for internal padding to maintain a clean, breathable feel while maximizing data density.

## Elevation & Depth
This design system uses **Low-contrast outlines** and **Tonal layers** to create depth without the visual clutter of heavy shadows.

- **Level 0 (Base):** Primary background (`#FAFAF9` in light).
- **Level 1 (Cards/Surfaces):** Raised one level using a subtle 1px border (`#E2E8F0` or Stone-200) and a very soft, high-diffusion shadow: `0 1px 3px rgba(0,0,0,0.05)`.
- **Level 2 (Modals/Popovers):** Elevated with a more pronounced border and a double-layered shadow to simulate physical lift. 

In Dark Mode, depth is achieved by lightening the surface hex value (Slate-800 on Slate-900) and using a subtle emerald-tinted outer glow for active elements.

## Shapes
The shape language is intentional and varied to denote hierarchy and function:

- **Standard Elements (Buttons, Inputs):** Use a `8px` radius. This provides a balance between professional geometry and approachable softness.
- **Container Elements (Cards, Panels):** Use a `12px` radius (`rounded-lg`) to clearly frame content.
- **Status Elements (Badges, Tags):** Use a `full` (pill) radius. This distinguishes status information from interactive buttons at a glance.

## Components

### Buttons
- **Primary:** Emerald-500 background, white text. 8px radius. Subtle top-inner highlight for a tactile "pressed" feel.
- **Secondary:** Stone-100 background (Light) or Slate-800 (Dark), 1px border. 
- **Ghost:** No background or border, used for low-priority navigation.

### Input Fields
- 1px border (Stone-200), 8px radius.
- Focused state: Primary Emerald-500 border with a 2px semi-transparent emerald ring (20% opacity).
- Labels are positioned above the field using **Label-MD**.

### Badges (Risk Levels)
- **High Risk:** Danger Red background (10% opacity) with Red-600 text.
- **Optimal:** Primary Emerald background (10% opacity) with Emerald-600 text.
- **Moderate:** Accent Amber background (10% opacity) with Amber-600 text.
- Shape: Always pill-shaped.

### Navigation Patterns
- **Sidebar:** Clean, vertical navigation using `Label-MD` for links. Use subtle icons (20px) with 12px horizontal spacing from text.
- **Breadcrumbs:** Used on all nested forecasting pages to maintain user context.

### Progress Bars
- 8px height, rounded ends. Track is a light neutral; fill color corresponds to the status (Emerald for "Pollination Complete", Amber for "In Progress").

### Tooltips
- Slate-900 background for both light/dark modes. Small 4px radius. Used extensively for explaining complex agricultural metrics.