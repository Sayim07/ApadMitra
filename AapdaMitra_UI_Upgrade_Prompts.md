# 🎨 AapdaMitra 2.0 — Complete UI Upgrade Prompts

> **Rule:** These prompts upgrade ONLY the visual layer. No API calls, no agent logic, no Firebase queries,
> no routing structure should be touched. Only replace JSX markup, CSS classes, and styling.
> All `onClick`, `onSubmit`, `useEffect`, `useState`, `axios` calls remain exactly as they are.

---

## 🎨 Design System First — Read Before Any Prompt

**Theme: "Emergency Intelligence"**
- Dark, serious, high-contrast — like a war room meets a tech startup
- Primary background: `#080B14` (near black with blue tint)
- Secondary surface: `#0D1117`
- Card surface: `#111827`
- Border color: `#1F2937`
- Primary accent: `#E63946` (emergency red)
- Secondary accent: `#FF6B35` (alert orange)
- Success: `#22C55E`
- Warning: `#FBBF24`
- Text primary: `#F9FAFB`
- Text secondary: `#9CA3AF`
- Text muted: `#4B5563`

**Typography:**
- Display / Hero: `Syne` (Google Font) — bold, geometric, futuristic
- Body: `DM Sans` (Google Font) — clean, readable, modern
- Monospace / Data: `JetBrains Mono` — for scores, timestamps, codes
- Import in index.html:
  `https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap`

**Global CSS variables** — add to frontend/src/index.css:
```css
:root {
  --bg-primary: #080B14;
  --bg-secondary: #0D1117;
  --bg-card: #111827;
  --bg-card-hover: #1a2235;
  --border: #1F2937;
  --border-bright: #374151;
  --accent-red: #E63946;
  --accent-red-glow: rgba(230, 57, 70, 0.25);
  --accent-orange: #FF6B35;
  --accent-blue: #3B82F6;
  --severity-red: #EF4444;
  --severity-yellow: #FBBF24;
  --severity-green: #22C55E;
  --text-primary: #F9FAFB;
  --text-secondary: #9CA3AF;
  --text-muted: #4B5563;
  --font-display: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-glow-red: 0 0 30px rgba(230, 57, 70, 0.3);
}

* { box-sizing: border-box; }
body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4 { font-family: var(--font-display); }
```

---

## Prompt 1 — Global Reusable Components

```
Create a design system component library for AapdaMitra in frontend/src/components/ui/.
These are purely visual wrapper components — they accept children and className props and
DO NOT contain any business logic.

1. frontend/src/components/ui/Button.jsx
   Variants: primary | secondary | danger | ghost | outline
   Sizes: sm | md | lg
   States: loading (spinner), disabled

   Primary: bg #E63946, white text, hover: brighter + slight glow shadow
   Secondary: bg #1F2937, white text
   Danger: bg transparent, border #EF4444, text #EF4444, hover: fill red
   Ghost: transparent, hover: bg #1F2937
   
   Add subtle scale(0.97) on active. Add 200ms transition on all.
   Loading state: replace text with spinning circle SVG icon.

   Usage: <Button variant="primary" size="lg" loading={isSubmitting} onClick={handleSubmit}>
            Report Emergency
          </Button>

2. frontend/src/components/ui/Card.jsx
   Variants: default | elevated | bordered | glass
   
   Default: bg #111827, border 1px #1F2937, border-radius 12px
   Elevated: same + box-shadow 0 4px 24px rgba(0,0,0,0.4)
   Bordered: 1px solid #374151
   Glass: bg rgba(255,255,255,0.03), backdrop-filter blur(20px), border rgba(255,255,255,0.08)
   
   Add hover state on elevated: translateY(-2px) + slightly brighter border

3. frontend/src/components/ui/Badge.jsx
   Variants: red | yellow | green | blue | grey
   Sizes: sm | md
   
   Each has matching bg (low opacity), border, and text color.
   RED: bg rgba(239,68,68,0.15), border rgba(239,68,68,0.4), text #FCA5A5
   YELLOW: bg rgba(251,191,36,0.15), border rgba(251,191,36,0.4), text #FDE68A
   GREEN: bg rgba(34,197,94,0.15), border rgba(34,197,94,0.4), text #86EFAC
   BLUE: bg rgba(59,130,246,0.15), border rgba(59,130,246,0.4), text #93C5FD
   
   Add pulsing ring animation for RED badge when pulse prop is true.

4. frontend/src/components/ui/Input.jsx
   Dark styled: bg #0D1117, border #1F2937, text white
   Focus: border #E63946, ring rgba(230,57,70,0.2)
   Error state: border #EF4444, show error message below
   With icon support: left icon and right icon slots

5. frontend/src/components/ui/Navbar.jsx
   Fixed top, height 64px
   bg rgba(8,11,20,0.85), backdrop-filter blur(20px)
   Border-bottom 1px solid rgba(255,255,255,0.06)
   Logo: "⚡ AapdaMitra" in Syne font, red accent on "Aapda"
   
   Desktop: logo | nav links | CTA button
   Mobile: logo | hamburger menu (slide-down drawer)
   
   Active link: red underline indicator
   Scroll effect: slightly increase bg opacity after scrolling 50px

6. frontend/src/components/ui/StatCard.jsx
   For dashboard stats: icon | label | value | trend
   bg #111827, border #1F2937
   Value in JetBrains Mono font, large (2rem)
   Trend: green arrow up / red arrow down with percentage
   
   Animate value counting up on mount (count from 0 to final value over 1.2 seconds)
```

---

## Prompt 2 — Landing Page (Complete Redesign)

```
Completely redesign frontend/src/pages/LandingPage.jsx.
Keep all existing data fetching (fetch from /dashboard/summary) exactly as-is.
Only replace the JSX and styling.

SECTION 1 — HERO (full viewport height):

Background: #080B14 with subtle animated gradient mesh:
  Use CSS @keyframes to slowly animate 3 radial gradients in the background:
  - One red glow (rgba(230,57,70,0.12)) slowly drifting top-left
  - One orange glow (rgba(255,107,53,0.08)) drifting bottom-right
  - One blue glow (rgba(59,130,246,0.06)) in center
  Animation duration: 12s, ease-in-out, infinite alternate

Top-left: small pill badge — "🔴 LIVE MONITORING ACTIVE" with pulsing red dot

Center layout (max-width 900px, centered):
  - Overline text: "AI-POWERED DISASTER INTELLIGENCE" — small, letter-spacing 0.15em, color #E63946, font DM Sans
  - H1 (Syne 800, 80px desktop / 44px mobile):
    Line 1: "Detect Disasters."
    Line 2: "Save Lives." — the word "Lives" in #E63946
  - Subheading (DM Sans, 20px, #9CA3AF, max-width 560px):
    "AapdaMitra is an autonomous AI platform that scans social media, citizen reports, and
    weather APIs to verify disasters in real time and alert authorities in under 30 seconds."

  - Live stats row (3 numbers side by side, JetBrains Mono):
    [Active Incidents: {count}] [Alerts Sent Today: {count}] [Avg Response: {time}min]
    Each in a small glass card. Numbers animate counting up on load.
    Pull from /dashboard/summary.

  - Two CTA buttons:
    Primary: "🚨 Report Emergency" → /report (large, red bg)
    Secondary: "Authority Login →" → /auth (outline, white)
    Gap between: 16px

  - Scroll indicator: small animated down-arrow at bottom of hero

SECTION 2 — HOW IT WORKS (dark section):

Title: "From Tweet to Rescue" (Syne 700, centered)
Subtitle: "Five AI agents working in milliseconds, not hours"

Show 5 agent steps as a horizontal timeline (desktop) / vertical (mobile):
Each step: numbered circle (1-5) → connector line → card
  1. 🛰️ Monitor — "Scans 10+ sources continuously"
  2. ✅ Verify — "Cross-checks with weather & seismic APIs"
  3. 🚨 Prioritize — "Assigns RED/YELLOW/GREEN severity"
  4. 🌐 Generate — "Creates multilingual alerts via Gemini AI"
  5. 📡 Dispatch — "SMS · WhatsApp · Email · Voice · Dashboard"

Connector lines between cards. Active step glows red (animate cycling through them).
Card hover: lift + red border glow.

SECTION 3 — WHY AAPDA MITRA (comparison table):

Title: "Why AapdaMitra?" (Syne 700, centered)
Subtitle: "Traditional disaster systems are failing. We built something better."

Render a styled comparison table (NOT a plain HTML table):

  Column 1: Feature (left-aligned)
  Column 2: ❌ Traditional Systems (header: bg #1a0a0a, text #ef4444)
  Column 3: ✅ AapdaMitra AI (header: bg #0a1a0a, text #22c55e)

  Rows:
  | Disaster Verification     | Manual, 2-4 hours          | AI-automated, under 60 sec    |
  | Fake News Filtering       | None                       | AI confidence scoring (0-100) |
  | Emergency Alerts          | Phone calls & manual SMS   | 5 channels simultaneously     |
  | Multilingual Support      | English only               | English, Hindi, Bengali+      |
  | Authority Notification    | Assumed (no confirmation)  | AI voice call + acknowledgment|
  | Rescue Prioritization     | Gut feeling                | Data-driven severity scoring  |
  | Citizen Reporting         | Call a helpline            | One-tap SOS with GPS          |
  | Response Coordination     | Hours of back-and-forth    | Unified real-time dashboard   |
  | Misinformation Control    | None                       | Weather API cross-verification|
  | Scale                     | 1 operator per call        | 1,000+ simultaneous alerts    |

  Styling:
  - Alternating row backgrounds (#111827 / #0D1117)
  - ❌ cells: text #FCA5A5, subtle red tint
  - ✅ cells: text #86EFAC, subtle green tint
  - Feature column: bold, white
  - Hover row: highlight entire row border in #374151
  - Table has rounded corners, overflow hidden
  - Add entrance animation: rows fade+slide in with staggered delay

SECTION 4 — DISASTER TYPES (icon grid):

Title: "Built for Every Disaster"
6 cards in a 3x2 grid:
  🌊 Floods | 🌀 Cyclones | 🏔️ Earthquakes | ⛰️ Landslides | 🔥 Wildfires | ⚡ Any Emergency

Each card: large emoji, name, short description. Hover: card lifts + colored glow matching disaster type.

SECTION 5 — CTA BANNER (full width):

Dark red gradient bg: linear-gradient(135deg, #1a0608 0%, #0D1117 100%)
Border top: 1px solid rgba(230,57,70,0.3)

Large centered text: "Every second you wait is a life at risk."
Subtext: "Join governments, NGOs, and emergency teams using AapdaMitra."
CTA: "Get Started Free" button → /auth

SECTION 6 — FOOTER:

bg #0D1117, border-top #1F2937
Columns: Logo + tagline | Product links | Emergency links | Contact
Bottom row: copyright + "Built with ❤️ for disaster response"
```

---

## Prompt 3 — Auth / Login Page

```
Redesign frontend/src/pages/AuthPage.jsx.
Keep all Firebase authentication logic exactly as-is (signInWithEmailAndPassword,
GoogleAuthProvider, createUserWithEmailAndPassword, onAuthStateChanged, navigate calls).
Only replace the visual layout.

Layout: Split screen (desktop) / stacked (mobile)

LEFT PANEL (50%, hidden on mobile):
  bg: linear-gradient(160deg, #0D1117 0%, #080B14 100%)
  
  Top-left: "⚡ AapdaMitra" logo (Syne font)
  
  Center content:
    - Large quote in Syne font (italic):
      "In disaster response, every second counts.
       AapdaMitra makes seconds matter."
    
    - Below quote: 3 trust indicators as small pills:
      🔴 Live Monitoring Active
      🛡️ AI-Verified Reports Only  
      📡 5-Channel Alert System
    
    - Bottom: animated stats cycling through:
      "127 incidents verified this month"
      "< 30 second average response time"
      "3 languages, 5 alert channels"
      (auto-cycle every 3 seconds with fade transition)
  
  Decorative: subtle grid pattern overlay (CSS background-image with 1px lines)
  Add slow-moving red glow orb animation in bottom-left corner

RIGHT PANEL (50%):
  bg: #080B14
  Centered card (max-width 420px):

  TABS: "Sign In" | "Create Account"
  Tab indicator: sliding red underline (CSS transition)
  
  SIGN IN FORM:
    - Heading: "Welcome back" (Syne 700, 28px)
    - Subtext: "Sign in to access the emergency dashboard"
    
    - Google Sign-In button (full width):
      bg #111827, border #374151, white text
      Google SVG icon on left
      Text: "Continue with Google"
      Hover: border #E63946
    
    - Divider: "— or sign in with email —" (small, muted)
    
    - Email input (use Input component from Prompt 1)
    - Password input with show/hide toggle eye icon
    - "Forgot password?" link (right-aligned, small, red)
    
    - Sign In button (full width, primary red)
    - Loading state: show spinner inside button
    - Error state: red shake animation on form + error message below button
  
  REGISTER FORM (shown when "Create Account" tab active):
    - Heading: "Join AapdaMitra"
    - Subtext: "Create your emergency response account"
    
    - Full name input
    - Email input
    - Password input
    - Confirm password input
    - Role selector dropdown (styled dark):
      Options: Citizen | Ward Officer | Rescue Team | District Authority
    - District input (text, shown only for non-citizen roles)
    
    - Register button (full width, primary red)
    - Terms text: "By registering you agree to our Terms of Service"
  
  Both forms: smooth fade transition when switching tabs.
  
  AFTER AUTH SUCCESS:
    Keep existing navigate('/dashboard') or navigate('/') logic exactly as-is.
```

---

## Prompt 4 — Dashboard Shell Redesign

```
Redesign the dashboard layout shell in frontend/src/pages/DashboardPage.jsx.
Keep all data fetching, WebSocket/Firebase subscriptions, routing, and state management
exactly as-is. Only replace layout and styling.

TOP NAVBAR (fixed, 64px height):
  bg: rgba(8,11,20,0.9), backdrop-filter: blur(20px)
  Border-bottom: 1px solid #1F2937

  Left: "⚡ AapdaMitra" logo
  
  Center: System status indicator:
    - Green pulsing dot + "MONITORING ACTIVE" text (if system ok)
    - Red pulsing dot + "⚠ ACTIVE EMERGENCY" (if any RED incident unacknowledged)
    - Text in JetBrains Mono, small caps
  
  Right side:
    - Active incidents badge: red pill showing count of RED incidents
    - User avatar circle with initials
    - User name + role badge
    - Dropdown: Profile | Settings | Sign Out
  
  RED ALERT BANNER (conditional — show below navbar if any RED + unacknowledged):
    Full width, bg linear-gradient(90deg, #7f0d0d, #1a0608)
    Animated left-to-right scan line effect (CSS @keyframes)
    Text: "⚠ CRITICAL ALERT — {location} — Unacknowledged — [View & Acknowledge →]"
    Text pulses slightly

LEFT SIDEBAR (240px fixed, full height):
  bg: #0D1117, border-right: 1px solid #1F2937
  
  Nav sections:
  
  OVERVIEW:
    🗺️  Live Map
    🚨  Active Incidents  [count badge]
    📊  Analytics
  
  MANAGEMENT:
    📋  Alert History
    👥  Authority Contacts
    ⚙️  Settings
  
  Each nav item:
    - Icon (20px) + label
    - Active state: bg rgba(230,57,70,0.1), left border 3px solid #E63946, text white
    - Hover: bg #111827
    - Transition: 150ms
  
  Bottom of sidebar:
    Small card showing: "System Health"
    - API: ✅ Online
    - Firebase: ✅ Connected
    - Agents: ✅ Running
    Refresh every 60s.

MAIN CONTENT AREA:
  Padding: 24px
  Page title area at top of each page:
    - Breadcrumb: Dashboard > [current page]
    - Page title (Syne 700, 28px)
    - Subtitle text

RIGHT PANEL (320px, collapsible):
  bg: #0D1117, border-left: 1px solid #1F2937
  Title: "Live Feed" with red pulsing dot
  
  Scrollable list of real-time incidents from Firebase.
  Each item: left severity border | type+location | time ago | severity badge
  
  Collapse button: arrow icon to hide/show panel
  When collapsed: thin 48px strip with just the collapse arrow visible

OVERALL GRID:
  display: grid
  grid-template-columns: 240px 1fr 320px (collapsed: 240px 1fr 48px)
  height: 100vh
  
  Smooth transition on right panel collapse: 300ms ease
```

---

## Prompt 5 — Dashboard Home Stats Page

```
Redesign the main dashboard stats view (the page shown at /dashboard).
Keep all API calls to /dashboard/summary exactly as-is. Only replace the UI.

Layout: responsive grid of stat cards + charts

ROW 1 — Hero Stats (4 stat cards using StatCard component from Prompt 1):
  1. 🔴 Active RED Incidents — value from summary.by_severity.red
  2. 🟡 Active YELLOW Incidents — summary.by_severity.yellow
  3. ⚡ Avg Response Time — summary.avg_response_time_minutes + "min"
  4. ✅ Acknowledgment Rate — summary.acknowledgment_rate + "%"

Each card: 280px min-width, full bleed color accent on top border.
RED card: top border 3px solid #EF4444, number in red
YELLOW card: top border 3px solid #FBBF24, number in yellow
RESPONSE card: top border 3px solid #3B82F6
ACK card: top border 3px solid #22C55E

ROW 2 — Verification Breakdown (pie chart + legend):
  Use Recharts PieChart.
  Data: verified (green #22C55E) | suspicious (yellow #FBBF24) | fake (red #EF4444)
  Values from summary.verification_stats
  
  Custom legend on right side: each entry shows colored dot + label + count + percentage pill
  Chart has inner label showing total incidents count.
  Animate on mount: pie segments draw in with 800ms transition.

ROW 3 — Incidents By Type (horizontal bar chart):
  Recharts BarChart horizontal layout.
  Bar color: gradient from #E63946 to #FF6B35
  Each bar has value label on right.
  X axis: count, Y axis: disaster types
  Tooltip: dark bg #111827, white text

ROW 4 — Recent Activity Timeline:
  List of last 10 events (verified incidents + dispatched alerts) in chronological order.
  Each row: colored left dot | time (JetBrains Mono) | event description | badge
  Alternating bg #111827 / #0D1117
  
All charts: bg #111827, border #1F2937, border-radius 12px, padding 24px.
Chart title in Syne 600.
```

---

## Prompt 6 — Incidents List Page Redesign

```
Redesign frontend/src/pages/IncidentsPage.jsx.
Keep all API calls (GET /incidents with filters), pagination, and navigation exactly as-is.

HEADER ROW:
  Left: Page title "Active Incidents" + total count badge
  Right: 
    - Filter bar: severity pills (ALL | 🔴 RED | 🟡 YELLOW | 🟢 GREEN)
    - Disaster type filter dropdown
    - District filter input
    - Search input (search by location)
  
  Active filters shown as removable chips below filter bar.

INCIDENT CARDS GRID (2 columns desktop, 1 mobile):

Each IncidentCard (redesign frontend/src/components/incidents/IncidentCard.jsx):

  Card structure:
    - Top strip: full-width 4px solid bar in severity color (RED/YELLOW/GREEN)
    - Card bg: #111827, hover: #1a2235 + border #374151
    - Transition: 200ms
  
  Card header (flex, space-between):
    Left: disaster type icon (emoji, 24px) + disaster type label (Syne 600)
    Right: severity badge (Badge component)
  
  Location row:
    📍 {location_name} — bold, white
    Below: {time ago} in muted text, JetBrains Mono
  
  Verification row (flex):
    Left: "Verification" label (small, muted)
    Right: colored progress bar (0-100) + score number
    Color: green if >80, yellow if 50-79, red if <50
  
  Footer row (flex, space-between):
    Left: source type chip (small, grey)
    Right: two buttons:
      - "View Details" → ghost button
      - "Acknowledge" → small danger outline button (only if unacknowledged)
  
  RED+unacknowledged cards: add subtle pulsing glow border animation

EMPTY STATE (when no incidents match filter):
  Centered: 🛡️ large icon + "No incidents match your filters" + "Clear filters" button

LOADING STATE:
  Skeleton cards: 4 placeholder cards with shimmer animation
  Shimmer: CSS gradient animation left to right, #1F2937 → #374151 → #1F2937
```

---

## Prompt 7 — Incident Detail Page Redesign

```
Redesign frontend/src/pages/IncidentDetailPage.jsx.
Keep all API calls, Firebase listeners, acknowledge handler, and state management.
Only replace the visual layout.

TOP SECTION — Incident Header:
  Full-width header card with left border 6px in severity color.
  
  Row 1: Back button ← | Breadcrumb | Incident ID (JetBrains Mono, small)
  Row 2: Large disaster emoji (48px) | H1 location name (Syne 700) | Severity badge (large) | Verification badge
  Row 3: Meta pills: source type | reported time | district | coordinates

ACKNOWLEDGE BANNER (shown if not acknowledged):
  Full-width, bg rgba(230,57,70,0.1), border 1px rgba(230,57,70,0.3)
  Left: ⚠️ "This RED alert requires acknowledgment"
  Right: Large "ACKNOWLEDGE & DISPATCH" button (bg #E63946, pulse animation)
  On click: existing handler, show confirmation + success state

TWO COLUMN LAYOUT:

LEFT COLUMN (60%):

  CARD 1 — Incident Description:
    Title: "Report Details"
    Raw text in italic, quote-style block
    Source type badge
    Media thumbnails row (if media_urls exist): clickable, opens lightbox

  CARD 2 — Verification Score (redesign VerificationScoreCard):
    Header row: "AI Verification" title | status badge
    
    Big circular gauge:
      SVG circle, 140px diameter
      Stroke color based on score (red/yellow/green)
      Score number in center (JetBrains Mono, 2.5rem)
      "/ 100" below in muted
      Animated: stroke draws from 0 to score on mount (1s transition)
    
    Factor progress bars (5 factors):
      Each: label | bar | score/max
      Bar fill animation on mount
      Color matches score percentage
    
    Reasoning text block: 
      bg #0D1117, border-left 3px solid #3B82F6
      Italic AI-generated explanation text

  CARD 3 — Location Map:
    Small Leaflet map (300px height)
    Red pulsing marker at incident coordinates
    Non-interactive (scrollWheelZoom=false, dragging=false)
    "Open full map →" link bottom-right

RIGHT COLUMN (40%):

  CARD 4 — Priority Score:
    Large number + "/100" + severity label
    5 factor rows: label | score/max (table style)
    Estimated population affected (bold)

  CARD 5 — Alert Dispatch Status:
    Title: "Dispatch Status"
    Per-channel rows (5 channels):
      Channel icon + name | status badge | "X contacts" | timestamp
      
      Status badges:
        ✅ Delivered — green
        🔄 Sending — blue animated
        ❌ Failed — red
        ⏳ Pending — yellow
    
    "Re-dispatch" button at bottom (ghost, small)

  CARD 6 — Generated Alerts:
    Language tab switcher: EN | HI | BN
    Sliding underline tab indicator
    Alert text in speech-bubble style box per language
    Character count shown (for SMS length awareness)

  CARD 7 — Timeline:
    Vertical timeline of all events for this incident:
    ○ Reported (T+0)
    ○ Verification started
    ○ Verified (score: 92)
    ○ Severity assigned: RED
    ○ Alerts generated
    ○ Dispatched: 5 channels
    ○ Acknowledged by: [name]
    
    Each node: dot in severity color | time (JetBrains Mono) | label
```

---

## Prompt 8 — Citizen Report Form Redesign

```
Redesign frontend/src/pages/CitizenReportPage.jsx.
Keep all form state, validation logic, geolocation API calls, Cloudinary upload,
POST to /incidents, and success/error handling exactly as-is.

PAGE LAYOUT:
  bg: #080B14
  Centered container, max-width 680px, padding top 80px

  Header:
    Red overline: "EMERGENCY REPORT"
    H1 (Syne 700): "Report a Disaster"
    Subtext: "Your report is AI-verified and sent to authorities in under 60 seconds."

PROGRESS INDICATOR (top of form):
  3 step indicators in a row connected by lines:
    Step 1: "What Happened" 
    Step 2: "Where"
    Step 3: "Evidence"
  
  Active step: filled red circle + bold label
  Completed step: checkmark circle (green) + muted label  
  Future step: empty circle + muted label
  Connecting lines: fill with color as steps complete (CSS transition)

STEP 1 — What Happened:
  Card with glass effect (bg rgba(255,255,255,0.02), backdrop-filter blur)
  
  Disaster Type selector (NOT a boring dropdown):
    Grid of 6 large clickable cards (3x2):
    🌊 Flood | 🌀 Cyclone | 🏔️ Earthquake | ⛰️ Landslide | 🔥 Wildfire | ⚡ Other
    
    Each card: emoji (40px) + label, bg #111827, border #1F2937
    Selected: border #E63946, bg rgba(230,57,70,0.1), subtle scale(1.02)
    Hover: bg #1a2235

  Description textarea:
    Styled dark input, placeholder: "Describe what you see. Be specific about location, water levels, number of people affected..."
    Character counter bottom-right (green when enough, red when too short)
    Min 20 chars validation.

  How severe: 3 button toggle:
    [Mild] [Moderate] [Severe]
    Selected state: filled in matching color (yellow/orange/red)

  "Next →" button (right-aligned, primary)

STEP 2 — Where:
  Card same style as Step 1
  
  Auto-detect button (full width, outlined):
    📍 "Detect My Location" 
    Loading state: spinning icon + "Getting GPS..."
    Success state: green + coordinates shown
    Error state: red + "Could not detect location"
  
  Divider: "— or enter manually —"
  
  Address input with search icon left
  Map preview (small Leaflet, 200px): shows pin when location selected
  
  Location confirmed state: green card showing location name + coordinates

  "← Back" | "Next →" buttons

STEP 3 — Evidence:
  File upload area (drag and drop):
    Dashed border: 2px dashed #374151
    Center: upload icon + "Drop photos or videos here" + "or click to browse"
    Accepted: image/*, video/*
    Max 5 files, 10MB each
    
    Hover state: border #E63946, bg rgba(230,57,70,0.05)
    File preview thumbnails grid when files selected
    Each thumbnail: image preview + remove (×) button + file size label
  
  Contact number input (optional):
    Phone icon left + input
    "Optional — for follow-up only" hint

  Submit button (full width, large, primary red):
    Text: "Submit Emergency Report"
    Loading: "Submitting... AI agents activated"
    
  Disclaimer text below: "🔒 Your location is only used for emergency response and is never sold."

SUCCESS STATE (replace form after submission):
  Centered animation: checkmark circle drawing in (CSS stroke animation)
  Title: "Report Submitted ✅"
  Tracking ID: large monospace token
  "AI verification typically completes in under 60 seconds"
  Two CTAs: "Track This Report" | "Back to Home"

ERROR STATE:
  Red shake animation on form
  Error card at top with specific message
```

---

## Prompt 9 — SOS Page Redesign

```
Redesign frontend/src/pages/SOSPage.jsx.
Keep ALL existing logic: geolocation, POST /incidents/sos, success state, error state.
Only replace the visual.

Full screen, bg #080B14.

BEFORE TAP STATE:
  
  Center of screen:
  
  Animated ring pulses:
    3 concentric circles that pulse outward from center (CSS @keyframes):
    - Inner: 180px, bg rgba(230,57,70,0.3)
    - Middle: 240px, bg rgba(230,57,70,0.15)  
    - Outer: 300px, bg rgba(230,57,70,0.05)
    All pulsing with 2s infinite ease-out animation
    
  SOS Button (circle, 160px diameter):
    bg: linear-gradient(145deg, #E63946, #c0392b)
    box-shadow: 0 0 40px rgba(230,57,70,0.5), 0 0 80px rgba(230,57,70,0.2)
    Text: "SOS" in Syne 800, white, 36px
    
    Tap/click: scale(0.93) active state
    Hover: box-shadow increases intensity
  
  Below button:
    "Tap to send your location and alert authorities"
    Muted, DM Sans
  
  Bottom section (emergency contacts):
    3 cards in a row:
    📞 112 Emergency | 🌊 1077 Flood | 🚁 NDRF: 011-24363260
    Each: dark card, click-to-call tel: link

LOADING STATE (after tap):
  Replace pulsing rings with spinner
  Text: "📍 Getting your location..."
  Subtext: "Please allow location access"

SUCCESS STATE:
  Replace button with large green checkmark (animated draw-in)
  Title: "🆘 SOS Sent" (Syne 700, white)
  Subtext: "Authorities have been alerted. Help is on the way."
  Report ID in JetBrains Mono pill
  "Your location has been shared with emergency responders"
  
  Subtle green glow background animation

ERROR STATE (location denied):
  Show manual address input form
  Same styling as report form Step 2
  "We couldn't get your GPS. Please enter your location manually."
```

---

## Prompt 10 — Analytics Page Charts Redesign

```
Redesign frontend/src/pages/AnalyticsPage.jsx.
Keep ALL Recharts data fetching from /dashboard/analytics, state management,
and date range filter logic exactly as-is. Only change visual styling of charts.

PAGE HEADER:
  Title: "Analytics" | Date range filter (Today / 7 days / 30 days) — styled as tab pills

Apply these Recharts customizations globally:

Custom Tooltip component for ALL charts:
  const CustomTooltip = ({ active, payload, label }) => (
    <div style={{
      background: '#111827',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '12px 16px',
      fontFamily: 'DM Sans',
      color: '#F9FAFB',
      boxShadow: '0 4px 24px rgba(0,0,0,0.5)'
    }}>
      <p style={{ color: '#9CA3AF', fontSize: '12px', marginBottom: '4px' }}>{label}</p>
      {payload?.map(p => (
        <p key={p.name} style={{ color: p.color, fontFamily: 'JetBrains Mono', margin: 0 }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )

All chart containers: bg #111827, border 1px #1F2937, border-radius 12px, padding 24px
Chart titles: Syne 600, 16px, white
Axis text: DM Sans, 12px, #6B7280
Grid lines: stroke #1F2937

1. "Incidents Over Time" AreaChart:
   - Fill: gradient top #E63946 to transparent
   - Stroke: #E63946
   - Dot: small red circle on data points
   - Reference line at average: dashed, #374151

2. "By Disaster Type" Horizontal BarChart:
   - Bars: fill with unique colors per type:
     Flood: #3B82F6, Cyclone: #8B5CF6, Earthquake: #F59E0B,
     Landslide: #10B981, Wildfire: #EF4444, Other: #6B7280
   - Bar radius: [0, 4, 4, 0]
   - Value labels: show count at end of each bar

3. "Verification Breakdown" PieChart:
   - Verified: #22C55E, Suspicious: #FBBF24, Fake: #EF4444
   - Inner radius 60, outer radius 100 (donut)
   - Custom legend below: colored dots + label + count + percentage
   - Center label: total count

4. "Severity Distribution" PieChart:
   - RED: #EF4444, YELLOW: #FBBF24, GREEN: #22C55E
   - Same donut style

5. "Response Time Trend" LineChart:
   - Actual line: #3B82F6, strokeWidth 2, smooth curve
   - Target line: #E63946 dashed, reference at y=5

6. "Channel Success Rates" Grouped BarChart:
   - Sent bars: #374151
   - Delivered bars: #22C55E
   - Show delivery rate % label above delivered bars

7. "Top Affected Districts" Table:
   - Styled like the comparison table from landing page
   - Alternating rows, severity color on district name
```

---

## Prompt 11 — Live Map Page Redesign

```
Redesign the map page container in frontend/src/pages/MapPage.jsx or wherever the
map is rendered. Keep ALL Leaflet initialization, marker logic, Firebase subscriptions,
heatmap layer, and filter functions exactly as-is. Only replace surrounding UI.

MAP CONTAINER WRAPPER:
  Full viewport height minus navbar (calc(100vh - 64px))
  No padding — map fills the area completely.

TOP OVERLAY BAR (floating over map, top: 16px, centered):
  Glass card: bg rgba(8,11,20,0.85), backdrop-filter blur(20px), border rgba(255,255,255,0.08)
  Border-radius: 50px (pill shape)
  Padding: 8px 16px
  
  Contents (flex row):
    - Severity filter pills: ALL | 🔴 RED | 🟡 YELLOW | 🟢 GREEN
    - Divider
    - Layer toggle buttons: Incidents | Heatmap
    - Divider  
    - District search input (small, dark)
    - Locate Me button (icon only)

LEFT OVERLAY PANEL (floating, left: 16px, top: 80px):
  Glass card, width 280px
  
  Title: "Live Incidents" + count badge
  Scrollable list (max-height 400px):
    Each item: colored dot | location | time ago
    Hover: highlight, cursor pointer
    Click: map flies to that incident
  
  Footer: "Updated {seconds} ago" + refresh indicator

BOTTOM OVERLAY BAR (floating over map, bottom: 16px, centered):
  Glass pill card
  3 live stats: 🔴 {n} Critical  |  🟡 {n} Moderate  |  🟢 {n} Safe
  Numbers in JetBrains Mono

CUSTOM LEAFLET MARKER STYLES (inject via leaflet CSS overrides):
  RED markers: red circle with outer pulsing ring animation
  YELLOW markers: orange circle
  GREEN markers: green circle
  Unverified: grey dashed circle
  All markers: drop shadow

MAP TILES:
  Switch to CartoDB Dark tiles for a dark map theme:
  URL: https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png
  Attribution: keep CartoDB attribution
  (This makes the map dark — matching the dashboard theme perfectly)
```

---

## Prompt 12 — Final Polish Pass

```
Final UI polish pass for AapdaMitra. Apply these global improvements across all pages.
Make ZERO changes to any logic, API calls, or state management.

1. PAGE TRANSITIONS:
   In App.jsx, wrap routes with a fade transition:
   Each page fades in over 200ms on route change.
   Use CSS: 
   .page-enter { opacity: 0; transform: translateY(8px); }
   .page-enter-active { opacity: 1; transform: translateY(0); transition: 200ms ease; }

2. LOADING STATES:
   Create frontend/src/components/ui/Skeleton.jsx
   A shimmer placeholder component with CSS animation.
   Apply to: incident cards, stat cards, chart containers while data loads.
   Shimmer: background: linear-gradient(90deg, #111827 0%, #1F2937 50%, #111827 100%)
   background-size: 200% auto; animation: shimmer 1.5s infinite linear;

3. TOAST NOTIFICATIONS:
   Create frontend/src/components/ui/Toast.jsx
   Position: top-right, below navbar
   Types: success (green) | error (red) | info (blue) | warning (yellow)
   
   Each toast: dark bg #111827 + left colored border + icon + message
   Animation: slide in from right, auto-dismiss after 4s
   
   Replace ALL existing alert() calls and inline error messages with toast notifications.
   Create a useToast() hook in src/hooks/useToast.js

4. EMPTY STATES:
   Create a reusable EmptyState component:
   Large icon (emoji, 48px) + title + subtitle + optional CTA button
   Centered, muted colors.
   Apply to: incidents list (no results), alerts list, analytics (no data).

5. MOBILE SIDEBAR:
   Dashboard sidebar on mobile: 
   Hidden by default. Hamburger button in navbar opens it as slide-over drawer.
   Overlay: bg rgba(0,0,0,0.6) behind drawer.
   Drawer slides in from left, 280px wide.
   Close on overlay click or close button.

6. SCROLLBAR STYLING (webkit):
   ::-webkit-scrollbar { width: 6px; }
   ::-webkit-scrollbar-track { background: #0D1117; }
   ::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
   ::-webkit-scrollbar-thumb:hover { background: #4B5563; }

7. FOCUS STATES:
   All interactive elements: outline: 2px solid #E63946; outline-offset: 2px;
   Replace default browser blue focus ring globally.

8. FAVICON + META:
   Update public/index.html:
   <title>AapdaMitra — AI Disaster Intelligence</title>
   <meta name="theme-color" content="#080B14">
   <meta name="description" content="AI-powered disaster intelligence platform. Real-time monitoring, verification, and emergency alerts.">
   Add emoji favicon: ⚡ or 🌪️ (SVG favicon with emoji)
```

---

## 📌 Implementation Order

Follow this exact order to avoid breaking anything:

| Step | Prompt | Why first |
|---|---|---|
| 1 | Global CSS variables (top of this doc) | Everything depends on CSS vars |
| 2 | Prompt 1 — UI component library | All pages use these components |
| 3 | Prompt 2 — Landing Page | No auth dependency, easiest to verify |
| 4 | Prompt 3 — Auth Page | Needed before testing dashboard |
| 5 | Prompt 4 — Dashboard Shell | Frame for all dashboard pages |
| 6 | Prompt 5 — Dashboard Stats | First content in dashboard |
| 7 | Prompt 6 — Incidents List | High visibility page |
| 8 | Prompt 7 — Incident Detail | Complex, do after list works |
| 9 | Prompt 8 — Citizen Report Form | Citizen-facing, test separately |
| 10 | Prompt 9 — SOS Page | Simple, fast |
| 11 | Prompt 10 — Analytics Charts | Visual only |
| 12 | Prompt 11 — Map Redesign | Map tiles change is impactful |
| 13 | Prompt 12 — Final Polish | Last, after all pages look right |

---

*AapdaMitra 2.0 — UI Upgrade Prompts v1.0*
