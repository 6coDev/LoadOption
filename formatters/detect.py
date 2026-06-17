"""Auto-detect which load board formatter to use."""

from formatters.registry import FORMATTER_REGISTRY, FormatterSpec


def detect_formatter_key(text: str) -> str:
  """
  Inspect pasted text and return the registry key of the best-matching formatter.
  Falls back to DAT when no clear match is found.
  """
  if not text.strip():
    return "dat"

  scores: dict[str, int] = {}

  for key, spec in FORMATTER_REGISTRY.items():
    score = 0
    for pattern in spec.detect_patterns:
      if pattern in text:
        score += 1
    scores[key] = score

  best_key = max(scores, key=scores.get)
  if scores[best_key] > 0:
    return best_key

  return "dat"


def resolve_formatter(mode_key: str, text: str) -> FormatterSpec:
  """Return the FormatterSpec to use for the given mode and input text."""
  if mode_key == "auto":
    detected = detect_formatter_key(text)
    return FORMATTER_REGISTRY[detected]
  return FORMATTER_REGISTRY[mode_key]
