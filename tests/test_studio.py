import importlib.util,json,tempfile,unittest,subprocess,sys
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'studio/game-studio/scripts/studio.py'
spec=importlib.util.spec_from_file_location('studio',SCRIPT)
studio=importlib.util.module_from_spec(spec);spec.loader.exec_module(studio)

class Studio(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.target=Path(self.temp.name)/'new-game'
    def init(self,app_id='com.example.newgame'):
        return studio.initialize(self.target,'new-game','新遊戲',app_id,'一款種花的離線遊戲')
    def test_real_cli_initializes_without_claiming_tests(self):
        output=subprocess.check_output([sys.executable,str(SCRIPT),'init','--target',str(self.target),'--id','new-game','--title','新遊戲','--app-id','com.example.newgame','--idea','種花'],encoding='utf-8')
        result=json.loads(output)
        self.assertFalse(result['tests_executed']);self.assertFalse(result['artifact_exists'])
        self.assertEqual(set(result['unconfigured_gates']),set(studio.GATES))
        self.assertIn('種花',(self.target/'IDEA.md').read_text(encoding='utf-8'))
    def test_existing_directory_preserved(self):
        self.target.mkdir();p=self.target/'user.txt';p.write_text('keep')
        with self.assertRaises(ValueError):self.init()
        self.assertEqual(p.read_text(),'keep')
    def test_previous_game_identity_rejected(self):
        with self.assertRaises(ValueError):self.init('com.demjastudio.gooblaster')
        self.assertFalse(self.target.exists())
    def test_invalid_identity_rejected_before_writing(self):
        with self.assertRaises(ValueError):self.init('../bad')
        self.assertFalse(self.target.exists())
    def test_no_inherited_commercial_authorization(self):
        p=self.init()
        self.assertFalse(any(p['authorization'].values()))
        self.assertIsNone(p['business']['price']);self.assertIsNone(p['test_channel'])
    def test_path_escape_rejected(self):
        p=self.init();p['artifact']='../outside.html'
        with self.assertRaises(ValueError):studio.validate(p,self.target)
    def test_shell_command_string_rejected(self):
        p=self.init();p['verification']['full']='python tests.py; publish'
        with self.assertRaises(ValueError):studio.validate(p,self.target)
    def test_current_project_configuration(self):
        result=studio.inspect(SCRIPT.parents[3])
        self.assertEqual(result['project'],'goo-blaster')
        self.assertTrue(result['artifact_exists']);self.assertFalse(result['release_approved'])

if __name__=='__main__':unittest.main()
