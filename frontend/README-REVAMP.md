# UI Revamp - Design System Documentation

## Overview
This redesign implements a cohesive design system focused on social impact, using cyan (#06B6D4) and amber (#FBBF24) as primary brand colors with slate neutrals.

## Run & Test

```bash
cd frontend
npm install
npm run dev
# open http://localhost:8080

# optional smoke tests
npm run test
```

## Design Tokens

### Colors
- **Primary (Cyan)**: `hsl(187 85% 43%)` - #06B6D4
- **Accent (Amber)**: `hsl(43 96% 56%)` - #FBBF24
- **Neutrals**: Slate scale (200-700)
- **Borders**: Soft slate with reduced opacity

### Typography
- **Font Family**: Inter (system fallback: system-ui, -apple-system, sans-serif)
- **Line Height**: Generous (1.75 for relaxed reading)
- **Weights**: Regular (400) and Semibold (600)

### Radii, Shadows & Spacing
- **Border Radius**: `--radius: 1rem` (rounded-xl/2xl cards)
- **Shadows**: `--shadow-soft`, `--shadow-medium` for subtle elevation
- **Whitespace**: space-y-6/8, p-6/8, responsive gaps in `PageHeader`

## Reusable Components

### Layout
- **AppShell** (`/components/layout/AppShell.tsx`): Main layout with collapsible sidebar
- **PageHeader** (`/components/layout/PageHeader.tsx`): Consistent heading + actions bar
- **WorkflowNav** (`/components/sidebar/WorkflowNav.tsx`): Navigation with Upload → Mapping → Dashboard → Reports → Settings + Spaces tree

### Common Components
- **KpiCard** (`/components/common/KpiCard.tsx`): Large numerals, soft gradient, trend chip
- **ChartBlock** (`/components/charts/ChartBlock.tsx`): Rounded-2xl chart container with subtle gridlines
- **AINarrativeCard** (`/components/dashboard/AINarrativeCard.tsx`): Gradient AI summary card with Sparkles icon

### Feature Components
- **UploadPanel** (`/components/upload/UploadPanel.tsx`): Drag-drop file upload with progress
- **MappingTable** (`/components/mapping/MappingTable.tsx`): Data mapping with AI confidence badges
- **ReportTabs** (`/components/report/ReportTabs.tsx`): SDG/Ops/SROI tabbed reports
- **AskAIDrawer** (`/components/ai/AskAIDrawer.tsx`): Left-side AI chat drawer

## Design Principles

1. **Social Impact Feel**: Warm, approachable, not corporate
2. **Generous Whitespace**: Breathing room between elements
3. **Soft Shadows**: Subtle elevation without harsh borders
4. **Accessible**: WCAG AA contrast, visible focus states
5. **Semantic Tokens**: All colors via CSS variables, never hardcoded

## CSS Utilities & Variables

`/src/index.css` defines CSS variables that Tailwind consumes:

- `--primary`, `--accent`, `--muted`, `--shadow-soft`, `--shadow-medium`
- `.soft-shadow`, `.soft-shadow-lg`, `.gradient-ai`, `.card-surface`

Use these utilities instead of inline hex values to keep themable.

## Accessibility
- WCAG AA contrast ratios on all text
- Visible focus outlines (ring-2 ring-primary)
- Keyboard navigation support
- Semantic HTML structure

## Smoke Tests

Minimal Vitest smoke tests live in `/src/__tests__/`:
- `mapping.test.tsx` toggles advanced mapping preview
- `dashboard.test.tsx` verifies KPI + AI narrative render

Add more tests as features firm up; keep them UI-level and resilience-focused.

## Next Steps
- [x] Implement Spaces tree component for navigating organizations → programs → datasets
- [x] Add File Preview drawer with quick metadata and text previews
- [x] Connect Ask AI drawer to `/api/v1/ai/ask`
- [x] Add responsive mobile and tablet layouts for the application shell
- [x] Establish smoke tests for dashboard + mapping flows
- Continue collecting feedback from programme teams to refine data taxonomy and AI prompts
