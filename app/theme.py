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


DARK = Palette(
  bg_main="#1E1E1E",
  bg_box="#252526",
  bg_btn="#0E639C",
  bg_btn_hover="#1177BB",
  bg_btn_inactive="#3C3C3C",
  bg_btn_inactive_hover="#4A4A4A",
  bg_accent="#4A4A4A",
  bg_accent_hover="#5A5A5A",
  bg_status="#2D2D30",
  fg_text="#FFFFFF",
  fg_muted="#D4D4D4",
  fg_title="#FFFFFF",
  fg_version="#A0A0A0",
  fg_separator="#3C3C3C",
  fg_on_btn="#FFFFFF",
  fg_btn_idle="#D4D4D4",
  border_box="#3C3C3C",
)

LIGHT = Palette(
  bg_main="#F0F0F0",
  bg_box="#FFFFFF",
  bg_btn="#0078D4",
  bg_btn_hover="#005A9E",
  bg_btn_inactive="#C8E0F8",
  bg_btn_inactive_hover="#A8D4F5",
  bg_accent="#E67E22",
  bg_accent_hover="#D35400",
  bg_status="#E0E0E0",
  fg_text="#000000",
  fg_muted="#1A1A1A",
  fg_title="#000000",
  fg_version="#333333",
  fg_separator="#B0B0B0",
  fg_on_btn="#FFFFFF",
  fg_btn_idle="#0A3D62",
  border_box="#9E9E9E",
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
  global FG_ON_BTN, FG_BTN_IDLE, BORDER_BOX

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


_sync_legacy_names()
