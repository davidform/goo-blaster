"""Do not distribute an APK using incomplete, stale, or failed test evidence."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('mobile_build',Path(__file__).resolve().parents[1]/'native/build_test_apk.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
pubspec=importlib.util.spec_from_file_location('mobile_publish',Path(__file__).resolve().parents[1]/'native/publish_test_apk.py')
publisher=importlib.util.module_from_spec(pubspec);pubspec.loader.exec_module(publisher)

class Gate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.required=sorted(module.required_suite())
    def report(self,name='full',names=None,failed=None,sha='current',complete=True):
        names=self.required if names is None else names
        data={'planned':names,'complete':complete,'source_unchanged':True,'sha256':sha,
          'results':[{'test':n,'passed':n!=failed,'exit_code':int(n==failed),'printed_failure':False} for n in names]}
        p=self.root/(name+'.json');p.write_text(json.dumps(data));return p
    def test_full_pass(self):module.validate_reports(self.report(),[],'current')
    def test_focused_is_not_full(self):
        with self.assertRaises(ValueError):module.validate_reports(self.report(names=self.required[:1]),[],'current')
    def test_old_payload_rejected(self):
        with self.assertRaises(ValueError):module.validate_reports(self.report(sha='old'),[],'current')
    def test_unfinished_rejected(self):
        with self.assertRaises(ValueError):module.validate_reports(self.report(complete=False),[],'current')
    def test_failed_gate_rejected(self):
        with self.assertRaises(ValueError):module.validate_reports(self.report(failed=self.required[0]),[],'current')
    def test_same_payload_retry(self):
        module.validate_reports(self.report(failed=self.required[0]),[self.report('retry',names=self.required[:1])],'current')
    def test_wrong_payload_retry_rejected(self):
        with self.assertRaises(ValueError):module.validate_reports(self.report(failed=self.required[0]),[self.report('retry',names=self.required[:1],sha='old')],'current')

class DraftLookup(unittest.TestCase):
    def test_existing_draft_resumes_without_creating_duplicate(self):
        draft={'id':123,'tag_name':'android-test','draft':True}
        class Client:
            def request(self,method,path):
                assert method=='GET'
                return None if '/tags/' in path else [draft]
        self.assertEqual(publisher.channel_release(Client()),draft)
    def test_duplicate_drafts_stop(self):
        class Client:
            def request(self,method,path):
                return None if '/tags/' in path else [{'tag_name':'android-test'}]*2
        with self.assertRaises(ValueError):publisher.channel_release(Client())

if __name__=='__main__':unittest.main()
