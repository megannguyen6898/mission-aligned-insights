# UI Revamp - Design System Documentation

## Overview
This redesign implements a cohesive design system focused on social impact, using cyan (#06B6D4) and amber (#FBBF24) as primary brand colors with slate neutrals.

## Running the Project

```bash
cd frontend
npm install
npm run dev
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

### Spacing & Layout
- **Border Radius**: 1rem (16px) base, up to 2xl for cards
- **Shadows**: Soft, subtle elevation (soft-shadow, soft-shadow-lg)
- **Whitespace**: Generous padding and gaps (p-6, p-8, space-y-6)

## Reusable Components

### Layout
- **AppShell** (`/components/layout/AppShell.tsx`): Main layout with collapsible sidebar
- **WorkflowNav** (`/components/sidebar/WorkflowNav.tsx`): Navigation with Upload → Mapping → Dashboard → Reports → Settings

### Common Components
- **KpiCard** (`/components/common/KpiCard.tsx`): Large numeral cards with trends
- **ChartBlock** (`/components/common/ChartBlock.tsx`): Chart containers with optional AI narratives

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

## CSS Utilities

```css
.soft-shadow         /* Subtle card elevation */
.soft-shadow-lg      /* More prominent shadow */
.gradient-ai         /* AI narrative gradient background */
```

## Accessibility
- WCAG AA contrast ratios on all text
- Visible focus outlines (ring-2 ring-primary)
- Keyboard navigation support
- Semantic HTML structure

## Next Steps
- [x] Implement Spaces tree component for navigating organizations → programs → datasets
- [x] Add File Preview drawer with quick metadata and text previews
- [x] Connect AI drawer to the mission-aligned AI service endpoint
- [x] Add responsive mobile and tablet layouts for the application shell
- Continue collecting feedback from program teams to refine data taxonomy and AI prompts
