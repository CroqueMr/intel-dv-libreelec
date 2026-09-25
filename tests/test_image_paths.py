"""Target library symlinks must not accidentally resolve on the build host."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('image_audit', Path(__file__).parents[1] / 'tools/audit-image.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImagePaths(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'usr/lib').mkdir(parents=True)
        (self.root / 'usr/lib/libtest.so.1').touch()

    def tearDown(self):
        self.temp.cleanup()

    def check(self, target):
        link = self.root / 'usr/lib/libtest.so'
        link.symlink_to(target)
        return module.resolve_image_path(self.root, link)

    def test_absolute_target(self):
        self.assertEqual(self.check('/usr/lib/libtest.so.1'), self.root / 'usr/lib/libtest.so.1')

    def test_relative_target(self):
        self.assertTrue(self.check('libtest.so.1').is_file())

    def test_parent_target(self):
        self.assertTrue(self.check('../lib/libtest.so.1').is_file())

    def test_missing_target(self):
        self.assertFalse(self.check('/etc/passwd').exists())

    def test_escape(self):
        with self.assertRaises(ValueError):
            self.check('../../../etc/passwd')

    def test_cycle(self):
        with self.assertRaises(ValueError):
            self.check('libtest.so')


if __name__ == '__main__':
    unittest.main()
