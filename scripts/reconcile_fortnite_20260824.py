#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
NOW = "2026-08-24T00:15:37Z"
NOW_ICS = "20260824T001537Z"
UID = "fortnite-lego-odyssey-monastery-portal-20260827@openai"
SOURCE_URL = "https://www.fortnite.com/@epic/lego-fortnite-odyssey"
CHANGE_ID = "chg_0b7089e1a6cd61e1b57954c2"
SUBJECT_SCOPE = "sub_83a8e195a3d4e86be1314d68518fbc2f2797c4c034b72c0ee6d331c27f72e7ab"
STATE_FP = "2b750e67c0cae79afcb06b1bdb6f835b8ea3cf71f0193ed8b7d413082cdd744d"
TRANSITION_FP = "6ebf84c0bcd2713f6e52625788a6fe967a9d1dfec04092d301a80031c10c7fb4"
NTF = "ntf_200a9054577949e861f033cca1f180fe99d5fe8c8579f637472eaf23d9224be1"
INTENT = "nti_e4038b7ea2b56d53d4f2454b"
RESERVATION = "nrs_033f5bb6dad308a65687df5d"
DELIVERY = "nde_386f09ac7827e8bb780395a1"
PAYLOAD = "🧱 LEGO Fortnite Odyssey — le portail du Monastère rouvre du 27 août à 10h00 au 2 septembre à 10h00 (heure de Paris). En éliminant le Shatter Spawn, tu peux obtenir quatre récompenses dorées : Sword of FIRE, Scythe of QUAKES, Nunchucks of LIGHTNING et Shurikens of ICE."
PAYLOAD_FP = "69c8782add78aec5c418d8a8cfefb9e2b96349ea9ec36dc122b00775e1be8aac"


def load(name):
    with (CAL / name).open("r", encoding="utf-8") as f: return json.load(f)

def dump(name, obj):
    (CAL / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

def fold(line):
    out=[]; cur=""; limit=75
    for ch in line:
        if len((cur+ch).encode("utf-8")) > limit:
            out.append(cur); cur=" "+ch; limit=75
        else: cur += ch
    out.append(cur)
    return out

def event_text():
    lines = [
      "BEGIN:VEVENT", f"UID:{UID}", f"DTSTAMP:{NOW_ICS}", f"LAST-MODIFIED:{NOW_ICS}", "SEQUENCE:0", "STATUS:CONFIRMED", "PRIORITY:5", "X-FORTNITE-PRIORITY:IMPORTANT", "X-FORTNITE-ACTION:PLAY", "X-FORTNITE-EVENT-TYPE:LIMITED_TIME_EVENT", "X-FORTNITE-MODE:LEGO_FORTNITE_ODYSSEY", "X-FORTNITE-THEME:MONASTERY", "X-FORTNITE-EVIDENCE-GRADE:A", "X-FORTNITE-SOURCE-ID:fortnite_news", "X-FORTNITE-SOURCE-TIMEZONE:America/New_York", "X-FORTNITE-TIME-PRECISION:EXACT", "X-FORTNITE-CANDIDATE-ID:fortnite-lego-odyssey-monastery-portal-20260827", f"X-FORTNITE-LAST-CHANGE-ID:{CHANGE_ID}", f"X-FORTNITE-FIRST-ADDED-AT:{NOW_ICS}", "X-FORTNITE-NEW-UNTIL:20260829T001537Z", "DTSTART;TZID=Europe/Paris:20260827T100000", "DTEND;TZID=Europe/Paris:20260902T100000", "SUMMARY:⭐ ✅ 🆕 🧱 LEGO Fortnite Odyssey — portail du Monastère", "DESCRIPTION:Priorité : ⭐ Important — fenêtre limitée officiellement publiée par Epic.\\nDu 27 août 2026 à 10h00 au 2 septembre 2026 à 10h00 heure de Paris, le portail du Monastère rouvre dans LEGO Fortnite Odyssey.\\nÉliminer le Shatter Spawn permet d’obtenir quatre récompenses dorées : Sword of FIRE, Scythe of QUAKES, Nunchucks of LIGHTNING et Shurikens of ICE.\\nAucune autre condition, quota ou rareté n’est déduite.\\nSource : https://www.fortnite.com/@epic/lego-fortnite-odyssey", f"URL:{SOURCE_URL}", "CATEGORIES:Fortnite,LEGO Fortnite Odyssey,Événement limité,Monastère,Récompenses", "BEGIN:VALARM", "TRIGGER:-P1D", "ACTION:DISPLAY", "DESCRIPTION:🧱 Portail du Monastère demain à 10h — fenêtre limitée LEGO Fortnite Odyssey", "END:VALARM", "END:VEVENT"
    ]
    return "\r\n".join(y for x in lines for y in fold(x)) + "\r\n"

def add_event(name):
    p=CAL/name; raw=p.read_bytes(); text=raw.decode("utf-8-sig").replace("\r\n","\n").replace("\r","\n")
    if f"UID:{UID}" in text: return False
    marker="END:VCALENDAR\n"
    if marker not in text and text.rstrip().endswith("END:VCALENDAR"):
        text=text.rstrip()+"\n"
    text=text.replace("END:VCALENDAR\n", event_text().replace("\r\n","\n")+"END:VCALENDAR\n", 1)
    p.write_bytes(text.replace("\n","\r\n").encode("utf-8")); return True

# 1) Project the already-confirmed READY candidate to both subscribed views.
add_event("fortnite-updates-france.ics")
add_event("fortnite-paris.ics")

# 2) Promote watchlist candidate, preserving stable identity.
w=load("fortnite-watchlist-france.json")
for c in w.get("candidates",[]):
    if c.get("candidate_id")=="fortnite-lego-odyssey-monastery-portal-20260827":
        c["state"]="CALENDAR_ADDED"; c["promoted_at"]=NOW; c["related_calendar_uid"]=UID
        c["known"]="Epic confirme le portail du Monastère dans LEGO Fortnite Odyssey du 27 août 2026 à 04:00 ET au 2 septembre 2026 à 04:00 ET, soit du 27 août 10:00 au 2 septembre 10:00 à Paris. Vaincre le Shatter Spawn donne quatre récompenses dorées : Sword of FIRE, Scythe of QUAKES, Nunchucks of LIGHTNING et Shurikens of ICE."
w["updated_at"]=NOW; dump("fortnite-watchlist-france.json",w)

# 3) Append one causal calendar-projection change (one user effect for both views).
l=load("fortnite-change-ledger.json")
if not any(c.get("change_id")==CHANGE_ID for c in l.get("changes",[])):
    material_after={"uid":UID,"status":"CONFIRMED","start_at":"2026-08-27T08:00:00Z","end_at":"2026-09-02T08:00:00Z","mode":"LEGO_FORTNITE_ODYSSEY","action":"PLAY","event_type":"LIMITED_TIME_EVENT","subject":"MONASTERY_PORTAL","rewards":["Sword of FIRE","Scythe of QUAKES","Nunchucks of LIGHTNING","Shurikens of ICE"],"projection_targets":["calendars/fortnite-updates-france.ics","calendars/fortnite-paris.ics"]}
    l["changes"].append({"change_id":CHANGE_ID,"domain":"CALENDAR_PROJECTION","subject_scope_key":SUBJECT_SCOPE,"subject_key":f"calendars/fortnite-updates-france.ics|{UID}","subject_revision":1,"causal_parent_change_id":None,"change_type":"CALENDAR_PROMOTED","materiality":"NOTIFY","state_fingerprint":STATE_FP,"transition_fingerprint":TRANSITION_FP,"detected_at":NOW,"source_refs":[SOURCE_URL],"notification_disposition":"ELIGIBLE_NOW","scope_key":"calendars/fortnite-paris.ics","material_before":None,"material_after":material_after,"material_evidence_state":"EPIC_OFFICIAL_COMMUNITY_EXACT_WINDOW","projection_targets":["calendars/fortnite-updates-france.ics","calendars/fortnite-paris.ics"],"policy_version":"FORTNITE_CHANGE_ENGINE_FR_V2","notes":"READY candidate reconciled into specialist + global calendars. Single change prevents duplicate notification for the mirrored projection."})
    l.setdefault("history",[]).append({"at":NOW,"type":"MATERIAL_CALENDAR_PROMOTION","note":"Official LEGO Fortnite Odyssey Monastery portal window projected from READY watchlist into updates + global calendars."})
l["updated_at"]=NOW; dump("fortnite-change-ledger.json",l)

# 4) Reserve exactly one notification intent before any user-visible emission.
o=load("fortnite-notification-outbox-france.json")
if NTF not in o.get("consumed_keys",{}):
    if not any(i.get("notification_key")==NTF for i in o.get("intents",[])):
        o.setdefault("intents",[]).append({"intent_id":INTENT,"notification_key":NTF,"change_ids":[CHANGE_ID],"notice_kind":"LEGO_ODYSSEY_MONASTERY_PORTAL_WINDOW","audience_key":"user","channel_key":"chat","payload_fingerprint":PAYLOAD_FP,"render_version":"FORTNITE_ALERT_FR_V1","created_at":NOW,"subject_key":UID,"locale":"fr-FR","payload_snapshot":PAYLOAD,"condition_snapshot":{"status":"CONFIRMED","start_at":"2026-08-27T10:00:00+02:00","end_at":"2026-09-02T10:00:00+02:00","event_window_future":True},"policy_version":"FORTNITE_CHANGE_ENGINE_FR_V2"})
    o.setdefault("delivery_events",[]).append({"delivery_event_id":DELIVERY,"intent_id":INTENT,"notification_key":NTF,"state":"RESERVED","at":NOW,"reservation_id":RESERVATION,"note":"Reserved after fresh canonical reconciliation of the official LEGO Odyssey Monastery limited-time window. Key is consumed before user-visible emission."})
    o.setdefault("consumed_keys",{})[NTF]={"intent_id":INTENT,"state":"RESERVED","last_event_id":DELIVERY}
    o.setdefault("history",[]).append({"at":NOW,"type":"NOTIFICATION_RESERVED","notification_key":NTF,"note":"One notification reserved for the official LEGO Odyssey Monastery portal window."})
o["updated_at"]=NOW; dump("fortnite-notification-outbox-france.json",o)

# 5) Rebuild the portions of the derived change index that validators require, plus semantic groupings.
i=load("fortnite-change-index-france.json")
heads={}
for c in l.get("changes",[]):
    k=c["subject_scope_key"]; r=c["subject_revision"]
    if k not in heads or r>heads[k]["revision"]: heads[k]={"revision":r,"change_id":c["change_id"]}
i["subject_heads"]={k:heads[k] for k in sorted(heads)}
i.setdefault("by_domain",{}).setdefault("CALENDAR_PROJECTION",[])
if CHANGE_ID not in i["by_domain"]["CALENDAR_PROJECTION"]: i["by_domain"]["CALENDAR_PROJECTION"].append(CHANGE_ID)
i["by_domain"]["CALENDAR_PROJECTION"]=sorted(set(i["by_domain"]["CALENDAR_PROJECTION"]))
i.setdefault("by_change_type",{}).setdefault("CALENDAR_PROMOTED",[])
if CHANGE_ID not in i["by_change_type"]["CALENDAR_PROMOTED"]: i["by_change_type"]["CALENDAR_PROMOTED"].append(CHANGE_ID)
i["by_change_type"]["CALENDAR_PROMOTED"]=sorted(set(i["by_change_type"]["CALENDAR_PROMOTED"]))
i.setdefault("open_changes_by_subject",{}).setdefault(SUBJECT_SCOPE,[])
if CHANGE_ID not in i["open_changes_by_subject"][SUBJECT_SCOPE]: i["open_changes_by_subject"][SUBJECT_SCOPE].append(CHANGE_ID)
i["open_changes_by_subject"][SUBJECT_SCOPE]=sorted(set(i["open_changes_by_subject"][SUBJECT_SCOPE]))
consumed={}
by_intent={x["intent_id"]:x for x in o.get("intents",[])}
for e in sorted(o.get("delivery_events",[]),key=lambda x:x.get("at","")):
    if e.get("state") in {"RESERVED","SENT","UNKNOWN_DELIVERY"}:
        consumed[e["notification_key"]]={"intent_id":e["intent_id"],"state":e["state"],"last_event_id":e["delivery_event_id"]}
i["consumed_notification_keys"]=sorted(consumed)
i["unknown_delivery_keys"]=sorted(k for k,v in consumed.items() if v["state"]=="UNKNOWN_DELIVERY")
i["stats"]={"changes":len(l.get("changes",[])),"subjects":len(heads),"notification_intents":len(o.get("intents",[])),"consumed_notification_keys":len(consumed),"unknown_delivery":len(i["unknown_delivery_keys"]),"pending_reconciliation":len(i.get("pending_reconciliation",[]))}
i["updated_at"]=NOW; dump("fortnite-change-index-france.json",i)

print("Reconciled",UID,CHANGE_ID,NTF)
