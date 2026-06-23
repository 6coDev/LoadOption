"""DAT load board text formatter."""

import re


def format_dat(input_text: str) -> str:
    """Parse raw DAT posting text and return a formatted output string."""
    text = input_text.replace("\r", "").strip()

    if not text:
        return ""

    lines = text.split("\n")

    pickup = ""
    delivery = ""
    pickup_details = ""
    delivery_details = ""
    loaded_miles = ""
    dead_head = ""
    paying = ""
    weight = ""
    commodity = ""
    truck = ""
    load_type = ""
    length = ""
    mc = ""
    company = ""

    # Detect "City, ST" location lines, with or without a trailing dead-head
    # number in parentheses — e.g. both "Zion, IL (15)" and "Naperville, IL"
    # are recognised as valid pickup/delivery candidates. When the
    # parentheses ARE present, that number is still captured as Dead Head
    # for the first (pickup) location only — matching original behaviour.
    locs = []
    for line in lines:
        line_stripped = line.strip()

        # Try the "City, ST (number)" form first
        m = re.match(r"^(.*?)\s*\((\d+)\)$", line_stripped)
        if m:
            city = m.group(1).strip()
            number = m.group(2)
        else:
            # Fall back to a bare "City, ST" line — no parentheses needed
            m = re.match(r"^([A-Za-z .'\-]+,\s*[A-Z]{2})$", line_stripped)
            if not m:
                continue
            city = m.group(1).strip()
            number = ""

        if re.match(r"^[A-Za-z .'\-]+,\s*[A-Z]{2}$", city):
            locs.append(city)
            if len(locs) == 1 and number:
                dead_head = number

    if len(locs) >= 1:
        pickup = locs[0]
    if len(locs) >= 2:
        delivery = locs[1]

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

    m = re.search(r"(\d+)\s*mi", text)
    if m:
        loaded_miles = m.group(1)

    m = re.search(r"\$[\d,]+", text)
    if m:
        paying = m.group(0)

    m = re.search(r"\d{1,3}(?:,\d{3})*\s*lbs", text)
    if m:
        weight = m.group(0)

    m = re.search(r"Commodity\s*\n([^\n]+)", text)
    if m:
        commodity = m.group(1).strip()

    m = re.search(r"Truck\s*\n([^\n]+)", text)
    if m:
        truck = m.group(1).strip()

    m = re.search(r"Load\s*\n([^\n]+)", text)
    if m:
        load_type = m.group(1).strip()

    m = re.search(r"Length\s*\n([^\n]+)", text)
    if m:
        length = m.group(1).strip()

    m = re.search(r"MC#\s*(\d+)", text)
    if m:
        mc = m.group(1)

    m = re.search(r"Company\s*\nVIEW IN DIRECTORY\s*\n([^\n]+)", text)
    if m:
        company = m.group(1).strip()

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

    return (
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
