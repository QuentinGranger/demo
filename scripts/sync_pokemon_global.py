#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
SOURCES = [CAL / "pokemon-tcg-france.ics", CAL / "pokemon-events-france-paris.ics"]
TARGET = CAL / "pokemon-paris.ics"

HEADER = """BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//OpenAI//Pokemon Calendars//FR\r\nCALSCALE:GREGORIAN\r\nMETHOD:PUBLISH\r\nX-WR-CALNAME:⭐ Pokémon — Tout (France & Paris)\r\nX-WR-TIMEZONE:Europe/Paris\r\nX-POKEMON-REMINDER-POLICY:TYPE_FIRST_V2\r\nX-POKEMON-PRICE-POLICY:OFFICIAL_EUR_EXACT_SKU_V2\r\nX-POKEMON-WAVE-POLICY:ONE_EVENT_CHECKLIST_V2\r\nX-POKEMON-LOCATION-POLICY:FULL_ADDRESS_GEO_TICKETING_MAPS_V2\r\nX-POKEMON-CHANGE-POLICY:UID_STABLE_HISTORY_V1\r\nX-POKEMON-RETAILER-POLICY:RETAILER_WATCH_ALL_FR_V2\r\n"""


def unfold(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def event_blocks(text: str):
    normalized = unfold(text)
    return re.findall(r"BEGIN:VEVENT\n.*?\nEND:VEVENT", normalized, flags=re.S)


def uid_of(block: str) -> str:
    m = re.search(r"^UID:(.+)$", block, flags=re.M)
    if not m:
        raise ValueError("VEVENT without UID")
    return m.group(1).strip()


def dtstart_key(block: str):
    m = re.search(r"^DTSTART(?:;[^:]*)?:(.+)$", block, flags=re.M)
    value = m.group(1).strip() if m else "99999999"
    digits = re.sub(r"[^0-9]", "", value)
    return (digits or "99999999", uid_of(block))


def to_crlf(block: str) -> str:
    return block.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")


def main():
    events = {}
    for path in SOURCES:
        text = path.read_text(encoding="utf-8")
        if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
            raise SystemExit(f"invalid source calendar: {path}")
        for block in event_blocks(text):
            uid = uid_of(block)
            if uid in events and events[uid] != block:
                raise SystemExit(f"conflicting duplicate UID across specialists: {uid}")
            events[uid] = block

    ordered = sorted(events.values(), key=dtstart_key)
    output = HEADER + "\r\n".join(to_crlf(block) for block in ordered) + "\r\nEND:VCALENDAR\r\n"

    old = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
    old_norm = old.replace("\r\n", "\n").replace("\r", "\n")
    new_norm = output.replace("\r\n", "\n")
    if old_norm == new_norm:
        print("Pokémon global calendar already synchronized")
        return

    TARGET.write_bytes(output.encode("utf-8"))
    print(f"Synchronized {TARGET}: {len(ordered)} unique VEVENTs")


if __name__ == "__main__":
    main()
