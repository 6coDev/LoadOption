"""Visual Studio Code inspired colour palettes and theme switching."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
  bg_main: str
  bg_box: str
  bg_btn: str
  bg_btn_hover: str
  bg_btn_inactive: str
  bg_btn_inactive_hover: str
  bg_accent: str
  bg_accent_hover: str
  bg_status: str
  fg_text: str
  fg_muted: str
  fg_title: str
  fg_version: str
  fg_separator: str
  fg_on_btn: str
  fg_btn_idle: str
  border_box: str
  tab_accent: str           # underline colour for the active tab chip
  bg_box_focus_border: str  # highlight border colour when a box has focus


DARK = Palette(
  bg_main="#1A1A1C",
  bg_box="#1E1E1E",
  bg_btn="#0E78C4",
  bg_btn_hover="#1A8CDB",
  bg_btn_inactive="#2D2D30",
  bg_btn_inactive_hover="#3A3A3D",
  bg_accent="#4A4A4A",
  bg_accent_hover="#5A5A5A",
  bg_status="#252528",
  fg_text="#F2F2F2",
  fg_muted="#D4D4D4",
  fg_title="#FFFFFF",
  fg_version="#9A9A9A",
  fg_separator="#33333A",
  fg_on_btn="#FFFFFF",
  fg_btn_idle="#C8C8C8",
  border_box="#33333A",
  tab_accent="#2BA6E0",
  bg_box_focus_border="#2BA6E0",
)

LIGHT = Palette(
  bg_main="#EFEFF2",
  bg_box="#FFFFFF",
  bg_btn="#0078D4",
  bg_btn_hover="#106EBE",
  bg_btn_inactive="#E2E8F0",
  bg_btn_inactive_hover="#CBD8E8",
  bg_accent="#E67E22",
  bg_accent_hover="#D35400",
  bg_status="#E2E2E6",
  fg_text="#1A1A1A",
  fg_muted="#2A2A2A",
  fg_title="#101010",
  fg_version="#5A5A5A",
  fg_separator="#C7C7CC",
  fg_on_btn="#FFFFFF",
  fg_btn_idle="#1F4E79",
  border_box="#C7C7CC",
  tab_accent="#0078D4",
  bg_box_focus_border="#0078D4",
)

FONT_UI = ("Segoe UI", 11)
FONT_UI_BOLD = ("Segoe UI", 11, "bold")
FONT_UI_SMALL = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_VERSION = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 11)
FONT_BTN = ("Segoe UI", 10, "bold")
FONT_STATUS = ("Segoe UI", 10)

PAD = 10
PAD_COMPACT = 6

_mode = "dark"
_p = DARK


def current_mode() -> str:
  return _mode


def palette() -> Palette:
  return _p


def set_mode(mode: str) -> str:
  """Switch theme to 'dark' or 'light'."""
  global _mode, _p
  _mode = "light" if mode == "light" else "dark"
  _p = LIGHT if _mode == "light" else DARK
  _sync_legacy_names()
  return _mode


def toggle_mode() -> str:
  return set_mode("light" if _mode == "dark" else "dark")


def _sync_legacy_names():
  """Keep module-level colour names in sync for existing imports."""
  global BG_MAIN, BG_BOX, BG_BTN, BG_BTN_HOVER
  global BG_BTN_INACTIVE, BG_BTN_INACTIVE_HOVER, BG_ACCENT, BG_ACCENT_HOVER
  global BG_STATUS, FG_TEXT, FG_MUTED, FG_TITLE, FG_VERSION, FG_SEPARATOR
  global FG_ON_BTN, FG_BTN_IDLE, BORDER_BOX, TAB_ACCENT, BG_BOX_FOCUS_BORDER

  p = _p
  BG_MAIN = p.bg_main
  BG_BOX = p.bg_box
  BG_BTN = p.bg_btn
  BG_BTN_HOVER = p.bg_btn_hover
  BG_BTN_INACTIVE = p.bg_btn_inactive
  BG_BTN_INACTIVE_HOVER = p.bg_btn_inactive_hover
  BG_ACCENT = p.bg_accent
  BG_ACCENT_HOVER = p.bg_accent_hover
  BG_STATUS = p.bg_status
  FG_TEXT = p.fg_text
  FG_MUTED = p.fg_muted
  FG_TITLE = p.fg_title
  FG_VERSION = p.fg_version
  FG_SEPARATOR = p.fg_separator
  FG_ON_BTN = p.fg_on_btn
  FG_BTN_IDLE = p.fg_btn_idle
  BORDER_BOX = p.border_box
  TAB_ACCENT = p.tab_accent
  BG_BOX_FOCUS_BORDER = p.bg_box_focus_border


_sync_legacy_names()
