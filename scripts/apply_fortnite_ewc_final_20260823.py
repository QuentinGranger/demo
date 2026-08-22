#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAL=ROOT/'calendars'
AT='2026-08-22T22:07:18Z'
ICS_AT='20260822T220718Z'
COMP_ID='reload-elite-ewc-paris-2026'
UID='fortnite-reload-elite-ewc-paris-20260819@openai'
SOURCE_EWC='https://ewc-web.prod.esf-systems.com/en/competitions/2026/fortnite'
SOURCE_EPIC='https://www.fortnite.com/competitive/events/EWCParis/?lang=fr&region=EU'


def load(name):
    return json.loads((CAL/name).read_text(encoding='utf-8'))

def dump(name,obj):
    (CAL/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

def canon(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def sha256(obj):
    raw=canon(obj) if not isinstance(obj,str) else obj
    return hashlib.sha256(raw.encode()).hexdigest()

def blob_sha(path):
    raw=path.read_bytes(); return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()

def unfold(text):
    text=text.replace('\r\n','\n').replace('\r','\n')
    out=[]
    for line in text.split('\n'):
        if line.startswith((' ','\t')) and out: out[-1]+=line[1:]
        else: out.append(line)
    return out

def fold_line(line):
    b=line.encode('utf-8')
    if len(b)<=75:return [line]
    out=[]; first=True
    while b:
        lim=75 if first else 74
        cut=min(lim,len(b))
        while cut>0:
            try: seg=b[:cut].decode('utf-8'); break
            except UnicodeDecodeError: cut-=1
        out.append(('' if first else ' ')+seg); b=b[cut:]; first=False
    return out

def write_ics(name, lines):
    physical=[]
    for l in lines:
        physical.extend(fold_line(l))
    (CAL/name).write_bytes(('\r\n'.join(physical).rstrip('\r\n')+'\r\n').encode('utf-8'))

def set_prop(block,key,value):
    pref=key+':'
    for i,l in enumerate(block):
        if l.startswith(pref): block[i]=pref+value; return
    # insert before DTSTART
    ix=next((i for i,l in enumerate(block) if l.startswith('DTSTART')),len(block)-1)
    block.insert(ix,pref+value)

def replace_session_status(block,phase,status):
    token=f'X-FORTNITE-COMPETITIVE-SESSION;PHASE={phase};STATUS='
    for i,l in enumerate(block):
        if l.startswith(token):
            head, val=l.split(':',1)
            head=re.sub(r'STATUS=[^;:]+',f'STATUS={status}',head)
            block[i]=head+':'+val

def update_ics(name):
    lines=unfold((CAL/name).read_text(encoding='utf-8'))
    start=None; end=None
    for i,l in enumerate(lines):
        if l=='BEGIN:VEVENT' and i+1<len(lines):
            j=i+1
            while j<len(lines) and lines[j]!='END:VEVENT':
                if lines[j]==f'UID:{UID}': start=i
                j+=1
            if start==i: end=j; break
    if start is None: raise SystemExit(f'{name}: target UID missing')
    b=lines[start:end+1]
    # Idempotency: if already finalized do nothing.
    if any(l=='X-FORTNITE-COMPETITION-STATUS:COMPLETED' for l in b) and any(l=='X-FORTNITE-CHAMPION-CLUB:BIG' for l in b): return False
    # Business changes.
    for key,val in [('DTSTAMP',ICS_AT),('LAST-MODIFIED',ICS_AT),('X-FORTNITE-ACTION','INFO'),('X-FORTNITE-COMPETITION-STATUS','COMPLETED'),('X-FORTNITE-CHAMPION-CLUB','BIG'),('X-FORTNITE-CHAMPION-DUO','BIG Malibuca / BIG vic0'),('X-FORTNITE-MVP','vic0'),('X-FORTNITE-RESULT-FINALITY','FINAL_OFFICIAL'),('X-FORTNITE-CHAMPION-PRIZE-USD','260000')]: set_prop(b,key,val)
    for i,l in enumerate(b):
        if l.startswith('SEQUENCE:'):
            b[i]=f"SEQUENCE:{int(l.split(':',1)[1])+1}"
        if l.startswith('X-FORTNITE-UPDATE-REASON:'): b[i]='X-FORTNITE-UPDATE-REASON:FINAL_OFFICIAL_RESULT'
        if l.startswith('X-FORTNITE-LAST-MAJOR-UPDATE-AT:'): b[i]='X-FORTNITE-LAST-MAJOR-UPDATE-AT:'+ICS_AT
        if l.startswith('X-FORTNITE-UPDATE-UNTIL:'): b[i]='X-FORTNITE-UPDATE-UNTIL:20260825T220718Z'
    replace_session_status(b,'SURVIVAL','COMPLETED'); replace_session_status(b,'FINALS','COMPLETED')
    # Add official result sentence once, keeping the rest of the prior description intact.
    for i,l in enumerate(b):
        if l.startswith('DESCRIPTION:'):
            desc=l[len('DESCRIPTION:'):]
            result='🏆 Résultat final officiel : BIG remporte le Reload Elite Series Championship 2026 et 260 000 $ ; le duo est BIG Malibuca / BIG vic0, et vic0 est désigné MVP par EWC. RVNS SkyJump + LYOST Momsy termine 2e et Aurora Gaming 3e. Source résultats : '+SOURCE_EWC+'\\n'
            b[i]='DESCRIPTION:'+result+desc
            break
    lines[start:end+1]=b; write_ics(name,lines); return True

# --- Competitive canonical ledger ---
ledger=load('fortnite-competitive-ledger-france.json')
comp=next(c for c in ledger['competitions'] if c['competition_id']==COMP_ID)
if comp.get('status')!='COMPLETED' or not any(h.get('type')=='COMPETITION_STATUS_CHANGED' and h.get('at')==AT for h in comp.get('history',[])):
    comp['status']='COMPLETED'
    phase=comp['phases'][0]; phase['status']='COMPLETED'
    for s in phase.get('sessions',[]): s['status']='COMPLETED'
    comp['result']={
      'finality':'FINAL_OFFICIAL','champion_club':'BIG','champion_players':['BIG Malibuca','BIG vic0'],'mvp':'vic0',
      'champion_prize_usd':260000,'runner_up':'RVNS SkyJump + LYOST Momsy','third_place':'Aurora Gaming',
      'source_id':'ewc_official','source_url':SOURCE_EWC,'confirmed_at':AT
    }
    comp.setdefault('history',[]).append({'at':AT,'type':'COMPETITION_STATUS_CHANGED','source_id':'ewc_official','note':'EWC official Fortnite competition page marks the tournament completed: BIG are champions, $260,000 prize, MVP VICO; Epic official participant listing identifies the BIG duo as Malibuca and vic0. All four championship sessions are now completed.'})
    ledger['updated_at']=AT
    dump('fortnite-competitive-ledger-france.json',ledger)

# --- Visible projections ---
ics_changed=False
for name in ('fortnite-competitive-france.ics','fortnite-paris.ics'):
    ics_changed = update_ics(name) or ics_changed

# --- Semantic change record ---
chg=load('fortnite-change-ledger.json')
subject='reload-elite-ewc-paris-2026'; scope=None
same=[c for c in chg.get('changes',[]) if c.get('domain')=='COMPETITIVE' and c.get('subject_key')==subject and c.get('scope_key')==scope]
latest=max(same,key=lambda c:c['subject_revision']) if same else None
before={'competition_status':'LIVE','phase_status':'LIVE','survival_status':'LIVE','finals_status':'SCHEDULED'}
after={'competition_status':'COMPLETED','phase_status':'COMPLETED','survival_status':'COMPLETED','finals_status':'COMPLETED','champion_club':'BIG','champion_players':['BIG Malibuca','BIG vic0'],'mvp':'vic0','champion_prize_usd':260000,'runner_up':'RVNS SkyJump + LYOST Momsy','third_place':'Aurora Gaming','result_finality':'FINAL_OFFICIAL'}
trans=sha256({'change_type':'STATUS_CHANGED','material_before':before,'material_after':after,'material_evidence_state':'OFFICIAL_FINAL_RESULTS'})
statefp=sha256(after)
existing=next((c for c in same if c.get('transition_fingerprint')==trans and c.get('causal_parent_change_id')==(latest.get('change_id') if latest and c is not latest else None)),None)
# More reliable replay test: if latest itself is already this final transition, reuse it.
if latest and latest.get('transition_fingerprint')==trans:
    final_change=latest
else:
    rev=(latest['subject_revision']+1) if latest else 1
    parent=latest['change_id'] if latest else None
    scope_key=latest['subject_scope_key'] if latest else 'sub_'+sha256('COMPETITIVE|'+subject+'|')
    cid='chg_'+sha256(f'COMPETITIVE|{subject}||{rev}|{parent}|{trans}')[:24]
    final_change={'change_id':cid,'domain':'COMPETITIVE','subject_scope_key':scope_key,'subject_key':subject,'subject_revision':rev,'causal_parent_change_id':parent,'change_type':'STATUS_CHANGED','materiality':'NOTIFY','state_fingerprint':statefp,'transition_fingerprint':trans,'detected_at':AT,'source_refs':[SOURCE_EPIC,SOURCE_EWC],'notification_disposition':'ELIGIBLE_NOW','scope_key':None,'material_before':before,'material_after':after,'material_evidence_state':'OFFICIAL_FINAL_RESULTS','policy_version':'FORTNITE_CHANGE_ENGINE_FR_V2','notes':'Official EWC final result and completion. Winner identity cross-checked against Epic official EWC participant listing.'}
    chg.setdefault('changes',[]).append(final_change); chg['updated_at']=AT; dump('fortnite-change-ledger.json',chg)

# --- Reserve exactly one notification intent before user-visible alert ---
out=load('fortnite-notification-outbox-france.json')
notice='EWC_RELOAD_ELITE_FINAL_RESULT'
change_ids=[final_change['change_id']]
key='ntf_'+sha256('|'.join(sorted(change_ids))+'|'+notice+'|user|chat')
consumed=out.get('consumed_keys',{})
if key not in consumed:
    iid='nti_'+sha256(key)[:24]
    payload='🏆 EWC Paris — résultat final Fortnite : BIG Malibuca et BIG vic0 remportent le Reload Elite Series Championship 2026. EWC désigne vic0 MVP ; BIG gagne 260 000 $. RVNS SkyJump + LYOST Momsy sont 2es, Aurora Gaming 3e.'
    pf=sha256(payload)
    intent={'intent_id':iid,'notification_key':key,'change_ids':change_ids,'notice_kind':notice,'audience_key':'user','channel_key':'chat','payload_fingerprint':pf,'render_version':'FORTNITE_ALERT_FR_V1','created_at':AT,'subject_key':UID,'locale':'fr-FR','payload_snapshot':payload,'condition_snapshot':{'competition_status':'COMPLETED','result_finality':'FINAL_OFFICIAL','champion_club':'BIG','champion_duo':['BIG Malibuca','BIG vic0'],'mvp':'vic0'},'policy_version':'FORTNITE_CHANGE_ENGINE_FR_V2'}
    out.setdefault('intents',[]).append(intent)
    reservation='nrs_'+sha256(key+'|'+AT)[:24]
    eid='nde_'+sha256(iid+'|RESERVED|1|'+reservation)[:24]
    event={'delivery_event_id':eid,'intent_id':iid,'notification_key':key,'state':'RESERVED','at':AT,'reservation_id':reservation,'note':'Reserved after official final EWC result was persisted. Key is consumed before user-visible delivery.'}
    out.setdefault('delivery_events',[]).append(event)
    out['updated_at']=AT

# Rebuild canonical outbox derived maps from append-only events.
int_by={i['intent_id']:i for i in out.get('intents',[])}
by_int={}
for e in out.get('delivery_events',[]): by_int.setdefault(e.get('intent_id'),[]).append(e)
derived={}
unknown=set()
for iid,evs in by_int.items():
    evs=sorted(evs,key=lambda e:e.get('at','')); latest_consumed=None
    for e in evs:
        if e.get('state') in {'RESERVED','SENT','UNKNOWN_DELIVERY'}: latest_consumed=e
        if e.get('state')=='UNKNOWN_DELIVERY': unknown.add(e.get('notification_key'))
    if latest_consumed and iid in int_by:
        k=int_by[iid]['notification_key']; derived[k]={'intent_id':iid,'state':latest_consumed['state'],'last_event_id':latest_consumed['delivery_event_id']}
out['consumed_keys']=dict(sorted(derived.items()))
out['group_index']={i['group_key']:i['intent_id'] for i in out.get('intents',[]) if i.get('group_key')}
dump('fortnite-notification-outbox-france.json',out)

# --- Rebuild change index exactly from ledger/outbox ---
chg=load('fortnite-change-ledger.json'); out=load('fortnite-notification-outbox-france.json')
idx=load('fortnite-change-index-france.json')
heads={}; bydom={}; bytype={}; opens={}
for c in chg.get('changes',[]):
    sk=c['subject_scope_key']; rev=c['subject_revision']; cid=c['change_id']
    if sk not in heads or rev>heads[sk]['revision']: heads[sk]={'revision':rev,'change_id':cid}
    bydom.setdefault(c['domain'],[]).append(cid); bytype.setdefault(c['change_type'],[]).append(cid)
    if c.get('state','OPEN')=='OPEN': opens.setdefault(sk,[]).append(cid)
idx['updated_at']=AT; idx['subject_heads']=dict(sorted(heads.items())); idx['by_domain']={k:sorted(set(v)) for k,v in sorted(bydom.items())}; idx['by_change_type']={k:sorted(set(v)) for k,v in sorted(bytype.items())}; idx['open_changes_by_subject']={k:sorted(set(v)) for k,v in sorted(opens.items())}
idx['consumed_notification_keys']=sorted(out.get('consumed_keys',{})); idx['unknown_delivery_keys']=sorted(unknown); idx['pending_reconciliation']=[]
idx['stats']={'changes':len(chg.get('changes',[])),'subjects':len(heads),'notification_intents':len(out.get('intents',[])),'consumed_notification_keys':len(out.get('consumed_keys',{})),'unknown_delivery':len(unknown),'pending_reconciliation':0}
dump('fortnite-change-index-france.json',idx)

# --- Rebuild competitive derived index from canonical ledger ---
ledger=load('fortnite-competitive-ledger-france.json'); ci=load('fortnite-competitive-index-france.json')
ci['generated_at']=AT; ci['source']['ledger_sha']=blob_sha(CAL/'fortnite-competitive-ledger-france.json'); ci['source']['engine_sha']=blob_sha(CAL/'fortnite-competitive-engine-france.json')
comps=ledger.get('competitions',[]); ids=sorted(c['competition_id'] for c in comps); ci['competition_ids']=ids
sections={'by_visibility':'visibility','by_status':'status','by_series_id':'series_id','by_competition_class':'competition_class','by_ruleset':'ruleset','by_team_format':'team_format','by_platform_scope':'platform_scope'}
for sec,field in sections.items():
    m={}
    for c in comps:
        v=c.get(field)
        if v is not None: m.setdefault(str(v),[]).append(c['competition_id'])
    # preserve enum buckets from previous index as empty where useful
    for oldk in ci.get(sec,{}): m.setdefault(oldk,[])
    ci[sec]={k:sorted(set(v)) for k,v in sorted(m.items())}
reg={}
for c in comps:
    for r in c.get('regions',[]): reg.setdefault(r,[]).append(c['competition_id'])
ci['by_region']={k:sorted(set(v)) for k,v in sorted(reg.items())}
phase_type={}; sessions=[]; bydate={}
for c in comps:
    dw=c.get('date_window') or {}; s=dw.get('start_date'); e=dw.get('end_date')
    if s and e:
        from datetime import date,timedelta
        d=date.fromisoformat(s); de=date.fromisoformat(e)
        while d<=de: bydate.setdefault(d.isoformat(),[]).append(c['competition_id']); d+=timedelta(days=1)
    for p in c.get('phases',[]):
        phase_type.setdefault(p.get('phase_type','OTHER'),[]).append(p['phase_id'])
        sessions.extend(p.get('sessions',[]))
ci['by_phase_type']={k:sorted(set(v)) for k,v in sorted(phase_type.items())}; ci['by_date']={k:sorted(set(v)) for k,v in sorted(bydate.items())}
allids=sorted(s['session_id'] for s in sessions); bex={}; bst={}; bstart={}
for s in sessions:
    sid=s['session_id']; st=s.get('status','UNKNOWN'); bst.setdefault(st,[]).append(sid)
    if s.get('start_at'):
        bstart.setdefault(s['start_at'],[]).append(sid); bex.setdefault(s['start_at'][:10],[]).append(sid)
ci['sessions']={'all_ids':allids,'by_exact_date':{k:sorted(set(v)) for k,v in sorted(bex.items())},'by_status':{k:sorted(set(v)) for k,v in sorted(bst.items())},'by_start_at':{k:sorted(set(v)) for k,v in sorted(bstart.items())}}
dump('fortnite-competitive-index-france.json',ci)

print('EWC finalization applied idempotently; notification key',key)
