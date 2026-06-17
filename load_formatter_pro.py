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

import tkinter as tk

from app.main_window import LoadFormatterProApp


def main():
  root = tk.Tk()
  LoadFormatterProApp(root)
  root.mainloop()


if __name__ == "__main__":
  main()
