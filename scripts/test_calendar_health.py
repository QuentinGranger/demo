"""Repository defects and observed service incidents must remain distinguishable."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_calendar_health as health


class HealthTests(unittest.TestCase):
    def run_check(self, mutate=None, args=None):
        originals = {name: json.loads(getattr(health, name).read_text())
                     for name in ('POLICY', 'STATE', 'HEARTBEAT')}
        data = copy.deepcopy(originals)
        if mutate:
            mutate(data)
        with tempfile.TemporaryDirectory() as tmp:
            paths = {}
            for name, value in data.items():
                path = Path(tmp) / (name + '.json')
                path.write_text(json.dumps(value))
                paths[name] = path
            output = io.StringIO()
            with patch.multiple(health, **paths), contextlib.redirect_stdout(output):
                result = health.main(args or [])
            return result, output.getvalue()

    def test_v3_static_contracts_accept_honest_degraded_observation(self):
        result, text = self.run_check(args=['--static'])
        self.assertEqual(result, 0, text)
        self.assertIn('live monitor health not certified', text)

    def test_default_check_still_fails_on_paused_and_missing_monitors(self):
        result, text = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn('AUTOMATION_DISABLED', text)
        self.assertIn('AUTOMATION_MISSING', text)
        self.assertIn('OBSERVER_REDUNDANCY_LOST', text)

    def test_stale_heartbeat_is_never_certified_healthy(self):
        def stale(data):
            data['HEARTBEAT']['last_observer_check_at'] = '2020-01-01T00:00:00Z'
        result, text = self.run_check(stale)
        self.assertEqual(result, 1)
        self.assertIn('WATCHDOG_HEARTBEAT_STALE', text)

    def test_unknown_policy_version_blocks_static_contracts(self):
        result, text = self.run_check(lambda d: d['POLICY'].update(version='UNKNOWN'), ['--static'])
        self.assertEqual(result, 1)
        self.assertIn('unexpected health policy version', text)

    def test_wrong_path_count_blocks_static_contracts(self):
        result, text = self.run_check(lambda d: d['HEARTBEAT'].update(verified_ics_path_count=9), ['--static'])
        self.assertEqual(result, 1)
        self.assertIn('verified_ics_path_count does not match', text)

    def test_false_healthy_snapshot_blocks_static_contracts(self):
        def fake(data):
            data['HEARTBEAT']['automation_snapshot']['Calendriers Fortnite France & Europe']['liveness'] = 'HEALTHY'
        result, text = self.run_check(fake, ['--static'])
        self.assertEqual(result, 1)
        self.assertIn('falsely marks unhealthy monitor HEALTHY', text)

    def test_broken_ics_blocks_static_contracts(self):
        with patch.object(health, 'validate_ics', side_effect=lambda path, errors: errors.append('broken ICS')):
            result, text = self.run_check(args=['--static'])
        self.assertEqual(result, 1)
        self.assertIn('broken ICS', text)

    def test_online_cannot_be_combined_with_static(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            health.main(['--static', '--online'])


if __name__ == '__main__':
    unittest.main()
