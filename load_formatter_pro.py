#!/usr/bin/env python3
"""
Load Formatter Pro v3.0
Professional multi load-board formatter — DAT, Sylectus, Auto Detect.

Run:
    python load_formatter_pro.py

Build standalone .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "LoadFormatterPro" load_formatter_pro.py
"""

import sys
import tkinter as tk

from app.main_window import LoadFormatterProApp


def _enable_windows_dpi_awareness():
  """
  Without this, Windows treats the app as DPI-unaware on any scaled
  display (125%/150%/200% — the default on most modern laptops and
  monitors). An unaware app is rendered at 96 DPI into a small bitmap that
  Windows then stretches to fill the screen — that stretch is what makes
  every border, hairline, and glyph look soft/blurry. This is a rendering
  pipeline issue, not a font or colour choice, and no amount of palette or
  border tweaking fixes it without this call.

  Calling SetProcessDpiAwareness(2) (PROCESS_PER_MONITOR_DPI_AWARE) tells
  Windows to hand the app real per-monitor pixels instead of a stretched
  bitmap, so Tk renders text and borders at native sharpness.

  Must run BEFORE tk.Tk() is constructed. No-op on non-Windows platforms.
  """
  if sys.platform != "win32":
    return
  try:
    import ctypes
    # PROCESS_PER_MONITOR_DPI_AWARE = 2 — sharpest option, correctly
    # handles users with multiple monitors at different scale factors.
    ctypes.OleDLL("shcore").SetProcessDpiAwareness(2)
  except Exception:
    # Older Windows (no shcore) — fall back to the simpler, system-wide
    # DPI-aware flag. Still far better than no awareness call at all.
    try:
      import ctypes
      ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
      pass  # Best effort — never let DPI setup crash the app on launch.


def main():
  _enable_windows_dpi_awareness()

  root = tk.Tk()
  LoadFormatterProApp(root)
  root.mainloop()


if __name__ == "__main__":
  main()
