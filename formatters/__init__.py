"""Load board formatters package."""

from formatters.dat import format_dat
from formatters.detect import detect_formatter_key, resolve_formatter
from formatters.registry import (
  AUTO_DETECT_KEY,
  AUTO_DETECT_SPEC,
  FORMATTER_REGISTRY,
  FormatterSpec,
  get_all_mode_keys,
  get_formatter_keys,
)
from formatters.sylectus import format_sylectus

__all__ = [
  "AUTO_DETECT_KEY",
  "AUTO_DETECT_SPEC",
  "FORMATTER_REGISTRY",
  "FormatterSpec",
  "detect_formatter_key",
  "format_dat",
  "format_sylectus",
  "get_all_mode_keys",
  "get_formatter_keys",
  "resolve_formatter",
]
