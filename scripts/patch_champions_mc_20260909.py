from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
text = p.read_text(encoding='utf-8')
uid = 'pokemon-champions-reglement-mc-20260909@openai'
if uid in text:
    raise SystemExit(0)

event = '''BEGIN:VEVENT\r\nUID:pokemon-champions-reglement-mc-20260909@openai\r\nDTSTAMP:20260902T164600Z\r\nLAST-MODIFIED:20260902T164600Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:9\r\nX-POKEMON-PRIORITY:INFO\r\nX-POKEMON-REMINDER-PROFILE:DIGITAL_RELEASE_INFO\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-FIRST-ADDED-AT:20260902T164600Z\r\nX-POKEMON-DATE-PRECISION:EXACT_DATE\r\nX-POKEMON-CONFIDENCE:96\r\nX-POKEMON-ACTIONABILITY:58\r\nX-POKEMON-USER-EFFECT-ID:pokemon-champions-mc-fr-20260909\r\nDTSTART;VALUE=DATE:20260909\r\nDTEND;VALUE=DATE:20261203\r\nSUMMARY:ℹ️ ✅ 🎮 Pokémon Champions — Règlement M-C\r\nLOCATION:En ligne — Pokémon Champions\r\nDESCRIPTION:Priorité : ℹ️ Info — nouveau règlement compétitif officiel de Pokémon Champions.\\nFiabilité : ✅ Confirmé officiellement par Pokémon. Le règlement M-C entre en vigueur le 9 septembre 2026 et ajoute notamment de nouvelles Méga-Évolutions Z ainsi que de nouveaux Pokémon à la sélection.\\n📅 Précision : date exacte confirmée ; aucune heure n'est ajoutée ici afin de ne pas sur-préciser au-delà de la preuve primaire disponible dans ce scan.\\nSource : https://www.pokemon.com/fr/actualites/le-reglement-m-c-arrive-dans-pokemon-champions\r\nURL:https://www.pokemon.com/fr/actualites/le-reglement-m-c-arrive-dans-pokemon-champions\r\nCATEGORIES:Pokémon,Pokémon Champions,Jeu vidéo,Compétitif,Règlement\r\nEND:VEVENT\r\n'''
needle = 'END:VCALENDAR'
if needle not in text:
    raise SystemExit('invalid calendar: END:VCALENDAR missing')
text = text.replace(needle, event + needle, 1)
p.write_text(text, encoding='utf-8', newline='')
