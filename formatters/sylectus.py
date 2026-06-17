"""Sylectus load board text formatter — port of original AHK v2.0 logic."""

import re


# Lines skipped when scanning for company name
_COMPANY_SKIP = re.compile(
    r"Days to Pay|Credit|S\.A\.F\.E\.R|Sprinter|Van|Straight|Large|Cargo|^\d+$"
)

_CITY_RE = re.compile(r"([A-Z ]+, [A-Z]{2} \d{5})")
_TIME_RE = re.compile(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}|ASAP|Deliver Direct")
_NUMBERS_LINE_RE = re.compile(r"^\d+(\s+\d+)*$")
_MC_RE = re.compile(r"^(\d{5,10})\s+\d+")


def format_sylectus(input_text: str) -> str:
    """Parse raw Sylectus posting text and return a formatted output string."""
    text = input_text.replace("\r", "").strip()
    if not text:
        return ""

    lines = [line.strip() for line in text.split("\n")]

    # Company — first real text line
    company = ""
    for line in lines:
        if line and not _COMPANY_SKIP.search(line):
            company = line
            break

    # MC number — safe extraction
    mc = ""
    for line in lines:
        m = _MC_RE.match(line)
        if m:
            mc = m.group(1)
            break

    # Pickup + delivery cities and times
    cities: list[str] = []
    times: list[str] = []

    for line in lines:
        pos = 0
        while True:
            m = _CITY_RE.search(line, pos)
            if not m:
                break
            cities.append(m.group(1))
            pos = m.end()

        tm = _TIME_RE.search(line)
        if tm:
            times.append(tm.group(0))

    pickup_city = cities[0] if len(cities) >= 1 else ""
    delivery_city = cities[1] if len(cities) >= 2 else ""
    pickup_time = times[0] if len(times) >= 1 else ""
    delivery_time = times[1] if len(times) >= 2 else ""

    # Miles + weight — lines containing only digits (space/tab separated)
    numbers: list[str] = []
    for line in lines:
        if _NUMBERS_LINE_RE.match(line):
            numbers.append(line)

    miles = ""
    weight = ""

    if numbers:
        last_parts = re.split(r"[\s\t]+", numbers[-1])
        weight = last_parts[-1]

    if len(numbers) >= 2:
        prev_parts = re.split(r"[\s\t]+", numbers[-2])
        miles = prev_parts[0]

    return (
        f"{pickup_city} >>>>>>>> {delivery_city}\n"
        f"\n"
        f"Loaded Miles: {miles}\n"
        f"\n"
        f"DH:\n"
        f"\n"
        f"Paying: $\n"
        f"\n"
        f"Weight: {weight} lbs\n"
        f"\n"
        f"Pickup:\n"
        f"{pickup_city}\n"
        f"{pickup_time}\n"
        f"\n"
        f"Delivery:\n"
        f"{delivery_city}\n"
        f"{delivery_time}\n"
        f"\n"
        f"Company: {company}\n"
        f"MC: {mc}"
    )
