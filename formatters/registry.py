"""Formatter registry — add new load boards here without touching the GUI."""

from dataclasses import dataclass
from typing import Callable

from formatters.dat import format_dat
from formatters.sylectus import format_sylectus


@dataclass(frozen=True)
class FormatterSpec:
  key: str
  label: str
  icon: str
  format_fn: Callable[[str], str]
  detect_patterns: tuple[str, ...]


AUTO_DETECT_KEY = "auto"

FORMATTER_REGISTRY: dict[str, FormatterSpec] = {
  "dat": FormatterSpec(
    key="dat",
    label="DAT",
    icon="🚛",
    format_fn=format_dat,
    detect_patterns=("MC#", "VIEW IN DIRECTORY", "Commodity"),
  ),
  "sylectus": FormatterSpec(
    key="sylectus",
    label="Sylectus",
    icon="🚚",
    format_fn=format_sylectus,
    detect_patterns=(
      "Days to Pay",
      "S.A.F.E.R",
      "Deliver Direct",
      "Sprinter",
      "Sylectus",
    ),
  ),
}

AUTO_DETECT_SPEC = FormatterSpec(
  key=AUTO_DETECT_KEY,
  label="Auto Detect",
  icon="🤖",
  format_fn=format_dat,
  detect_patterns=(),
)


def get_formatter_keys() -> list[str]:
  return list(FORMATTER_REGISTRY.keys())


def get_all_mode_keys() -> list[str]:
  return get_formatter_keys() + [AUTO_DETECT_KEY]
