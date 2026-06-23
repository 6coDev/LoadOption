"""
Tab session model for Load Formatter Pro.

Each open tab keeps its own input text, output text, and active formatter
mode. The GUI uses ONE shared Input Text widget and ONE shared Output Text
widget — switching tabs saves the current widget contents into the
previously-active TabSession, then loads the newly-selected TabSession's
saved content back into those same widgets. This mirrors how Notepad++
behaves: one editor view, content swapped per tab, rather than spinning up
a separate pair of widgets per tab (which would be heavier and harder to
theme consistently).
"""

from dataclasses import dataclass, field

_next_id = 1


def _generate_tab_id() -> int:
  """Return a fresh, unique integer id for a new tab."""
  global _next_id
  new_id = _next_id
  _next_id += 1
  return new_id


@dataclass
class TabSession:
  """Holds everything needed to restore one tab's editor state."""

  tab_id: int
  title: str = "Untitled"
  input_text: str = ""
  output_text: str = ""
  active_mode: str = "dat"          # "dat" | "sylectus" | "auto"
  detected_label: str = ""          # filled in when active_mode == "auto"
  status_message: str = "Ready"

  @classmethod
  def create(cls, title: str = "", default_mode: str = "dat") -> "TabSession":
    tab_id = _generate_tab_id()
    return cls(
      tab_id=tab_id,
      title=title or "New Tab",
      active_mode=default_mode,
    )

  def short_title(self, max_len: int = 14) -> str:
    """Title clipped for the tab chip — keeps the tab strip compact."""
    if len(self.title) <= max_len:
      return self.title
    return self.title[: max_len - 1].rstrip() + "…"
