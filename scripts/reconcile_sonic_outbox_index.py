#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-29T02:00:55Z"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")

outbox = load(CAL / "fortnite-notification-outbox-france.json")
index_path = CAL / "fortnite-change-index-france.json"
index = load(index_path)

consumed = sorted(outbox.get("consumed_keys", {}).keys())
unknown = sorted(
    key for key, state in outbox.get("consumed_keys", {}).items()
    if state.get("state") == "UNKNOWN_DELIVERY"
)
index["consumed_notification_keys"] = consumed
index["unknown_delivery_keys"] = unknown
index["updated_at"] = AT
index.setdefault("stats", {})["notification_intents"] = len(outbox.get("intents", []))
index["stats"]["consumed_notification_keys"] = len(consumed)
index["stats"]["unknown_delivery"] = len(unknown)
dump(index_path, index)
print("RECONCILED", len(outbox.get("intents", [])), len(consumed), len(unknown))
