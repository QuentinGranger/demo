#!/usr/bin/env python3
from pathlib import Path
import re
import sys

UID = "hp-back-to-hogwarts-showcase-20260901@openai"
STAMP = "20260831T014332Z"
UPDATE_UNTIL = "20260903T014332Z"
SOURCE_URL = "https://www.youtube.com/watch?v=2dHaAeLsLmo"
FILES = [
    Path("calendars/harry-potter-events-france-paris.ics"),
    Path("calendars/harry-potter-paris.ics"),
]

NEW_BLOCK = f"""BEGIN:VEVENT
UID:{UID}
DTSTAMP:{STAMP}
LAST-MODIFIED:{STAMP}
SEQUENCE:1
STATUS:CONFIRMED
PRIORITY:5
X-HARRYPOTTER-PRIORITY:IMPORTANT
X-HARRYPOTTER-REMINDER-PROFILE:MEDIA_IMPORTANT
X-HARRYPOTTER-ACTION:WATCH
X-HARRYPOTTER-EVENT-TYPE:MEDIA_PREMIERE
X-HARRYPOTTER-FORMAT:ONLINE_SHOWCASE
X-HARRYPOTTER-MARKET:FR
X-HARRYPOTTER-END-TIME-STATUS:UNKNOWN
X-HARRYPOTTER-FIRST-ADDED-AT:20260819T040500Z
X-HARRYPOTTER-LAST-MAJOR-UPDATE-AT:{STAMP}
X-HARRYPOTTER-UPDATE-UNTIL:{UPDATE_UNTIL}
X-HARRYPOTTER-UPDATE-REASON:OFFICIAL_TIME_CONFIRMED
X-HARRYPOTTER-FRESHNESS:UPDATED
X-HARRYPOTTER-BADGE:UPDATED
X-HARRYPOTTER-ORIGINAL-DTSTART;VALUE=DATE:20260901
X-HARRYPOTTER-ORIGINAL-DTEND;VALUE=DATE:20260902
X-HARRYPOTTER-PREVIOUS-DTSTART;VALUE=DATE:20260901
X-HARRYPOTTER-PREVIOUS-DTEND;VALUE=DATE:20260902
X-HARRYPOTTER-CHANGE-COUNT:1
X-HARRYPOTTER-CURRENT-DATE-STATUS:CONFIRMED_TIME
X-HARRYPOTTER-CHANGE-SOURCE:{SOURCE_URL}
X-HARRYPOTTER-CHANGE-DETECTED-AT:{STAMP}
X-HARRYPOTTER-DATE-HISTORY:20260901 ALLDAY -> 20260901T180000 Europe/Paris (official showcase time confirmed)
DTSTART;TZID=Europe/Paris:20260901T180000
SUMMARY:⭐ ✅ ✨ 📡 Back to Hogwarts Showcase 2026 — 18h00
LOCATION:En ligne — chaîne officielle Harry Potter / YouTube / TikTok
DESCRIPTION:Priorité : ⭐ Important — rendez-vous officiel Back to Hogwarts avec annonces et célébration de la franchise.\\nFiabilité : ✅ Heure confirmée directement par la chaîne YouTube officielle Harry Potter.\\nHoraire : mardi 1er septembre 2026 à 18h00 heure de Paris (17h00 BST publié par Harry Potter).\\nDiffusion : chaîne officielle Harry Potter sur YouTube ; HarryPotter.com indique également YouTube et TikTok pour le direct.\\nHeure de fin : inconnue — aucune durée officielle n'est affirmée.\\n✨ Mise à jour majeure détectée le 31 août 2026 : l'heure exacte est désormais officielle.\\nRappels : J-1 et H-1 ; aucun rappel passé n'est créé.\\nSource horaire : {SOURCE_URL}\\nSource événement : https://www.harrypotter.com/news/how-to-celebrate-back-to-hogwarts-2026
URL:{SOURCE_URL}
CATEGORIES:Harry Potter,Back to Hogwarts,En ligne,Showcase,Mise à jour,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:📡 Back to Hogwarts Showcase demain à 18h — chaîne officielle Harry Potter
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:📡 Back to Hogwarts Showcase dans 1 heure — direct à 18h
END:VALARM
END:VEVENT"""


def find_event(text: str, uid: str):
    pattern = re.compile(r"BEGIN:VEVENT\n(?:(?!BEGIN:VEVENT).)*?UID:" + re.escape(uid) + r"\n(?:(?!BEGIN:VEVENT).)*?END:VEVENT", re.S)
    m = pattern.search(text)
    return m


def validate(text: str, path: Path):
    if not text.startswith("BEGIN:VCALENDAR\n"):
        raise RuntimeError(f"{path}: invalid VCALENDAR start")
    if not text.rstrip().endswith("END:VCALENDAR"):
        raise RuntimeError(f"{path}: invalid VCALENDAR end")
    if text.count("BEGIN:VEVENT") != text.count("END:VEVENT"):
        raise RuntimeError(f"{path}: unbalanced VEVENT")
    uids = re.findall(r"^UID:(.+)$", text, re.M)
    if len(uids) != len(set(uids)):
        raise RuntimeError(f"{path}: duplicate UID")
    if text.count(f"UID:{UID}") != 1:
        raise RuntimeError(f"{path}: target UID count != 1")
    block = find_event(text, UID)
    if not block:
        raise RuntimeError(f"{path}: target block missing after patch")
    b = block.group(0)
    required = [
        "SEQUENCE:1",
        "DTSTART;TZID=Europe/Paris:20260901T180000",
        "X-HARRYPOTTER-UPDATE-REASON:OFFICIAL_TIME_CONFIRMED",
        "TRIGGER:-PT1H",
        SOURCE_URL,
    ]
    for item in required:
        if item not in b:
            raise RuntimeError(f"{path}: missing {item}")


def main():
    changed = []
    canonical_block = None
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        m = find_event(text, UID)
        if not m:
            raise RuntimeError(f"{path}: UID not found")
        old = m.group(0)
        if old == NEW_BLOCK:
            validate(text, path)
            canonical_block = NEW_BLOCK if canonical_block is None else canonical_block
            continue
        # Idempotency / safe migration: accept the old all-day event or an already partly updated target,
        # but never create a second UID.
        text2 = text[:m.start()] + NEW_BLOCK + text[m.end():]
        validate(text2, path)
        path.write_text(text2, encoding="utf-8", newline="\n")
        changed.append(str(path))
        canonical_block = NEW_BLOCK if canonical_block is None else canonical_block

    a = find_event(FILES[0].read_text(encoding="utf-8"), UID).group(0)
    b = find_event(FILES[1].read_text(encoding="utf-8"), UID).group(0)
    if a != b:
        raise RuntimeError("global/specialist target VEVENT diverged")

    if changed:
        print("UPDATED:", ", ".join(changed))
    else:
        print("NOOP: target event already synchronized")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
