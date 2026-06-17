"""
Load Formatter Pro — main application window.

GUI only: all parsing lives in the formatters package.
"""

import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox

from app import theme as T
from app.maps_link import build_maps_directions_url, extract_route_from_output
from formatters.detect import resolve_formatter
from formatters.registry import AUTO_DETECT_KEY, AUTO_DETECT_SPEC, FORMATTER_REGISTRY


class LoadFormatterProApp:
  """Main window — formatter selection, input/output panes, and actions."""

  def __init__(self, root: tk.Tk):
    self.root = root
    self._active_mode = "dat"
    self._formatter_buttons: dict[str, tk.Button] = {}
    self._action_buttons: list[tk.Button] = []
    self._theme_frames: list[tk.Frame] = []
    self._text_frames: list[tk.Frame] = []
    self._theme_labels: list[tk.Label] = []
    self._status_message = "Ready"

    self._build_window()
    self._build_menu()
    self._build_top_bar()
    self._build_editor_panes()
    self._build_status_bar()
    self._bind_shortcuts()

    self._set_active_mode("dat")
    self._update_status("Ready")
    self.input_box.focus_set()

  # ── Window ──────────────────────────────────────────────────────────────────

  def _build_window(self):
    self.root.title("Load Formatter Pro v3.0")
    self.root.configure(bg=T.BG_MAIN)
    self.root.resizable(True, True)
    self.root.minsize(720, 520)

    self.root.update_idletasks()
    screen_w = self.root.winfo_screenwidth()
    screen_h = self.root.winfo_screenheight()
    w = min(900, max(720, screen_w - 60))
    h = min(720, max(520, screen_h - 80))
    x = max(0, (screen_w - w) // 2)
    y = max(0, (screen_h - h) // 2)
    self.root.geometry(f"{w}x{h}+{x}+{y}")

    self.root.columnconfigure(0, weight=1)
    for row in range(4):
      self.root.rowconfigure(row, weight=0)
    self.root.rowconfigure(2, weight=1, minsize=280)

  # ── Menu ────────────────────────────────────────────────────────────────────

  def _build_menu(self):
    menubar = tk.Menu(
      self.root,
      bg=T.BG_BTN,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_BTN_HOVER,
      activeforeground=T.FG_ON_BTN,
      relief="flat",
      bd=0,
    )
    help_menu = tk.Menu(
      menubar,
      tearoff=0,
      bg=T.BG_BTN,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_BTN_HOVER,
      activeforeground=T.FG_ON_BTN,
    )
    help_menu.add_command(label="About", command=self._show_about)
    menubar.add_cascade(label="Help", menu=help_menu)

    view_menu = tk.Menu(
      menubar,
      tearoff=0,
      bg=T.BG_BTN,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_BTN_HOVER,
      activeforeground=T.FG_ON_BTN,
    )
    view_menu.add_command(label="Reset Panel Split", command=self._reset_panel_split)
    view_menu.add_separator()
    view_menu.add_command(label="Switch to Light Theme", command=self._toggle_theme)
    self._theme_menu_index = view_menu.index("end")
    view_menu.add_separator()
    view_menu.add_command(label="Maximize", command=self._maximize_window)
    view_menu.add_command(label="Restore", command=self._restore_window)
    menubar.add_cascade(label="View", menu=view_menu)

    self._menubar = menubar
    self._view_menu = view_menu
    self._help_menu = help_menu
    self.root.config(menu=menubar)

  # ── Compact top bar (title + formatter buttons) ─────────────────────────────

  def _build_top_bar(self):
    self._top_bar = tk.Frame(self.root, bg=T.BG_MAIN)
    self._top_bar.grid(row=0, column=0, sticky="ew", padx=T.PAD, pady=(T.PAD_COMPACT, 2))
    self._top_bar.columnconfigure(0, weight=1)
    self._theme_frames.append(self._top_bar)

    title_frame = tk.Frame(self._top_bar, bg=T.BG_MAIN)
    title_frame.grid(row=0, column=0, sticky="w")
    self._theme_frames.append(title_frame)

    title_lbl = tk.Label(
      title_frame,
      text="LOAD FORMATTER PRO",
      bg=T.BG_MAIN,
      fg=T.FG_TITLE,
      font=T.FONT_TITLE,
      anchor="w",
    )
    title_lbl.pack(side="left")
    self._theme_labels.append(title_lbl)

    version_lbl = tk.Label(
      title_frame,
      text="  v3.0",
      bg=T.BG_MAIN,
      fg=T.FG_VERSION,
      font=T.FONT_VERSION,
      anchor="w",
    )
    version_lbl.pack(side="left", pady=(3, 0))
    self._theme_labels.append(version_lbl)

    btn_row = tk.Frame(self._top_bar, bg=T.BG_MAIN)
    btn_row.grid(row=0, column=1, sticky="e")
    self._theme_frames.append(btn_row)

    for spec in list(FORMATTER_REGISTRY.values()) + [AUTO_DETECT_SPEC]:
      btn = self._make_formatter_button(btn_row, spec)
      btn.pack(side="left", padx=(4, 0))
      self._formatter_buttons[spec.key] = btn

    self._theme_toggle_btn = tk.Button(
      btn_row,
      text="☀  Light",
      command=self._toggle_theme,
      font=T.FONT_BTN,
      relief="flat",
      bd=0,
      padx=10,
      pady=4,
      cursor="hand2",
    )
    self._theme_toggle_btn.pack(side="left", padx=(10, 0))
    self._style_theme_toggle_button()

    self._separator = tk.Frame(self.root, bg=T.FG_SEPARATOR, height=1)
    self._separator.grid(row=1, column=0, sticky="ew", padx=T.PAD, pady=(4, 4))

  def _make_formatter_button(self, parent, spec) -> tk.Button:
    label = f"{spec.icon} {spec.label}"
    btn = tk.Button(
      parent,
      text=label,
      command=lambda k=spec.key: self._on_formatter_selected(k),
      font=T.FONT_BTN,
      relief="flat",
      bd=0,
      padx=10,
      pady=4,
      cursor="hand2",
    )
    self._style_formatter_button(btn, active=False)
    return btn

  def _style_formatter_button(self, btn: tk.Button, *, active: bool):
    if active:
      bg, hover = T.BG_BTN, T.BG_BTN_HOVER
      fg = T.FG_ON_BTN
      active_fg = T.FG_ON_BTN
    else:
      bg, hover = T.BG_BTN_INACTIVE, T.BG_BTN_INACTIVE_HOVER
      fg = T.FG_BTN_IDLE
      active_fg = T.FG_ON_BTN if T.current_mode() == "light" else T.FG_TEXT

    btn.configure(bg=bg, fg=fg, activebackground=hover, activeforeground=active_fg)
    btn.unbind("<Enter>")
    btn.unbind("<Leave>")
    btn.bind("<Enter>", lambda _e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=bg))

  def _set_active_mode(self, mode_key: str):
    self._active_mode = mode_key
    for key, btn in self._formatter_buttons.items():
      self._style_formatter_button(btn, active=(key == mode_key))

  def _on_formatter_selected(self, mode_key: str):
    self._set_active_mode(mode_key)
    self._run_format()

  # ── Resizable input / output panes ──────────────────────────────────────────

  def _build_editor_panes(self):
    self._paned = tk.PanedWindow(
      self.root,
      orient=tk.VERTICAL,
      bg=T.FG_SEPARATOR,
      sashwidth=7,
      sashrelief=tk.FLAT,
      opaqueresize=True,
      borderwidth=0,
      relief=tk.FLAT,
      showhandle=False,
    )
    self._paned.grid(row=2, column=0, sticky="nsew", padx=T.PAD, pady=(0, T.PAD_COMPACT))

    input_pane = self._build_editor_pane("INPUT", is_output=False)
    output_pane = self._build_editor_pane("OUTPUT", is_output=True)

    self._paned.add(input_pane, minsize=110, stretch="always")
    self._paned.add(output_pane, minsize=160, stretch="always")

    self.root.after_idle(self._apply_initial_split)

  def _build_editor_pane(self, title: str, *, is_output: bool) -> tk.Frame:
    pane = tk.Frame(self._paned, bg=T.BG_MAIN)
    pane.columnconfigure(0, weight=1)
    pane.rowconfigure(1, weight=1)
    self._theme_frames.append(pane)

    section_lbl = tk.Label(
      pane,
      text=title,
      bg=T.BG_MAIN,
      fg=T.FG_TEXT,
      font=T.FONT_UI_BOLD,
      anchor="w",
    )
    section_lbl.grid(row=0, column=0, sticky="ew", padx=T.PAD, pady=(4, 2))
    self._theme_labels.append(section_lbl)

    text_frame = tk.Frame(pane, bg=T.BG_BOX)
    text_frame.grid(row=1, column=0, sticky="nsew", padx=T.PAD)
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)
    self._text_frames.append(text_frame)

    text_kwargs = dict(
      bg=T.BG_BOX,
      fg=T.FG_TEXT,
      insertbackground=T.FG_TEXT,
      selectbackground=T.BG_BTN,
      font=T.FONT_MONO,
      wrap="none",
      relief="flat",
      bd=4,
      height=1,
      undo=True,
      maxundo=-1,
    )
    if is_output:
      text_kwargs.update(
        highlightthickness=1,
        highlightbackground=T.BORDER_BOX,
        highlightcolor=T.BG_BTN,
      )

    text_box = tk.Text(text_frame, **text_kwargs)
    text_box.grid(row=0, column=0, sticky="nsew")

    scroll_y = tk.Scrollbar(text_frame, orient="vertical", command=text_box.yview)
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x = tk.Scrollbar(text_frame, orient="horizontal", command=text_box.xview)
    scroll_x.grid(row=1, column=0, sticky="ew")
    text_box.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    btn_frame = tk.Frame(pane, bg=T.BG_MAIN)
    btn_frame.grid(row=2, column=0, sticky="w", padx=T.PAD, pady=(4, 4))
    self._theme_frames.append(btn_frame)

    if is_output:
      self.output_box = text_box
      self._make_action_button(btn_frame, "📄  Copy", self._copy_output).pack(
        side="left", padx=(0, 8)
      )
      self._make_action_button(btn_frame, "💾  Save", self._save_output).pack(
        side="left", padx=(0, 8)
      )
      self._make_action_button(btn_frame, "🗺  Maps Route", self._open_maps_route).pack(side="left")
    else:
      self.input_box = text_box
      self.input_box.bind("<<Modified>>", self._on_input_changed)
      self.input_box.bind("<KeyRelease>", self._on_input_stats_changed)
      self._make_action_button(btn_frame, "📋  Paste", self._paste_clipboard).pack(
        side="left", padx=(0, 8)
      )
      self._make_action_button(btn_frame, "🗑  Clear", self._clear_fields).pack(side="left")

    return pane

  def _apply_initial_split(self, input_ratio: float = 0.32):
    """Default split: ~32% input, ~68% output."""
    self.root.update_idletasks()
    total_h = self._paned.winfo_height()
    if total_h <= 0:
      self.root.after(50, lambda: self._apply_initial_split(input_ratio))
      return
    sash_y = max(110, min(total_h - 160, int(total_h * input_ratio)))
    try:
      self._paned.sash_place(0, 0, sash_y)
    except tk.TclError:
      pass

  def _reset_panel_split(self):
    self._apply_initial_split(0.32)
    self._update_status("Panel split reset.")

  def _maximize_window(self):
    try:
      self.root.state("zoomed")
    except tk.TclError:
      self.root.attributes("-zoomed", True)

  def _restore_window(self):
    try:
      self.root.state("normal")
    except tk.TclError:
      self.root.attributes("-zoomed", False)

  # ── Maps route ──────────────────────────────────────────────────────────────

  def _open_maps_route(self):
    output_text = self.output_box.get("1.0", "end-1c")
    route = extract_route_from_output(output_text)

    if not route:
      messagebox.showwarning(
        "Maps Route",
        "Could not find pickup and delivery in the output.\n\n"
        "Format a load first — the first line should look like:\n"
        "  City, ST ------- City, ST\n"
        "  City, ST >>>>>>>> City, ST",
      )
      self._update_status("No pickup/delivery found for maps.")
      return

    pickup, delivery = route
    webbrowser.open(build_maps_directions_url(pickup, delivery))
    self._update_status(f"Opened maps route: {pickup} → {delivery}")

  # ── Status bar ──────────────────────────────────────────────────────────────

  def _build_status_bar(self):
    self.status_var = tk.StringVar(value="Status: Ready")
    self._status_label = tk.Label(
      self.root,
      textvariable=self.status_var,
      bg=T.BG_STATUS,
      fg=T.FG_TEXT,
      font=T.FONT_STATUS,
      anchor="w",
      relief="flat",
      bd=0,
      padx=10,
      pady=4,
    )
    self._status_label.grid(row=3, column=0, sticky="ew")

  # ── Theme toggle ────────────────────────────────────────────────────────────

  def _toggle_theme(self):
    mode = T.toggle_mode()
    self._apply_theme()
    name = "Light" if mode == "light" else "Dark"
    self._update_status(f"{name} theme enabled.")

  def _style_theme_toggle_button(self):
    btn = self._theme_toggle_btn
    if T.current_mode() == "dark":
      label = "☀  Light"
    else:
      label = "🌙  Dark"

    btn.configure(
      text=label,
      bg=T.BG_ACCENT,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_ACCENT_HOVER,
      activeforeground=T.FG_ON_BTN,
    )
    btn.unbind("<Enter>")
    btn.unbind("<Leave>")
    btn.bind("<Enter>", lambda _e: btn.configure(bg=T.BG_ACCENT_HOVER))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=T.BG_ACCENT))

  def _apply_theme(self):
    self.root.configure(bg=T.BG_MAIN)
    self._paned.configure(bg=T.FG_SEPARATOR)
    self._separator.configure(bg=T.FG_SEPARATOR)

    for frame in self._theme_frames:
      frame.configure(bg=T.BG_MAIN)
    for frame in self._text_frames:
      frame.configure(bg=T.BG_BOX)

    for label in self._theme_labels:
      font = label.cget("font")
      if font == T.FONT_TITLE:
        fg = T.FG_TITLE
      elif font == T.FONT_VERSION:
        fg = T.FG_VERSION
      else:
        fg = T.FG_TEXT
      label.configure(bg=T.BG_MAIN, fg=fg)

    for box in (self.input_box, self.output_box):
      box.configure(
        bg=T.BG_BOX,
        fg=T.FG_TEXT,
        insertbackground=T.FG_TEXT,
        selectbackground=T.BG_BTN,
      )
    self.output_box.configure(
      highlightbackground=T.BORDER_BOX,
      highlightcolor=T.BG_BTN,
    )

    for key, btn in self._formatter_buttons.items():
      self._style_formatter_button(btn, active=(key == self._active_mode))

    for btn in self._action_buttons:
      btn.configure(
        bg=T.BG_BTN,
        fg=T.FG_ON_BTN,
        activebackground=T.BG_BTN_HOVER,
        activeforeground=T.FG_ON_BTN,
      )
      btn.unbind("<Enter>")
      btn.unbind("<Leave>")
      btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=T.BG_BTN_HOVER))
      btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=T.BG_BTN))

    self._status_label.configure(bg=T.BG_STATUS, fg=T.FG_TEXT)
    self._style_theme_toggle_button()

    menu_kw = dict(
      bg=T.BG_BTN,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_BTN_HOVER,
      activeforeground=T.FG_ON_BTN,
    )
    self._menubar.configure(**menu_kw)
    self._view_menu.configure(**menu_kw)
    self._help_menu.configure(**menu_kw)

    if T.current_mode() == "dark":
      self._view_menu.entryconfigure(self._theme_menu_index, label="Switch to Light Theme")
    else:
      self._view_menu.entryconfigure(self._theme_menu_index, label="Switch to Dark Theme")

  # ── Widget helpers ──────────────────────────────────────────────────────────

  def _make_action_button(self, parent, text: str, command) -> tk.Button:
    btn = tk.Button(
      parent,
      text=text,
      command=command,
      bg=T.BG_BTN,
      fg=T.FG_ON_BTN,
      activebackground=T.BG_BTN_HOVER,
      activeforeground=T.FG_ON_BTN,
      font=T.FONT_UI_BOLD,
      relief="flat",
      bd=0,
      padx=14,
      pady=6,
      cursor="hand2",
    )
    btn.bind("<Enter>", lambda _e: btn.configure(bg=T.BG_BTN_HOVER))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=T.BG_BTN))
    self._action_buttons.append(btn)
    return btn

  # ── Keyboard shortcuts ──────────────────────────────────────────────────────

  def _bind_shortcuts(self):
    self.root.bind_all("<Control-v>", self._shortcut_paste)
    self.root.bind_all("<Control-V>", self._shortcut_paste)
    self.root.bind_all("<Control-c>", self._shortcut_copy)
    self.root.bind_all("<Control-C>", self._shortcut_copy)
    self.root.bind_all("<Control-s>", self._shortcut_save)
    self.root.bind_all("<Control-S>", self._shortcut_save)
    self.root.bind_all("<Control-l>", self._shortcut_clear)
    self.root.bind_all("<Control-L>", self._shortcut_clear)
    self.root.bind_all("<Control-a>", self._shortcut_select_all)
    self.root.bind_all("<Control-A>", self._shortcut_select_all)

  def _shortcut_paste(self, _event=None):
    self._paste_clipboard()
    return "break"

  def _shortcut_copy(self, _event=None):
    self._copy_output()
    return "break"

  def _shortcut_save(self, _event=None):
    self._save_output()
    return "break"

  def _shortcut_clear(self, _event=None):
    self._clear_fields()
    return "break"

  def _shortcut_select_all(self, event=None):
    widget = self.root.focus_get()
    if isinstance(widget, tk.Text):
      widget.tag_add("sel", "1.0", "end")
      return "break"
    return None

  # ── Status helpers ──────────────────────────────────────────────────────────

  def _input_stats(self) -> tuple[int, int]:
    text = self.input_box.get("1.0", "end-1c")
    lines = text.count("\n") + (1 if text else 0)
    return lines, len(text)

  def _refresh_status_line(self):
    lines, chars = self._input_stats()
    self.status_var.set(
      f"Status: {self._status_message}   |   Lines: {lines}   |   Chars: {chars}"
    )

  def _update_status(self, message: str):
    self._status_message = message
    self._refresh_status_line()

  def _on_input_stats_changed(self, _event=None):
    self._refresh_status_line()

  # ── Formatting pipeline ─────────────────────────────────────────────────────

  def _on_input_changed(self, _event=None):
    if not self.input_box.edit_modified():
      return
    self.input_box.edit_modified(False)
    self._auto_format()

  def _auto_format(self):
    raw = self.input_box.get("1.0", "end-1c")
    if not raw.strip():
      self._set_output("")
      self._update_status("Ready")
      return
    self._update_status("Formatting...")
    self._run_format()

  def _run_format(self):
    try:
      raw = self.input_box.get("1.0", "end-1c")
      if not raw.strip():
        self._set_output("")
        self._update_status("Ready")
        return

      spec = resolve_formatter(self._active_mode, raw)
      result = spec.format_fn(raw)
      self._set_output(result)

      if self._active_mode == AUTO_DETECT_KEY:
        detected = resolve_formatter("auto", raw)
        self._update_status(f"Formatted successfully ({detected.label}).")
      else:
        self._update_status("Formatted successfully.")
    except Exception as exc:
      messagebox.showerror("Format Error", f"Could not format data:\n{exc}")
      self._update_status("Error formatting data.")

  def _set_output(self, text: str):
    """Update output while preserving cursor position when possible."""
    cursor = self.output_box.index(tk.INSERT)
    scroll = self.output_box.yview()

    self.output_box.delete("1.0", "end")
    self.output_box.insert("1.0", text)

    try:
      self.output_box.mark_set(tk.INSERT, cursor)
    except tk.TclError:
      self.output_box.mark_set(tk.INSERT, "end")

    self.output_box.yview_moveto(scroll[0])

  # ── Actions ─────────────────────────────────────────────────────────────────

  def _paste_clipboard(self):
    try:
      raw = self.root.clipboard_get()
    except tk.TclError:
      self._update_status("Clipboard is empty.")
      return

    if not raw.strip():
      self._update_status("Clipboard is empty.")
      return

    self.input_box.delete("1.0", "end")
    self.input_box.insert("1.0", raw)
    self._update_status("Formatting...")
    self._run_format()

  def _copy_output(self):
    txt = self.output_box.get("1.0", "end-1c")
    if not txt.strip():
      self._update_status("Nothing to copy.")
      return
    self.root.clipboard_clear()
    self.root.clipboard_append(txt)
    self._update_status("Output copied.")

  def _clear_fields(self):
    self.input_box.delete("1.0", "end")
    self.output_box.delete("1.0", "end")
    self._update_status("Ready")

  def _save_output(self):
    txt = self.output_box.get("1.0", "end-1c")
    if not txt.strip():
      self._update_status("Nothing to save.")
      return

    file_path = filedialog.asksaveasfilename(
      defaultextension=".txt",
      filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
      initialfile="Formatted_Load.txt",
      title="Save Output As",
    )
    if not file_path:
      return

    try:
      with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(txt)
      self._update_status("Saved successfully.")
    except OSError as exc:
      messagebox.showerror("Save Error", f"Could not save file:\n{exc}")
      self._update_status("Save failed.")

  def _show_about(self):
    messagebox.showinfo(
      "About Load Formatter Pro",
      "Load Formatter Pro\n\n"
      "Version: 3.0\n\n"
      "Multi load-board formatter supporting DAT, Sylectus,\n"
      "and automatic format detection.\n\n"
      "Developed by Syed M. Taqi\n"
      "Copyright © 2026 6coDev",
    )
