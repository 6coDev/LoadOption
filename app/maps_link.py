"""Build Google Maps directions URLs from formatted load output."""

import re
from urllib.parse import quote_plus

_ROUTE_LINE_RE = re.compile(r"^(.+?)\s*(?:-------|>>>>>>>+)\s*(.+)$")


def extract_route_from_output(text: str) -> tuple[str, str] | None:
    """Return (pickup, delivery) parsed from the first line of formatted output."""
    for line in text.replace("\r", "").split("\n"):
        line = line.strip()
        if not line:
            continue
        match = _ROUTE_LINE_RE.match(line)
        if match:
            pickup = match.group(1).strip()
            delivery = match.group(2).strip()
            if pickup and delivery:
                return pickup, delivery
        break
    return None


def build_maps_directions_url(pickup: str, delivery: str) -> str:
    """Return a Google Maps driving directions URL."""
    origin = quote_plus(pickup)
    destination = quote_plus(delivery)
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}&destination={destination}&travelmode=driving"
    )
