from __future__ import annotations

from pathlib import Path
import re

PATH = Path("calendars/pokemon-paris.ics")
MONTH = "2026-09"
UID = f"pokemon-concierge-{MONTH}@openai"
DTSTAMP = "20260901T075806Z"
SUMMARY = "🎒 Pokémon Monthly Experience — La Rentrée des 30 ans"


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def fold_ical_line(line: str, limit: int = 75) -> list[str]:
    """RFC5545 line folding without splitting UTF-8 code points."""
    if len(line.encode("utf-8")) <= limit:
        return [line]
    out: list[str] = []
    current = ""
    first = True
    for ch in line:
        prefix = "" if first else " "
        candidate = current + ch
        if len((prefix + candidate).encode("utf-8")) > limit and current:
            out.append(prefix + current)
            current = ch
            first = False
        else:
            current = candidate
    if current:
        out.append(("" if first else " ") + current)
    return out


def render(lines: list[str], newline: str) -> str:
    physical: list[str] = []
    for line in lines:
        physical.extend(fold_ical_line(line))
    return newline.join(physical) + newline


raw = PATH.read_bytes()
text = raw.decode("utf-8")
newline = "\r\n" if b"\r\n" in raw else "\n"

if text.count("BEGIN:VCALENDAR") != 1 or text.count("END:VCALENDAR") != 1:
    raise SystemExit("Unsafe calendar envelope")

# Business/editorial payload. DTSTAMP/LAST-MODIFIED/SEQUENCE are handled separately
# so SEQUENCE only increments when the actual Monthly Experience changes.
description = "\n".join(
    [
        "🍂 Saison/période : rentrée en France, fin d’été et mois du 30e anniversaire du JCC Pokémon.",
        "🌟 Thème : retourner aux origines avant la grande fête des 30 ans.",
        "⚡ Mascotte : Pikachu | 🌍 Région/génération : Kanto / Génération I | 🕰 Époque : 1996→2026.",
        "🎮 Inspiration : JCC 30e Anniversaire, manga Pokémon La Grande Aventure, histoire et art Pokémon.",
        "Verdict : SELECTIVE BUY — profiter de Pokémon sans surpayer les précommandes 30 ans.",
        "🛒 Achats retenus :",
        "1) Admirez-les tous ! — visite libre Musée en Herbe — 8,00 € TTC — UTILISER — https://www.musee-en-herbe.com/50-ans-ca-se-fete-en-grand-lo4435.html",
        "2) Pokémon - La Grande Aventure, Tome 1 (Kurokawa) — 10,00 € TTC — UTILISER — https://www.cultura.com/p-pokemon-la-grande-aventure-t-1-9782368520130.html",
        "💰 TOTAL TTC : 18,00 € / 50 € | Réserve Pokédollars : 32,00 €.",
        "🧠 Anti-FOMO : l’ETB 30 ans dépasse le budget de cette Experience et plusieurs offres observées sont au-dessus du prix de référence du calendrier. Ne pas courir après une ETB chère.",
        "🎒 Rituel : visite de l’exposition puis lecture du début de La Grande Aventure ; à la maison, créer une mini-vitrine 1996→2026 avec une carte ou un objet déjà possédé.",
        "🧳 Mini-expédition <=25 € : manga seul à 10,00 € + rituel 1996→2026.",
        "🌿 No-buy 0 € : découvrir les cartes 30e Anniversaire sur Pokemon.fr, jouer à Pokémon Pocket/TCG Live avec ce que tu possèdes déjà et réorganiser 30 pièces de collection par ordre chronologique.",
        "📅 Rappels du calendrier : 6 sept. précommande ETB 30 ans Guizette (retailer) ; 16 sept. sortie officielle JCC 30e Anniversaire ; 19 sept. précommande Bundle 6 boosters Guizette ; 20 sept. précommande Coffret Classeur Guizette.",
        "⭐ Score : 94/100 — 🟢 Badge obtenu. Émotion 20/20 | Immersion 19/20 | Culture 15/15 | Expérience 14/15 | Objets 8/10 | Plaisir/prix 9/10 | Long terme 9/10.",
    ]
)

base_lines = [
    "BEGIN:VEVENT",
    f"UID:{UID}",
    "STATUS:CONFIRMED",
    "DTSTART;TZID=Europe/Paris:20260901T100000",
    "DTEND;TZID=Europe/Paris:20260901T103000",
    f"SUMMARY:{escape_text(SUMMARY)}",
    f"DESCRIPTION:{escape_text(description)}",
    "CATEGORIES:POKEMON,CONCIERGE,MONTHLY-EXPERIENCE",
    "X-POKEMON-CONCIERGE:YES",
    "X-POKEMON-CONCIERGE-BUDGET:50EUR",
    f"X-POKEMON-CONCIERGE-MONTH:{MONTH}",
    "X-POKEMON-CONCIERGE-VERDICT:SELECTIVE_BUY",
    "X-POKEMON-CONCIERGE-SCORE:94",
    "URL:https://www.pokemon.com/fr/actualites/preparez-vous-pour-lextension-30-anniversaire-du-jcc-pokemon",
    "BEGIN:VALARM",
    "TRIGGER:-P1D",
    "ACTION:DISPLAY",
    "DESCRIPTION:🎒 La Pokémon Monthly Experience de septembre arrive demain",
    "END:VALARM",
    "END:VEVENT",
]

# Unfold existing content for semantic comparison and event replacement.
unfolded = text.replace("\r\n ", "").replace("\n ", "")
pattern = re.compile(r"BEGIN:VEVENT(?:\r?\n).*?END:VEVENT(?:\r?\n)", re.S)
existing_match = None
existing_seq = 0
for match in pattern.finditer(unfolded):
    block = match.group(0)
    if f"UID:{UID}" in block:
        existing_match = match
        seq_match = re.search(r"^SEQUENCE:(\d+)$", block, flags=re.M)
        existing_seq = int(seq_match.group(1)) if seq_match else 0
        break


def normalize_business(block: str) -> str:
    lines = block.replace("\r\n", "\n").split("\n")
    filtered = [
        line
        for line in lines
        if not line.startswith("DTSTAMP:")
        and not line.startswith("LAST-MODIFIED:")
        and not line.startswith("SEQUENCE:")
        and line
    ]
    return "\n".join(filtered)

candidate_business = "\n".join(base_lines)

if existing_match:
    existing_block = existing_match.group(0)
    if normalize_business(existing_block) == normalize_business(candidate_business):
        print("Monthly Experience already current; no change.")
        raise SystemExit(0)
    sequence = existing_seq + 1
else:
    sequence = 0

final_lines = [
    base_lines[0],
    base_lines[1],
    f"DTSTAMP:{DTSTAMP}",
    f"LAST-MODIFIED:{DTSTAMP}",
    f"SEQUENCE:{sequence}",
    *base_lines[2:],
]
event = render(final_lines, newline)

# Rebuild from raw text to preserve all non-Concierge VEVENTs byte-for-byte apart
# from newline normalization already used by this calendar.
if existing_match:
    # Locate the same event in the original (possibly folded) text by UID and boundaries.
    uid_pos = text.find(f"UID:{UID}")
    start = text.rfind("BEGIN:VEVENT", 0, uid_pos)
    end = text.find("END:VEVENT", uid_pos)
    if start < 0 or end < 0:
        raise SystemExit("Could not safely locate existing Concierge event")
    end += len("END:VEVENT")
    if text.startswith("\r\n", end):
        end += 2
    elif text.startswith("\n", end):
        end += 1
    text = text[:start] + event + text[end:]
else:
    marker = "END:VCALENDAR"
    idx = text.index(marker)
    prefix, suffix = text[:idx], text[idx:]
    if prefix and not prefix.endswith(("\r\n", "\n")):
        prefix += newline
    text = prefix + event + suffix

# Enforce original newline style and validate key invariants locally.
text = text.replace("\r\n", "\n").replace("\n", newline)
if text.count("BEGIN:VCALENDAR") != 1 or text.count("END:VCALENDAR") != 1:
    raise SystemExit("Calendar envelope corrupted")
if text.count(f"UID:{UID}") != 1:
    raise SystemExit("Concierge UID is not unique")
if text.count("BEGIN:VEVENT") != text.count("END:VEVENT"):
    raise SystemExit("VEVENT boundary mismatch")
if "X-POKEMON-CONCIERGE:YES" not in text or "CATEGORIES:POKEMON,CONCIERGE,MONTHLY-EXPERIENCE" not in text:
    raise SystemExit("Concierge metadata missing")
if not text.rstrip().endswith("END:VCALENDAR"):
    raise SystemExit("Calendar does not end correctly")

PATH.write_bytes(text.encode("utf-8"))
print(f"Applied {UID} with SEQUENCE:{sequence}")
