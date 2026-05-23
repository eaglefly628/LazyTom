# Handoff: LazyTom Pomodoro — Visual Redesign

## Overview

LazyTom is a Pomodoro-style focus timer with a Tasks queue, a Points/streak system, and Settings (theme + durations). This handoff redesigns the existing 4-screen experience with a more sophisticated, "anti-procrastinator" visual language: warm cream, deep moss green, terracotta accents, and a serif/sans typographic pairing. The behaviour and information architecture are unchanged — only the visual layer and a few small UX improvements (single-action focus button, "Start with this" task suggestion card).

## About the design files

The files in this bundle are **design references created in HTML/React** — they are prototypes showing the intended look and behaviour, **not production code to copy directly**.

The task is to **recreate these designs in LazyTom's existing codebase** (looks like an Electron-style mac app from the original screenshots) using its established patterns and component library. Lift exact colour values, spacing, typography, and copy from the source — but render them with the app's native UI primitives.

If LazyTom has no design system yet, choose the most appropriate framework for the project (React + Tailwind, SwiftUI, etc.) and implement the designs there.

## Fidelity

**High-fidelity (hifi).** Pixel-perfect mockups with final colours, typography, spacing, and interaction states. Recreate pixel-perfectly. Exact hex values, font families, and dimensions are documented in `tokens.jsx` and listed in [Design Tokens](#design-tokens) below.

---

## Screens

The app uses a fixed-size window (~400 × 740) with a dark titlebar (macOS traffic lights) and a bottom tab bar with 4 tabs: **Timer · Points · Tasks · Settings**.

### Frame chrome (shared across all screens)

- **Window size**: 400 × 740 (matches original; resize-friendly)
- **Window radius**: 22
- **Titlebar**: 36px tall, `#1F1F1F` background, centered title "LazyTom" in 13px/500 cream `#E6E1D2`, traffic lights at left (12px circles: `#FF5F57`, `#FEBC2E`, `#28C840`, gap 8)
- **Body background**: `#EFE9D9` (warm linen)
- **Tab bar**: 10px/14px padding, 1px top border `rgba(31,42,33,0.08)`, 4 tabs evenly spaced, active tab has a 24×3px moss bar above the icon and label colour switches to moss `#2F5A3A`; inactive label is `#9AA193`. Icons are 22×22 stroke icons (1.6 stroke), labels are 10.5px uppercase 600 weight.

---

### 01 · Timer

**Purpose**: Start a focus session. The "do one thing now" screen.

**Layout** (top → bottom):
1. **Header row** (padded 18px top, 24px sides) — left: "LazyTom" wordmark in serif 30px + uppercase date subtitle 11px/500 `#9AA193`; right: streak chip (cream pill with terracotta flame icon, big number, "DAY STREAK" label).
2. **Session pills** — 5 pills (22×6, radius 3) showing session progress; completed = moss `#2F5A3A`, current = leaf `#A8C49A`, future = line `rgba(31,42,33,0.08)`. Below: "Session 3 of 5 · Focus" caption in uppercase 10.5px.
3. **Ring** — 260×260 SVG centered, with:
   - 60 tick marks around the circumference (every 5th tick longer + darker)
   - Progress ring at radius 118, 3px stroke, gradient `#3F7A4B → #2F5A3A`, rotated -90° so 12 o'clock is start
   - Inner cream disc `#F7F2E4` with inset highlight + soft drop shadow
   - Inside disc: "FOCUS ON" caption, task title (Math Homework), big serif time `15:00` (68px, letter-spacing -2, tabular nums), "ends at 3:42 PM" caption
4. **+/- buttons** flanking the ring — 36px ghost circles with 1px border `rgba(31,42,33,0.14)`
5. **Primary CTA** — "Begin Focus" pill button: moss background, cream text, play icon + label, 14/26/14/32 padding, radius 999, prominent press shadow `0 12px 32px -8px rgba(47,90,58,0.45)`
6. **Caption below CTA**: "Notifications muted · Tap to start" (11px)

**Anti-procrastination touches**: Only one prominent button. The cancel ✕ is gone — you can't bail until after you start. The task you're about to focus on is shown inside the ring (commitment device).

---

### 02 · Points

**Purpose**: See cumulative progress and recent session history.

**Layout**:
1. **Title row**: "Your Garden" serif 30px + "MAY" right-aligned uppercase 10.5px.
2. **Hero card** — dark moss gradient (`linear-gradient(160deg, #2F5A3A 0%, #1F3F28 100%)`), 18 radius, 18/20 padding, with:
   - Subtle dot pattern overlay at 0.08 opacity (14×14 pattern, 1px dots in cream)
   - "TOTAL POINTS" label + "+4 today" chip (leaf-on-leaf-tint pill)
   - Big serif number `127` (64px, letter-spacing -2) + small "pts"
   - 7-bar weekly chart at bottom, bars cream `rgba(242,235,211,0.55)`, today's bar = terracotta `#C97A57`, height proportional to value, M/T/W/T/F/S/S labels
3. **"Recent sessions" section header** + counter "5 of 47" right
4. **History list** — flat list (no card backgrounds), each row:
   - 3px × 28px difficulty colour bar (left)
   - Task title (13.5px/600) + meta line "Today · 14:32 · 25m · Hard" (10.5px `#9AA193`)
   - Points "+3" right, serif 22px, moss colour, tabular nums
   - 1px bottom divider `rgba(31,42,33,0.08)` between items (no divider on last)

---

### 03 · Tasks

**Purpose**: Manage the queue and add new tasks.

**Layout**:
1. **Title row**: "Tasks" serif 30px + meta "● 3 pending · 1h 30m" (small terracotta dot + counter)
2. **"Start with this" hero card** — the auto-recommendation:
   - Cream paper background `#F7F2E4`, 16 radius, 1px line border, soft card shadow
   - Top row: spark/sun icon (terracotta) + "START WITH THIS" eyebrow + "HARD FIRST" label right (the sort mode it derived from)
   - Body: large serif task title ("Chinese essay — first draft"), 22px, line-height 1.15
   - Meta row: difficulty chip ("VERY HARD" in tinted rose pill) + "45 min · +5 pts"
   - Right: 52px moss play button with press shadow
3. **Sort segmented control** — small uppercase "ORDER" label + 3-option pill segment ("Easy first / Hard first / Manual"). Active option = dark ink fill `#1F2A21` with cream text.
4. **Task list** — same row pattern as Points history but with:
   - Empty 18×18 checkbox on left (5 radius, 1.5px border, cream fill)
   - Difficulty shown as a 6×6 colour dot + label
   - Round 28px play button on right
   - The suggested task (already shown in hero) is at 0.5 opacity to indicate "already promoted"
5. **Add-task composer card** (bottom, paper card):
   - "Templates" section header (8 templates as small pill chips — colour dot + name + duration)
   - Difficulty selector — labelled row, 5 buttons evenly spaced, the active one fills with its difficulty colour
   - Duration selector — same pattern, 8 options (5/10/15/20/25/30/45/60), active = dark ink fill
   - Text input + send (moss circle button with arrow icon)

---

### 04 · Settings

**Purpose**: Theme + Pomodoro durations + sound + DND.

**Layout**:
1. **Title row**: "Settings" serif 30px + "v2.4 · Synced 2 min ago" caption (11px)
2. **Appearance section**:
   - Section label "APPEARANCE" + hint "A calming visual to focus in"
   - 3 theme cards in a grid (Lakeside / Meadow / Dusk):
     - 12 radius paper card with 1.5px border (active = moss `#2F5A3A` with 3px ring glow)
     - 38px swatch row: background colour fills card, a 22×22 large circle bottom-left (primary accent), 14×14 small circle top-right (secondary)
     - Theme name (12px/600) + description (10px `#9AA193`)
     - Active card shows a 16px moss checkmark badge top-right
3. **Focus duration** — segment row, 6 options (15/20/25/30/45/60), active option uses serif font and gets bigger (subtle scale-up); "min" suffix at 0.6 opacity
4. **Break** — same segment pattern, 4 options (3/5/10/15)
5. **End sound** — 4-button row (Chime / Bowl / Birds / Silent), same active-dark-fill pattern
6. **DND toggle row** — paper card with toggle on right:
   - Title "Do not disturb while focusing" (13/600)
   - Subtitle "Silence notifications during sessions" (11 `#9AA193`)
   - 40×24 toggle, moss when on, ink line when off, 20px white thumb with shadow

---

## Interactions & behaviour

- **Tab bar**: tapping a tab switches the screen. Active tab gets the moss underline bar and label colour change.
- **Begin Focus button (Timer)**: starts the session. The ring fills clockwise as time progresses (animate `stroke-dasharray` from 0 → C). When running, the button should change to "Pause" (same shape, moss → terracotta?). Reaching 0 plays the chosen end-sound and increments points.
- **+/- buttons (Timer)**: adjust duration in 5-minute increments before the session starts. Hide / disable while a session is running.
- **Streak chip**: passive — no tap action.
- **Session pills (Timer)**: passive indicator of where you are in a 5-session cycle.
- **Hero "Start with this" card (Tasks)**: tap the play button to start that task as a session. The card content is derived from the Sort mode (`Easy first` picks lowest-difficulty, `Hard first` picks highest, `Manual` shows first in list).
- **Sort segmented (Tasks)**: changing the sort re-orders the task list and recalculates the hero suggestion.
- **Template chips (Tasks)**: tap to prefill the composer (sets title, difficulty, duration); does not auto-create.
- **Send (Tasks)**: creates a task and appends to the list.
- **Theme cards (Settings)**: tap to apply theme immediately across the app. Active card gets the moss border + checkmark badge.
- **DND toggle**: animate left ↔ right 0.2s ease.

### Animations / transitions

- Ring fill: smooth `stroke-dasharray` interpolation, 1s tick on second changes (or animate at frame rate for smoother sweep)
- Segment / pill selection: 150ms ease colour transition
- Card hover (desktop only): subtle lift — translate-Y -1px + boost shadow
- DND toggle thumb slide: 200ms ease

### Empty / loading / error states (not mocked — recommended defaults)

- **No tasks**: replace task list and hero card with a single placeholder card: "All clear — add a task to begin."
- **No history (Points)**: replace list with a small caption: "Your first session is one tap away."
- **Loading sync (Settings caption)**: cycle "Syncing…" → "Synced N min ago".

---

## State management

State needed (per current mocks):

- `timer`: { duration, elapsed, isRunning, currentTaskId, currentSession (1..5), totalSessions }
- `tasks`: list of { id, title, difficulty (0..4), durationMins, completed }
- `templates`: list of { id, name, difficulty, durationMins } — could be seeded constants
- `points`: { total, history: [{ taskId, completedAt, mins, pts, difficulty }] }
- `streak`: { days, lastCompletedDate }
- `settings`: { theme, focusDuration, breakDuration, endSound, doNotDisturb }
- `sort`: 'easy' | 'hard' | 'manual'

Points formula (inferred from screenshots): `pts = floor((difficulty + 1) * (mins / 25))` — easy short task = 1pt, very hard 45min = 5pts.

---

## Design Tokens

All tokens live in `tokens.jsx` and are also listed here for convenience.

### Colours

| Token | Value | Use |
|---|---|---|
| `bg` | `#EFE9D9` | Page background (warm linen) |
| `paper` | `#F7F2E4` | Cards / surfaces |
| `ink` | `#1F2A21` | Primary text, dark fills |
| `inkSoft` | `#5C6655` | Secondary text |
| `inkMute` | `#9AA193` | Captions, disabled |
| `line` | `rgba(31,42,33,0.08)` | Subtle dividers |
| `lineStr` | `rgba(31,42,33,0.14)` | Stronger borders |
| `moss` | `#2F5A3A` | Primary brand colour |
| `mossSoft` | `#5C8A5C` | Normal difficulty |
| `leaf` | `#A8C49A` | Muted sage, easy difficulty, current session pill |
| `cream` | `#F2EBD3` | Accent cream, on-dark text |
| `clay` | `#C97A57` | Terracotta accent, "now do this" |
| `amber` | `#D9A24E` | Hard difficulty |
| `rose` | `#B85A5A` | Very hard difficulty |
| `sky` | `#7AA2C2` | Easy difficulty / Lakeside theme primary |
| `shell` | `#E8DCC0` | Very easy difficulty |

### Typography

- **Serif (display)**: `Instrument Serif`, fallback `Cormorant Garamond, Georgia, serif`. Used for: page titles, big numerals, hero task titles.
- **Sans (UI)**: `Geist`, fallback `Inter, -apple-system, BlinkMacSystemFont, sans-serif`. Used for: body, labels, buttons.
- **Mono (rare)**: `Geist Mono`, fallback `JetBrains Mono, ui-monospace, monospace`.

Type scale (from the mocks):

| Use | Family | Size | Weight | Letter-spacing |
|---|---|---|---|---|
| Page title | serif | 30 | regular | -0.5 |
| Hero number (Points) | serif | 64 | regular | -2 |
| Timer numeric | serif | 68 | regular | -2 |
| Hero task title (Tasks) | serif | 22 | regular | -0.3 |
| History "+N" | serif | 22 | regular | -0.5 |
| Body | sans | 13–13.5 | 500–600 | 0 |
| Button | sans | 12–15 | 600 | 0.3 |
| Caption | sans | 10.5–11 | 500 | 0.4 |
| Eyebrow / section label | sans | 10.5–11 | 600 | 1.0 (UPPERCASE) |
| Pill / chip | sans | 10–11.5 | 500–600 | 0.3 |

Always set `font-variant-numeric: tabular-nums` on any displayed number that will change (timer, points, history values).

### Spacing

- Screen edge padding: **24** horizontal, **18–20** top
- Section gap: **14–18**
- Card padding: **12–18**
- Pill padding: **5/10** (sm), **8/12** (md), **14/26** (lg/CTA)

### Radii

- Window: **22**
- Card (large): **16–18**
- Card (medium): **12–14**
- Input / pill (small): **8–10**
- Fully rounded pill: **999**
- Toggle: **999**

### Shadows

- `card`: `0 1px 0 rgba(255,255,255,0.6) inset, 0 1px 2px rgba(31,42,33,0.04), 0 8px 24px -8px rgba(31,42,33,0.08)`
- `cardHi`: `0 1px 0 rgba(255,255,255,0.7) inset, 0 4px 12px rgba(31,42,33,0.08), 0 24px 48px -16px rgba(31,42,33,0.12)`
- `press` (CTAs): `0 12px 32px -8px rgba(47,90,58,0.45)`
- Inset highlight on light surfaces is part of the "warm paper" feel — keep it.

### Difficulty colour mapping

| Level | Colour | Token |
|---|---|---|
| Very Easy | `#7AA2C2` | sky |
| Easy | `#A8C49A` | leaf |
| Normal | `#5C8A5C` | mossSoft |
| Hard | `#D9A24E` | amber |
| Very Hard | `#B85A5A` | rose |

---

## Assets

- **No bitmap assets used** — all icons are inline SVG stroke icons (1.6 stroke width, round caps/joins), the streak flame is also inline SVG.
- **Fonts**: load from Google Fonts (`Instrument Serif`, `Geist`, `Geist Mono`) or self-host equivalents.
- **Original "before" screenshots** are in `screenshots/before-0[1-4]-*.png` for reference.

---

## Files in this bundle

| File | Role |
|---|---|
| `LazyTom Redesign.html` | Entry point — opens the design canvas with all 4 screens side by side |
| `tokens.jsx` | All design tokens + shared frame chrome (`LTFrame`, `LTTabBar`) |
| `screen-timer.jsx` | Timer screen component |
| `screen-points.jsx` | Points screen component |
| `screen-tasks.jsx` | Tasks screen component |
| `screen-settings.jsx` | Settings screen component |
| `design-canvas.jsx` | Pan/zoom canvas wrapper (presentation only — not part of the app) |
| `screenshots/before-*.png` | Original screens (provided by user) for before/after comparison |
| `screenshots/01-overview.png` | Snapshot of the canvas |

### Opening the prototype

Open `LazyTom Redesign.html` in a browser — it presents all 4 screens on a zoomable canvas. Double-click any screen to focus fullscreen; use ← / → / Esc to navigate.

---

## Implementation notes for the developer

1. **Lift the tokens first** — reproduce `tokens.jsx` as your codebase's nearest equivalent (CSS variables, Tailwind config, design tokens file, etc.) **before** building any screen. Every other measurement depends on these.
2. **The "Begin Focus" single-button pattern is intentional** — the original had an ✕ + play pair which gives procrastinators an easy out. Don't restore the cancel button on the ready state. (A cancel/pause can appear once the session has started.)
3. **"Start with this" card** is the most important new UX pattern. It removes the choice paralysis of staring at a task list. The recommendation logic should derive from the current Sort mode (Easy first / Hard first / Manual).
4. **Difficulty as a colour dot, not a coloured chip** — the original task list had every task wrapped in a coloured pill which created visual noise. Use a 6×6 dot + text label instead. Reserve the coloured pill treatment for the hero card only.
5. **Tabular numerals everywhere** — any number that ticks (timer, points, durations) must use `font-variant-numeric: tabular-nums` to avoid layout jitter.
6. **Serif for moments of weight** — page titles, hero numbers, hero task titles. Don't sprinkle serif into UI buttons or body text.
7. **The Settings page added Break / Sound / DND** that weren't in the original mocks but are essential to a Pomodoro app — confirm with product whether to ship these now or hide them behind a feature flag.
