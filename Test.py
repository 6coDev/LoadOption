# ==============================================================================
#  DAT Formatter v2.0
#  Author      : 6coDev
#  License     : MIT License
#  Copyright   : © 2026 6coDev
#  Description : Parses and formats DAT load postings into a clean structured
#                layout.  Pure Python + tkinter — no external dependencies.
#
#  To compile to a standalone Windows .exe (no Python install needed):
#    pip install pyinstaller
#    pyinstaller --onefile --windowed --name "DATFormatter_v2" DATFormatter_v2.py
#
#  The resulting exe will be in the  dist/  folder.
# ==============================================================================
#  FUTURE HOOKS (stubs / comments mark extension points):
#    - Settings dialog
#    - Light / dark theme toggle
#    - Automatic update checker
#    - Open DAT text file directly
#    - Drag-and-drop support
#    - Export to PDF
# ==============================================================================

import re
import tkinter as tk
from tkinter import filedialog, messagebox

# ── Colour palette (dark theme) ───────────────────────────────────────────────
BG_MAIN   = "#202020"   # window background
BG_BOX    = "#2B2B2B"   # textbox background
BG_BTN    = "#303030"   # button background
BG_STATUS = "#282828"   # status bar background
FG_TEXT   = "#FFFFFF"   # all foreground text
FG_STATUS = "#CCCCCC"   # status bar text (slightly dimmed)
FONT_UI   = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)


# ==============================================================================
#  format_dat(input_text) -> str
#
#  Core parsing engine — direct port of the original AHK v1.0 logic.
#  Receives raw DAT posting text, returns formatted output string.
#  No clipboard access; the GUI passes text in and gets the result back.
# ==============================================================================
def format_dat(input_text: str) -> str:

    # ── 1. Normalize line endings (strip CR, match original) ──────────────────
    text = input_text.replace("\r", "").strip()

    if not text:
        return ""

    lines = text.split("\n")

    # ── 2. Initialise fields with v1.0 defaults ───────────────────────────────
    pickup          = ""
    delivery        = ""
    pickup_details  = ""
    delivery_details = ""
    loaded_miles    = ""
    dead_head       = ""
    paying          = ""
    weight          = ""
    commodity       = ""
    truck           = ""
    load_type       = ""
    length          = ""
    mc              = ""
    company         = ""

    # ── 3. Pickup & Delivery locations + Dead Head ────────────────────────────
    #  Scan every line for "City, ST (number)" pattern.
    #  First match  → pickup + dead_head
    #  Second match → delivery
    locs = []

    for line in lines:
        line_stripped = line.strip()

        # Match: <anything> (digits) at end of line
        m = re.match(r"^(.*?)\s*\((\d+)\)$", line_stripped)
        if m:
            city   = m.group(1).strip()
            number = m.group(2)

            # Validate: "Word(s), XX" city/state format
            if re.match(r"^[A-Za-z .'\-]+,\s*[A-Z]{2}$", city):
                locs.append(city)
                if len(locs) == 1:
                    dead_head = number

    if len(locs) >= 1:
        pickup = locs[0]
    if len(locs) >= 2:
        delivery = locs[1]

    # ── 4. Pickup details ─────────────────────────────────────────────────────
    #  Find the line containing the pickup city, read next 1–2 lines.
    #  Second line included only if it starts with a date (YYYY-MM-DD).
    idx = -1

    if pickup:
        for i, line in enumerate(lines):
            if pickup in line.strip():
                idx = i
                break

    if idx >= 0:
        if idx + 1 < len(lines):
            pickup_details = lines[idx + 1].strip()
        if idx + 2 < len(lines):
            nxt = lines[idx + 2].strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}", nxt):
                pickup_details += "\n" + nxt

    # ── 5. Delivery details ───────────────────────────────────────────────────
    #  Find delivery city line, read next 1–2 lines that start with a date.
    idx2 = -1

    if delivery:
        for i, line in enumerate(lines):
            if delivery in line.strip():
                idx2 = i
                break

    if idx2 >= 0:
        if idx2 + 1 < len(lines):
            nxt1 = lines[idx2 + 1].strip()
            if re.match(r"^\d{4}-", nxt1):
                delivery_details = nxt1
        if idx2 + 2 < len(lines):
            nxt2 = lines[idx2 + 2].strip()
            if re.match(r"^\d{4}-", nxt2):
                delivery_details += "\n" + nxt2

    # ── 6. Loaded miles ───────────────────────────────────────────────────────
    m = re.search(r"(\d+)\s*mi", text)
    if m:
        loaded_miles = m.group(1)

    # ── 7. Paying ─────────────────────────────────────────────────────────────
    m = re.search(r"\$[\d,]+", text)
    if m:
        paying = m.group(0)

    # ── 8. Weight ─────────────────────────────────────────────────────────────
    m = re.search(r"\d{1,3}(?:,\d{3})*\s*lbs", text)
    if m:
        weight = m.group(0)

    # ── 9. Commodity ──────────────────────────────────────────────────────────
    m = re.search(r"Commodity\s*\n([^\n]+)", text)
    if m:
        commodity = m.group(1).strip()

    # ── 10. Truck (Equipment) ─────────────────────────────────────────────────
    m = re.search(r"Truck\s*\n([^\n]+)", text)
    if m:
        truck = m.group(1).strip()

    # ── 11. Load type ─────────────────────────────────────────────────────────
    m = re.search(r"Load\s*\n([^\n]+)", text)
    if m:
        load_type = m.group(1).strip()

    # ── 12. Trailer length ────────────────────────────────────────────────────
    m = re.search(r"Length\s*\n([^\n]+)", text)
    if m:
        length = m.group(1).strip()

    # ── 13. MC number ─────────────────────────────────────────────────────────
    m = re.search(r"MC#\s*(\d+)", text)
    if m:
        mc = m.group(1)

    # ── 14. Company name ──────────────────────────────────────────────────────
    m = re.search(r"Company\s*\nVIEW IN DIRECTORY\s*\n([^\n]+)", text)
    if m:
        company = m.group(1).strip()

    # ── 15. Build details block ───────────────────────────────────────────────
    details_parts = []

    if weight:
        details_parts.append(weight)
    if commodity and commodity != "–":
        details_parts.append("Commodity: " + commodity)
    if truck:
        details_parts.append("Equipment: " + truck)
    if load_type:
        details_parts.append("Load: " + load_type)
    if length:
        details_parts.append("Length: " + length)

    details = "\n".join(details_parts)

    # ── 16. Final output — identical format to v1.0 ───────────────────────────
    output = (
        f"{pickup} ------- {delivery}\n"
        f"\n"
        f"Loaded miles: {loaded_miles}\n"
        f"\n"
        f"D-H: {dead_head}\n"
        f"\n"
        f"Paying: {paying}\n"
        f"\n"
        f"Pickup:\n"
        f"{pickup_details}\n"
        f"\n"
        f"Delivery:\n"
        f"{delivery_details}\n"
        f"\n"
        f"{details}\n"
        f"\n"
        f"MC: {mc}\n"
        f"\n"
        f"{company}"
    )

    return output


# ==============================================================================
#  DATFormatterApp
#  Main application class — builds the GUI and wires all events.
# ==============================================================================
class DATFormatterApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self._build_window()
        self._build_menu()
        self._build_ui()
        self._update_status("Ready")

    # ── Window setup ──────────────────────────────────────────────────────────
    def _build_window(self):
        self.root.title("DAT Formatter v2.0")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(900, 700)

        # Center on screen
        self.root.update_idletasks()
        w, h = 920, 720
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Make rows/columns resize proportionally
        self.root.columnconfigure(0, weight=1)
        # Row weights: label=0, input box=1, buttons=0, label=0, output box=1, buttons=0, status=0
        for row, weight in enumerate([0, 1, 0, 0, 1, 0, 0]):
            self.root.rowconfigure(row, weight=weight)

    # ── Menu bar ──────────────────────────────────────────────────────────────
    def _build_menu(self):
        menubar  = tk.Menu(self.root, bg=BG_BTN, fg=FG_TEXT,
                           activebackground="#404040", activeforeground=FG_TEXT,
                           relief="flat", bd=0)
        help_menu = tk.Menu(menubar, tearoff=0, bg=BG_BTN, fg=FG_TEXT,
                            activebackground="#404040", activeforeground=FG_TEXT)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    # ── Main UI layout ────────────────────────────────────────────────────────
    def _build_ui(self):
        PAD = 10   # outer padding

        # ── INPUT label ───────────────────────────────────────────────────────
        tk.Label(self.root, text="INPUT", bg=BG_MAIN, fg=FG_TEXT,
                 font=FONT_UI, anchor="w"
                 ).grid(row=0, column=0, sticky="ew", padx=PAD, pady=(PAD, 2))

        # ── Input textbox ─────────────────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_BOX)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=PAD, pady=0)
        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)

        self.input_box = tk.Text(
            input_frame,
            bg=BG_BOX, fg=FG_TEXT,
            insertbackground=FG_TEXT,   # cursor colour
            font=FONT_MONO,
            wrap="none",
            relief="flat",
            bd=4,
            undo=True,
        )
        self.input_box.grid(row=0, column=0, sticky="nsew")

        input_scroll_y = tk.Scrollbar(input_frame, orient="vertical",
                                      command=self.input_box.yview)
        input_scroll_y.grid(row=0, column=1, sticky="ns")
        self.input_box.configure(yscrollcommand=input_scroll_y.set)

        # Auto-format on every keystroke
        self.input_box.bind("<<Modified>>", self._on_input_changed)

        # ── Input buttons ─────────────────────────────────────────────────────
        input_btn_frame = tk.Frame(self.root, bg=BG_MAIN)
        input_btn_frame.grid(row=2, column=0, sticky="w", padx=PAD, pady=4)

        self._make_button(input_btn_frame, "Paste",
                          self._paste_clipboard).pack(side="left", padx=(0, 6))
        self._make_button(input_btn_frame, "Clear",
                          self._clear_fields).pack(side="left")

        # ── OUTPUT label ──────────────────────────────────────────────────────
        tk.Label(self.root, text="OUTPUT", bg=BG_MAIN, fg=FG_TEXT,
                 font=FONT_UI, anchor="w"
                 ).grid(row=3, column=0, sticky="ew", padx=PAD, pady=(6, 2))

        # ── Output textbox (read-only) ────────────────────────────────────────
        output_frame = tk.Frame(self.root, bg=BG_BOX)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=PAD, pady=0)
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_box = tk.Text(
            output_frame,
            bg=BG_BOX, fg=FG_TEXT,
            insertbackground=FG_TEXT,
            font=FONT_MONO,
            wrap="none",
            relief="flat",
            bd=4,
            state="disabled",   # read-only
        )
        self.output_box.grid(row=0, column=0, sticky="nsew")

        output_scroll_y = tk.Scrollbar(output_frame, orient="vertical",
                                       command=self.output_box.yview)
        output_scroll_y.grid(row=0, column=1, sticky="ns")
        self.output_box.configure(yscrollcommand=output_scroll_y.set)

        # ── Output buttons ────────────────────────────────────────────────────
        output_btn_frame = tk.Frame(self.root, bg=BG_MAIN)
        output_btn_frame.grid(row=5, column=0, sticky="w", padx=PAD, pady=4)

        self._make_button(output_btn_frame, "Copy Output",
                          self._copy_output).pack(side="left", padx=(0, 6))
        self._make_button(output_btn_frame, "Save Output",
                          self._save_output).pack(side="left")

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="  Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=BG_STATUS, fg=FG_STATUS,
            font=("Segoe UI", 9),
            anchor="w",
            relief="flat",
            bd=1,
        )
        status_bar.grid(row=6, column=0, sticky="ew", padx=0, pady=0)

    # ── Button factory ────────────────────────────────────────────────────────
    def _make_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=BG_BTN, fg=FG_TEXT,
            activebackground="#404040", activeforeground=FG_TEXT,
            font=FONT_UI,
            relief="flat",
            bd=0,
            padx=14, pady=6,
            cursor="hand2",
        )
        # Hover highlight
        btn.bind("<Enter>", lambda e: btn.configure(bg="#404040"))
        btn.bind("<Leave>", lambda e: btn.configure(bg=BG_BTN))
        return btn

    # ── Status bar helper ─────────────────────────────────────────────────────
    def _update_status(self, msg: str):
        self.status_var.set("  " + msg)

    # ── Input change handler ──────────────────────────────────────────────────
    def _on_input_changed(self, event=None):
        # tkinter fires <<Modified>> once after a change; must reset the flag
        # so future changes fire again.
        if not self.input_box.edit_modified():
            return
        self.input_box.edit_modified(False)
        self._auto_format()

    # ── Auto-format ───────────────────────────────────────────────────────────
    def _auto_format(self):
        raw = self.input_box.get("1.0", "end-1c")
        if not raw.strip():
            self._set_output("")
            self._update_status("Ready")
            return
        self._update_status("Formatting...")
        self._run_format()

    # ── Run format ────────────────────────────────────────────────────────────
    def _run_format(self):
        try:
            raw    = self.input_box.get("1.0", "end-1c")
            result = format_dat(raw)
            self._set_output(result)
            self._update_status("Formatted successfully.")
        except Exception as e:
            self._update_status("Error formatting data.")

    # ── Set output box content ────────────────────────────────────────────────
    def _set_output(self, text: str):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.configure(state="disabled")

    # ── Paste clipboard ───────────────────────────────────────────────────────
    def _paste_clipboard(self):
        try:
            raw = self.root.clipboard_get()
        except tk.TclError:
            self._update_status("Clipboard is empty.")
            return

        if not raw.strip():
            self._update_status("Clipboard is empty.")
            return

        # Replace input box content with clipboard text
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", raw)
        # Manually trigger format (insert doesn't fire <<Modified>> reliably)
        self._update_status("Formatting...")
        self._run_format()

    # ── Copy output ───────────────────────────────────────────────────────────
    def _copy_output(self):
        txt = self.output_box.get("1.0", "end-1c")
        if not txt.strip():
            self._update_status("Nothing to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        self._update_status("Output copied to clipboard.")

    # ── Clear fields ──────────────────────────────────────────────────────────
    def _clear_fields(self):
        self.input_box.delete("1.0", "end")
        self._set_output("")
        self._update_status("Ready")

    # ── Save output ───────────────────────────────────────────────────────────
    def _save_output(self):
        txt = self.output_box.get("1.0", "end-1c")
        if not txt.strip():
            self._update_status("Nothing to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile="DAT_Load.txt",
            title="Save Output As",
        )
        if not file_path:
            return   # user cancelled

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(txt)
            self._update_status("Saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")
            self._update_status("Save failed.")

    # ── About dialog ──────────────────────────────────────────────────────────
    def _show_about(self):
        messagebox.showinfo(
            "About DAT Formatter",
            "DAT Formatter\n\n"
            "Version: v2.0\n\n"
            "Developed by\n6coDev\n\n"
            "Licensed under MIT License\n"
            "Copyright © 2026 6coDev",
        )


# ==============================================================================
#  Entry point
# ==============================================================================
def main():
    root = tk.Tk()
    app  = DATFormatterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()