"""Offline publication safeguards; does not post to itch or run the game."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native'))
from devlog import PAGE,prepare,read,record

class DevlogTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.release=dict(page=PAGE,build='v0.9.55',game_payload_identical=True,browser_start_verified=True,game_sha256='a'*64,build_id=1)
        self.notes=dict(build='v0.9.55',title='v0.9.55 Update',languages=['en','zh-Hant'],blocks=[dict(kind='p',text='A < B & C'),dict(kind='li',text='更新說明')])
    def prep(self):return prepare(self.release,self.notes,self.temp.name)
    def receipt(self):return dict(url=PAGE+'/devlog/123/v0955-update',title=self.notes['title'],body_text='A < B & C\n更新說明',published=True)
    def test_prepare_escapes_and_is_idempotent(self):
        p=self.prep();before=p.read_bytes();self.assertIn('A &lt; B &amp; C',read(p)['body_html']);self.prep();self.assertEqual(before,p.read_bytes())
    def test_unpublished_version_blocked(self):
        self.notes['build']='v0.9.58'
        with self.assertRaises(ValueError):self.prep()
    def test_unverified_release_blocked(self):
        for key in ('game_payload_identical','browser_start_verified'):
            release=copy.deepcopy(self.release);release[key]=False
            with self.assertRaises(ValueError):prepare(release,self.notes,self.temp.name)
    def test_missing_public_content_blocked(self):
        p=self.prep();receipt=self.receipt();receipt['body_text']='A < B & C'
        with self.assertRaises(ValueError):record(p,receipt)
    def test_draft_is_not_publication(self):
        p=self.prep();receipt=self.receipt();receipt['published']=False
        with self.assertRaises(ValueError):record(p,receipt)
    def test_same_version_different_payload_blocked(self):
        self.prep();self.release['game_sha256']='b'*64
        with self.assertRaises(ValueError):self.prep()
    def test_wrong_project_blocked(self):
        p=self.prep();receipt=self.receipt();receipt['url']='https://example.com/devlog/123/test'
        with self.assertRaises(ValueError):record(p,receipt)
    def test_published_post_retry_does_not_duplicate(self):
        p=self.prep();receipt=self.receipt();record(p,receipt);before=p.read_bytes();record(p,receipt);self.prep();self.assertEqual(before,p.read_bytes())
        receipt['url']=PAGE+'/devlog/124/duplicate'
        with self.assertRaises(ValueError):record(p,receipt)
    def test_published_content_cannot_be_silently_replaced(self):
        p=self.prep();record(p,self.receipt());self.notes['blocks'][0]['text']='changed'
        with self.assertRaises(ValueError):self.prep()
if __name__=='__main__':unittest.main()
