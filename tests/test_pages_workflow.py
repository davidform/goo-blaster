"""No network or Git writes: pin release gates against incomplete/unreleased payloads."""
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('pages', Path(__file__).resolve().parents[1] / 'native/publish_pages.py')
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)

class PagesGate(unittest.TestCase):
    def setUp(self):
        self.payload = b"const BUILD='v0.9.55';\r\n// tested\n"
        self.sha = pages.hashlib.sha256(self.payload).hexdigest()
        self.receipt = dict(page='https://davidform.itch.io/goo-blaster', channel='html5', build='v0.9.55',
                            game_sha256=self.sha, game_payload_identical=True, browser_start_verified=True)
        self.report = dict(sha256=self.sha, complete=True, source_unchanged=True, planned=['a','perf'],
                           results=[dict(test=n, passed=True, exit_code=0, printed_failure=False) for n in ['a','perf']])
        def git(*args):
            if args[0] == 'rev-parse': return b'a' * 40
            if args[1].endswith(':index.html'): return self.payload.replace(b'\r\n', b'\n')
            return b'\nelse\nPY="a"\nJS=""\nSOLO="perf"\n'
        self.mock = patch.object(pages, 'git', side_effect=git)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def check_gate(self, reports=None, payload=None):
        return pages.validate('source', self.receipt, reports or [self.report], payload or self.payload)

    def test_exact_tested_bytes_preserved(self):
        self.assertEqual(self.check_gate()['sha256'], self.sha)

    def test_wrong_release(self):
        self.receipt['build'] = 'v0.9.58'
        with self.assertRaises(ValueError): self.check_gate()

    def test_unverified_browser(self):
        self.receipt['browser_start_verified'] = False
        with self.assertRaises(ValueError): self.check_gate()

    def test_failed_perf(self):
        self.report['results'][1]['passed'] = False
        with self.assertRaises(ValueError): self.check_gate()

    def test_missing_suite(self):
        self.report['planned'] = ['a']
        self.report['results'] = self.report['results'][:1]
        with self.assertRaises(ValueError): self.check_gate()

    def test_wrong_report_hash(self):
        self.report['sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.check_gate()

    def test_changed_source(self):
        with self.assertRaises(ValueError): self.check_gate(payload=self.payload + b'changed')

    def test_same_payload_retry_keeps_failure(self):
        retry = copy.deepcopy(self.report)
        retry['planned'] = ['perf']; retry['results'] = retry['results'][1:]
        self.report['results'][1]['passed'] = False
        self.assertEqual(self.check_gate([self.report,retry])['tests'], 2)
        self.assertFalse(self.report['results'][1]['passed'])

if __name__ == '__main__': unittest.main()
