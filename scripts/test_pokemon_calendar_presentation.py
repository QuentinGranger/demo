"""Regression checks for subscription compatibility and ingestion policy."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pokemon_calendar_presentation import (
    assert_allowed, clean_calendar, excluded, logical, present_event, properties,
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
        for key in ('UID', 'DTSTART', 'DTEND', 'DESCRIPTION'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(after['SUMMARY'], 'Sortie JCC — Test [À confirmer]')
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


if __name__ == '__main__':
    unittest.main()
