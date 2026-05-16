"""LazyTom theme configuration — 3 healing themes.

Themes:
  - Lakeside (default): butterfly & flower lake, soft blue-green
  - Meadow: fresh green grass, sunny and warm
  - Starry Night: deep blue-purple sky, calm and peaceful
"""

from enum import Enum


class ThemeName(Enum):
    LAKESIDE = "lakeside"
    MEADOW = "meadow"
    STARRY = "starry"


THEME_DISPLAY_NAMES = {
    ThemeName.LAKESIDE: "Lakeside 🦋",
    ThemeName.MEADOW: "Meadow 🌿",
    ThemeName.STARRY: "Starry Night ✨",
}


class ThemeColors:
    def __init__(self, bg, surface, text_primary, text_secondary, accent, accent_dim, divider, ring_track):
        self.bg = bg
        self.surface = surface
        self.text_primary = text_primary
        self.text_secondary = text_secondary
        self.accent = accent
        self.accent_dim = accent_dim
        self.divider = divider
        self.ring_track = ring_track


# ── Lakeside: soft blue-green, warm lake with butterflies & flowers ────
_LAKESIDE = ThemeColors(
    bg="#E8F4F0",
    surface="#FFFFFF",
    text_primary="#2D3B36",
    text_secondary="#7A918A",
    accent="#4DACB0",
    accent_dim="#B8DFE0",
    divider="#C8DDD8",
    ring_track="#D4EBE4",
)

# ── Meadow: fresh green, warm sunshine on grass ────────────────────────
_MEADOW = ThemeColors(
    bg="#F0F7E8",
    surface="#FFFFFF",
    text_primary="#2E3A28",
    text_secondary="#7A9170",
    accent="#6BBF59",
    accent_dim="#C2E8B8",
    divider="#D0DFC8",
    ring_track="#E2F0D4",
)

# ── Starry Night: deep blue-purple, calm and peaceful ─────────────────
_STARRY = ThemeColors(
    bg="#1A1B2E",
    surface="#2A2D4A",
    text_primary="#E8E8F0",
    text_secondary="#8888AA",
    accent="#7B8CDE",
    accent_dim="#3D4478",
    divider="#3A3D5A",
    ring_track="#252847",
)

THEMES = {
    ThemeName.LAKESIDE: _LAKESIDE,
    ThemeName.MEADOW: _MEADOW,
    ThemeName.STARRY: _STARRY,
}

# ── Current theme name ─────────────────────────────────────────────────
current_theme_name: ThemeName = ThemeName.LAKESIDE

# ── Module-level color variables (used by all existing code) ───────────
# These get reassigned by set_theme()
BG_COLOR = _LAKESIDE.bg
SURFACE_COLOR = _LAKESIDE.surface
TEXT_PRIMARY = _LAKESIDE.text_primary
TEXT_SECONDARY = _LAKESIDE.text_secondary
TOMATO_RED = _LAKESIDE.accent
TOMATO_RED_DIM = _LAKESIDE.accent_dim
DIVIDER_COLOR = _LAKESIDE.divider
RING_TRACK_COLOR = _LAKESIDE.ring_track


def set_theme(name: ThemeName):
    """Switch all color variables to the new theme."""
    global BG_COLOR, SURFACE_COLOR, TEXT_PRIMARY, TEXT_SECONDARY
    global TOMATO_RED, TOMATO_RED_DIM, DIVIDER_COLOR, RING_TRACK_COLOR
    global current_theme_name

    current_theme_name = name
    t = THEMES[name]
    BG_COLOR = t.bg
    SURFACE_COLOR = t.surface
    TEXT_PRIMARY = t.text_primary
    TEXT_SECONDARY = t.text_secondary
    TOMATO_RED = t.accent
    TOMATO_RED_DIM = t.accent_dim
    DIVIDER_COLOR = t.divider
    RING_TRACK_COLOR = t.ring_track


# ── Font sizes (theme-independent) ────────────────────────────────────
TIMER_FONT_SIZE = 72
TITLE_FONT_SIZE = 24
SUBTITLE_FONT_SIZE = 18
BODY_FONT_SIZE = 16
CAPTION_FONT_SIZE = 12

# ── Spacing (theme-independent) ───────────────────────────────────────
PADDING_SM = 8
PADDING_MD = 16
PADDING_LG = 24
PADDING_XL = 32

# ── Countdown ring (theme-independent) ────────────────────────────────
RING_SIZE = 280
RING_STROKE_WIDTH = 8
