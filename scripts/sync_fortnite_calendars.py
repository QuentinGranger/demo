#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from validate_fortnite_ics import normalize_ics_bytes, split_universal_lines, unfold_lines

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
GLOBAL = CAL / "fortnite-paris.ics"
UPDATES = CAL / "fortnite-updates-france.ics"
COMPETITIVE = CAL / "fortnite-competitive-france.ics"


def logical_lines(path: Path) -> list[str]:
    text = path.read_bytes().decode("utf-8-sig")
    physical = split_universal_lines(text)
    while physical and physical[-1] == "":
        physical.pop()
    return unfold_lines(physical)


def extract_events(lines: list[str]) -> list[list[str]]:
    events: list[list[str]] = []
    current: list[str] | None = None
    depth = 0
    for line in lines:
        if line == "BEGIN:VEVENT":
            if current is not None:
                raise RuntimeError("nested VEVENT")
            current = [line]
            depth = 1
            continue
        if current is not None:
            current.append(line)
            if line.startswith("BEGIN:"):
                depth += 1
            elif line.startswith("END:"):
                depth -= 1
                if depth == 0:
                    if line != "END:VEVENT":
                        raise RuntimeError("VEVENT closed by unexpected component")
                    events.append(current)
                    current = None
    if current is not None:
        raise RuntimeError("unclosed VEVENT")
    return events


def event_uid(event: list[str]) -> str:
    matches = [line[4:].strip() for line in event if line.startswith("UID:")]
    if len(matches) != 1 or not matches[0]:
        raise RuntimeError("every VEVENT must have exactly one non-empty UID")
    return matches[0]


def global_header(lines: list[str]) -> list[str]:
    try:
        first_event = lines.index("BEGIN:VEVENT")
        return lines[:first_event]
    except ValueError:
        if not lines or lines[-1] != "END:VCALENDAR":
            raise RuntimeError("global calendar missing END:VCALENDAR")
        return lines[:-1]


def main() -> int:
    global_lines = logical_lines(GLOBAL)
    update_events = extract_events(logical_lines(UPDATES))
    competitive_events = extract_events(logical_lines(COMPETITIVE))

    ordered_events = update_events + competitive_events
    seen: set[str] = set()
    for event in ordered_events:
        uid = event_uid(event)
        if uid in seen:
            raise RuntimeError(f"UID exists in more than one specialist feed: {uid}")
        seen.add(uid)

    merged: list[str] = global_header(global_lines)
    for event in ordered_events:
        merged.extend(event)
    merged.append("END:VCALENDAR")

    GLOBAL.write_bytes(("\r\n".join(merged) + "\r\n").encode("utf-8"))

    # Normalize all three feeds so every physical line is RFC 5545-safe and
    # specialist/global event signatures remain identical after unfolding.
    for path in (UPDATES, COMPETITIVE, GLOBAL):
        path.write_bytes(normalize_ics_bytes(path.read_bytes()))

    print(
        f"SYNCED: {len(update_events)} update event(s) + "
        f"{len(competitive_events)} competitive event(s) = {len(ordered_events)} global event(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
