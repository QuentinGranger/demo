const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'calendar.html'), 'utf8');
const code = html.match(/<script id="calendar-core">([\s\S]*?)<\/script>/)[1];
const context = { module: { exports: {} }, Intl, Date };
vm.runInNewContext(code, context);
const C = context.module.exports;
const event = (extra='', uid='test', title='Tournoi à Lyon') => `BEGIN:VEVENT\nUID:${uid}\nSUMMARY:${title}\nDTSTART;TZID=Europe/Paris:20260926T100000\n${extra}\nEND:VEVENT`;
const calendar = (...events) => 'BEGIN:VCALENDAR\nVERSION:2.0\n'+events.join('\n')+'\nEND:VCALENDAR';

test('Paris dates respect summer and winter offsets',()=>{
 assert.equal(new Date(C.dateValue('20260926T100000').epoch).toISOString(),'2026-09-26T08:00:00.000Z');
 assert.equal(new Date(C.dateValue('20261226T100000').epoch).toISOString(),'2026-12-26T09:00:00.000Z');
 assert.equal(C.dateValue('20260926T230000Z').day,'2026-09-27');
 assert.equal(new Date(C.dateValue('20260926T100000',{TZID:'America/New_York'}).epoch).toISOString(),'2026-09-26T14:00:00.000Z');
});
test('all-day end is exclusive, including DST and missing end',()=>{
 for(const date of ['20260329','20261025']){
  const raw=calendar(`BEGIN:VEVENT\nUID:${date}\nSUMMARY:Sortie\nDTSTART;VALUE=DATE:${date}\nEND:VEVENT`);
  const {events,warnings}=C.parseICS(raw,'pokemon');
  assert.equal(warnings.length,0);assert.equal(events[0].day,events[0].lastDay);
 }
 const {events}=C.parseICS(calendar('BEGIN:VEVENT\nUID:multi\nSUMMARY:Salon\nDTSTART;VALUE=DATE:20261003\nDTEND;VALUE=DATE:20261005\nEND:VEVENT'),'pokemon');
 assert.equal(events[0].lastDay,'2026-10-04');assert.equal(C.overlaps(events[0],'2026-10-05','2026-10-05'),false);
});
test('folded text and escaped punctuation survive; alarm notes do not replace event notes',()=>{
 const {events}=C.parseICS(calendar(event('DESCRIPTION:Notes\\nLieu\\, Lyon\\; test\\\\n\n Suite\nBEGIN:VALARM\nDESCRIPTION:Alarme\nEND:VALARM')),'pokemon');
 assert.equal(events[0].description,'Notes\nLieu, Lyon; test\\nSuite');
});
test('GO and Sleep excluded, incidental mentions and Pocket retained',()=>{
 const {events}=C.parseICS(calendar(event('', 'go','Pokémon GO — Raid'),event('', 'sleep','Pokémon Sleep'),event('DESCRIPTION:Pokémon GO en démonstration','pocket','Pocket — Booster'),event('','gold','Pokémon Gold')),'pokemon');
 assert.deepEqual(Array.from(events,e=>e.uid),['pocket','gold']);
});
test('same UID keeps latest sequence but separate sessions survive',()=>{
 const {events}=C.parseICS(calendar(event('SEQUENCE:1','a'),event('SEQUENCE:2','a','Nouveau titre'),event('','b')),'pokemon');
 assert.equal(events.length,2);assert.equal(events[0].title,'Nouveau titre');
});
test('unsupported recurrence is reported instead of showing a misleading single occurrence',()=>{
 const {events,warnings}=C.parseICS(calendar(event('RRULE:FREQ=WEEKLY')),'pokemon');
 assert.equal(events.length,0);assert.equal(warnings.length,1);
});
test('search is accent-insensitive and filters combine with month overlap',()=>{
 const events=C.parseICS(calendar(event('STATUS:TENTATIVE\nLOCATION:Lyon','a','Pokémon — Défi de Ligue'),event('STATUS:CONFIRMED','b','Sortie JCC — Coffret')),'pokemon').events;
 const filter={feeds:['pokemon'],kind:'competition',status:'tentative',query:'defi',future:false,now:0,first:'2026-09-01',last:'2026-09-30'};
 assert.equal(C.filterEvents(events,filter).length,1);
 assert.equal(C.filterEvents(events,{...filter,feeds:[]}).length,0);
 assert.equal(C.filterEvents(events,{...filter,first:'2026-10-01',last:'2026-10-31'}).length,0);
});
test('unmarked events are not presented as confirmed and cancelled events stay explicit',()=>{
 const {events}=C.parseICS(calendar(event('','a'),event('STATUS:CANCELLED','b'),event('','c','🟡 Sortie incertaine')),'pokemon');
 assert.deepEqual(Array.from(events,e=>e.status),['unspecified','cancelled','tentative']);
});
test('current three production feeds parse completely without unsupported events',()=>{
 for(const file of ['pokemon-paris','fortnite-paris','harry-potter-paris']){
  const raw=fs.readFileSync(path.join(root,'calendars',file+'.ics'),'utf8');
  const {events,warnings}=C.parseICS(raw,file);
  assert.equal(warnings.length,0,JSON.stringify(warnings));assert.ok(events.length>0);
  assert.equal(events.length,(raw.match(/BEGIN:VEVENT/g)||[]).length);
 }
});
test('quoted ALTREP URLs do not leak into the venue name',()=>{
 const {events}=C.parseICS(calendar(event('LOCATION;ALTREP="https://maps.apple.com/?q=a;b":Parc des Expositions\\, Lyon')),'pokemon');
 assert.equal(events[0].location,'Parc des Expositions, Lyon');
});
