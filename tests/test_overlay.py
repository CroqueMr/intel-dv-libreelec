"""Local fixture tests for the non-destructive overlay installer."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('overlay', Path(__file__).parents[1] / 'apply-overlay.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.tree = self.base / 'checkout'
        self.tree.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Overlay fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.tree / 'recipe').write_text('original\n')
        self.git('add', 'recipe')
        self.git('commit', '-qm', 'fixture baseline')
        self.bundle = self.base / 'bundle'
        (self.bundle / 'overlay').mkdir(parents=True)
        (self.bundle / 'overlay/recipe').write_text('updated\n')
        self.manifest = {'libreelec': self.git('rev-parse', 'HEAD').strip(), 'files': {
            'recipe': hashlib.sha256(b'updated\n').hexdigest()}}
        self.save()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.tree), *args], text=True)

    def save(self):
        (self.bundle / 'dvbridge-overlay.json').write_text(json.dumps(self.manifest))

    def unchanged(self):
        self.assertEqual((self.tree / 'recipe').read_text(), 'original\n')
        self.assertFalse((self.tree / 'dvbridge-overlay.json').exists())

    def test_valid_and_repeat_rejected(self):
        module.apply(self.bundle, self.tree)
        self.assertEqual((self.tree / 'recipe').read_text(), 'updated\n')
        with self.assertRaises(ValueError):
            module.apply(self.bundle, self.tree)

    def test_dirty_checkout_preserved(self):
        (self.tree / 'user-note').write_text('keep\n')
        with self.assertRaises(ValueError):
            module.apply(self.bundle, self.tree)
        self.unchanged()
        self.assertEqual((self.tree / 'user-note').read_text(), 'keep\n')

    def test_all_hashes_before_first_write(self):
        (self.bundle / 'overlay/bad').write_text('bad\n')
        self.manifest['files']['bad'] = '0' * 64
        self.save()
        with self.assertRaises(ValueError):
            module.apply(self.bundle, self.tree)
        self.unchanged()

    def test_wrong_revision(self):
        self.manifest['libreelec'] = '0' * 40
        self.save()
        with self.assertRaises(ValueError):
            module.apply(self.bundle, self.tree)
        self.unchanged()

    def test_path_escape(self):
        (self.bundle / 'outside').write_bytes(b'outside')
        self.manifest['files']['../outside'] = hashlib.sha256(b'outside').hexdigest()
        self.save()
        with self.assertRaises(ValueError):
            module.apply(self.bundle, self.tree)
        self.unchanged()


if __name__ == '__main__':
    unittest.main()
