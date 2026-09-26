"""Regression checks for subscription compatibility and ingestion policy."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pokemon_calendar_presentation import (
    assert_allowed, assert_no_duplicate, assert_unique_calendar, clean_calendar,
    clean_description, excluded, logical, present_event, properties,
)
from pokemon_calendar_safe_patch import apply_request
from pokemon_calendar_batch_patch import apply_batch


def event(uid='test@calendar', title='⭐ ✅ 🃏 Sortie JCC — Test', extra=''):
    return ('BEGIN:VEVENT\nUID:' + uid + '\nSUMMARY:' + title + '\n'
            'DTSTART;VALUE=DATE:20261001\nDTEND;VALUE=DATE:20261002\n'
            'DESCRIPTION:Notes conservées\\nSource : https://example.org\n'
            'SEQUENCE:3\n' + extra + '\n'
            'BEGIN:VALARM\nTRIGGER:-P1D\nACTION:DISPLAY\n'
            'DESCRIPTION:Rappel conservé\nEND:VALARM\nEND:VEVENT')


def calendar(*events):
    return 'BEGIN:VCALENDAR\nVERSION:2.0\n' + '\n'.join(events) + '\nEND:VCALENDAR\n'


class PresentationTests(unittest.TestCase):
    def test_exclusions_and_incidental_mentions(self):
        for title in ('Pokémon GO — Raid', '🌙 Pokémon Sleep — Mewtwo', '⚡ GO — Hordes Méga', 'Pokémon GO —\n Raid'):
            self.assertTrue(excluded(event(title=title)))
        self.assertTrue(excluded(event(uid='pokemon-go-raid@openai', title='Raid')))
        self.assertFalse(excluded(event(title='Pokémon — Salon', extra='X-NOTE:Pokémon GO en démonstration')))
        for title in ('Pokémon Pocket', 'Pokémon Champions', 'Pokémon UNITE', 'Pokémon Gold'):
            self.assertFalse(excluded(event(title=title)))

    def test_presentation_keeps_dates_notes_alarms_and_uncertainty(self):
        source = event(title='ℹ️ 🟡 🃏 Sortie JCC — Test')
        result = present_event(source, '20260926T080000Z')
        before, after = properties(source), properties(result)
        for key in ('UID', 'DTSTART', 'DTEND'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(after['SUMMARY'], 'JCC — Test [À confirmer]')
        self.assertEqual(after['DESCRIPTION'], before['DESCRIPTION'].replace(r'\nSource', r'\n\nSource'))
        self.assertEqual(after['SEQUENCE'], '4')
        self.assertEqual(after['TRANSP'], 'TRANSPARENT')
        self.assertEqual(source.split('BEGIN:VALARM')[1], result.split('BEGIN:VALARM')[1])
        self.assertEqual(present_event(result), result)

    def test_unicode_title_folding(self):
        title = 'Événement — ' + 'é' * 100
        result = present_event(event(title=title))
        self.assertEqual(properties(result)['SUMMARY'], title)
        for line in result.splitlines():
            if line.startswith(('SUMMARY:', ' ')):
                self.assertLessEqual(len(line.encode('utf-8')), 75)

    def test_long_notes_and_urls_round_trip_with_utf8_folding(self):
        source = event(extra='URL:https://example.org/' + 'é' * 120)
        result = present_event(source)
        self.assertEqual(properties(result)['URL'], properties(source)['URL'])
        self.assertTrue(all(len(line.encode('utf-8')) <= 75 for line in result.splitlines()))
        self.assertEqual(present_event(result), result)

    def test_description_spacing_preserves_details_and_certainty(self):
        notes = r'📦 Checklist produits :\n🟡 Coffret Mew — 49,99 €\n🟠 ETB\nSource : https://example.org/a\,b\nRappels : J-1'
        result = clean_description(notes)
        self.assertIn('[À confirmer] Coffret Mew — 49,99 €', result)
        self.assertIn('[Distributeur] ETB', result)
        self.assertIn(r'\n\nSource : https://example.org/a\,b', result)
        self.assertEqual(clean_description(result), result)
        self.assertEqual(clean_description(r'Literal \\n preserved'), r'Literal \\n preserved')

    def test_direct_write_duplicate_caught_by_validation(self):
        with self.assertRaises(SystemExit):
            assert_unique_calendar(calendar(event('a'), event('b')))
        with self.assertRaises(SystemExit):
            assert_unique_calendar(calendar(event('a'), event('a', 'Autre titre')))
        with self.assertRaises(SystemExit):
            assert_unique_calendar(calendar(event('go', 'Pokémon GO — Raid')))

    def test_different_zones_durations_and_recurrences_are_not_duplicates(self):
        source = event('a').replace('DTSTART;VALUE=DATE:20261001', 'DTSTART;TZID=Europe/Paris:20261001T100000')
        assert_no_duplicate(calendar(source), source.replace('UID:a', 'UID:b').replace('Europe/Paris', 'America/New_York'))
        assert_no_duplicate(calendar(source), source.replace('UID:a', 'UID:b').replace('20261002', '20261003'))
        assert_no_duplicate(calendar(source), source.replace('UID:a', 'UID:b').replace('SEQUENCE:3', 'RRULE:FREQ=DAILY;COUNT=2\nSEQUENCE:3'))

    def test_title_normalization_cannot_hide_duplicate(self):
        source = event('a', 'JCC Pokémon Pocket — Booster')
        with self.assertRaises(SystemExit):
            assert_no_duplicate(calendar(source), event('b', 'Pocket — Booster [À confirmer]'))

    def test_cleaning_deduplicates_only_known_alias_with_keeper(self):
        keeper = 'fnac-beaune-pokemon-30-20260919@openai'
        alias = 'pokemon-30ans-fnac-beaune-pokeshow-20260919@openai'
        result, removed = clean_calendar(calendar(event(keeper), event(alias), event('go', 'Pokémon GO — Raid')))
        self.assertEqual(set(removed), {alias, 'go'})
        self.assertIn('UID:' + keeper, result)
        self.assertEqual(clean_calendar(result)[0], result)
        self.assertNotIn('\n', result.replace('\r\n', ''))
        self.assertEqual(clean_calendar(calendar(event(alias)))[1], [])

    def test_blocked_requests_leave_file_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            cal = Path(tmp) / 'calendar.ics'
            cal.write_bytes(calendar(event()).replace('\n', '\r\n').encode())
            original = cal.read_bytes()
            request = Path(tmp) / 'request.json'
            request.write_text(json.dumps({'operation': 'upsert', 'event': event('go', 'Pokémon GO — Raid')}))
            with patch('pokemon_calendar_safe_patch.resolve_calendar', return_value=cal):
                with self.assertRaises(SystemExit):
                    apply_request(request)
            self.assertEqual(cal.read_bytes(), original)

    def test_batch_preflights_exclusions_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            cal = Path(tmp) / 'calendar.ics'
            cal.write_bytes(calendar(event()).replace('\n', '\r\n').encode())
            original = cal.read_bytes()
            paths = []
            for index, title in enumerate(('Sortie JCC — Nouveau', 'Pokémon Sleep — Mewtwo')):
                request = Path(tmp) / f'{index}.json'
                request.write_text(json.dumps({'operation': 'upsert', 'calendar_path': str(cal), 'event': event(str(index), title)}))
                paths.append(request)
            with patch('pokemon_calendar_batch_patch.CANONICAL_CALENDAR', str(cal)):
                with self.assertRaises(SystemExit):
                    apply_batch(paths)
            self.assertEqual(cal.read_bytes(), original)

    def test_alias_cannot_be_reintroduced(self):
        with self.assertRaises(SystemExit):
            assert_allowed(event('pokemon-30ans-fnac-beaune-pokeshow-20260919@openai'))

    def test_new_uid_cannot_reintroduce_same_pocket_release(self):
        incoming = event('new-unknown-uid', 'Pokémon Pocket — Booster de Luxe Méga').replace('20261001', '20260930')
        with self.assertRaises(SystemExit):
            assert_allowed(incoming)

    def test_same_session_rejected_but_different_dates_and_places_preserved(self):
        existing = calendar(event('a', 'Tournoi', 'LOCATION:Paris'))
        with self.assertRaises(SystemExit):
            assert_no_duplicate(existing, event('b', 'TOURNOI', 'LOCATION:Paris'))
        assert_no_duplicate(existing, event('b', 'Tournoi', 'LOCATION:Lyon'))
        assert_no_duplicate(existing, event('b', 'Tournoi', 'LOCATION:Paris').replace('20261001', '20261003'))

    def test_compact_period_preserves_real_window_and_notes(self):
        uid = 'pokemon-30ans-collection-classeur-q4-2026@openai'
        source = event(uid, 'Fenêtre classeur [À confirmer]').replace('DTEND;VALUE=DATE:20261002', 'DTEND;VALUE=DATE:20270101')
        result = present_event(source)
        props = properties(result)
        self.assertEqual(props['DTSTART'], '20261001')
        self.assertEqual(props['DTEND'], '20261002')
        self.assertEqual(props['X-POKEMON-PERIOD-END'], '20270101')
        self.assertIn('31/12/2026', props['DESCRIPTION'])
        self.assertIn('Notes conservées', props['DESCRIPTION'])
        self.assertIn('À confirmer', props['SUMMARY'])
        self.assertEqual(present_event(result), result)

    def test_end_relative_alarm_prevents_unsafe_compaction(self):
        uid = 'pokemon-30ans-collection-classeur-q4-2026@openai'
        source = event(uid).replace('DTEND;VALUE=DATE:20261002', 'DTEND;VALUE=DATE:20270101').replace('TRIGGER:', 'TRIGGER;RELATED=END:')
        self.assertEqual(properties(present_event(source))['DTEND'], '20270101')

    def test_batch_duplicate_preflight_leaves_calendar_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            cal = Path(tmp) / 'calendar.ics'
            cal.write_bytes(calendar(event()).replace('\n', '\r\n').encode())
            original = cal.read_bytes()
            paths = []
            for uid in ('first', 'second'):
                request = Path(tmp) / f'{uid}.json'
                request.write_text(json.dumps({'operation': 'upsert', 'calendar_path': str(cal), 'event': event(uid, 'Un seul événement')}))
                paths.append(request)
            with patch('pokemon_calendar_batch_patch.CANONICAL_CALENDAR', str(cal)), self.assertRaises(SystemExit):
                apply_batch(paths)
            self.assertEqual(cal.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
