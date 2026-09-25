# SPDX-License-Identifier: MIT
"""Keep everyday edits easy while retaining meaningful release-input checks."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_verify', REPO / 'tools/verify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', 'host-tests', 'build-output'))

    def passes(self):
        self.assertEqual(module.verify(self.root)['checks'], 'passed')

    def test_source_archive_without_git_or_inventory(self):
        self.assertFalse((self.root / '.git').exists())
        self.assertFalse((self.root / 'SOURCE-FILES.sha256').exists())
        self.passes()

    def test_documentation_edit(self):
        (self.root / 'docs/HARDWARE.md').write_text('Updated hardware notes.\n')
        self.passes()

    def test_new_documentation_and_text_tool(self):
        (self.root / 'docs/FAQ.md').write_text('A new explanation.\n')
        (self.root / 'tools/example.py').write_text('print("example")\n')
        self.passes()

    def test_binary_illustration_does_not_crash_text_scan(self):
        (self.root / 'docs/illustration.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        self.passes()

    def test_git_ignores_local_outputs_but_scans_new_sources(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        output = self.root / 'build-output'
        output.mkdir()
        key = 'ghp_' + 'a' * 36  # Synthetic token-shaped test input, not a credential.
        (output / 'local.json').write_text(key)
        self.passes()
        (self.root / 'tools/new-source.txt').write_text(key)
        with self.assertRaisesRegex(ValueError, 'Private-data pattern'):
            module.verify(self.root)

    def test_git_still_scans_tracked_ignored_files(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / 'example.log').write_text('ghp_' + 'b' * 36)
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', 'example.log'], check=True)
        with self.assertRaisesRegex(ValueError, 'Private-data pattern'):
            module.verify(self.root)

    def test_changed_runtime_patch_is_rejected(self):
        patch = next((self.root / 'patches/libplacebo').glob('*.patch'))
        patch.write_bytes(patch.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'Overlay checksum mismatch'):
            module.verify(self.root)

    def test_missing_build_input_is_rejected(self):
        next((self.root / 'patches/libplacebo').glob('*.patch')).unlink()
        with self.assertRaisesRegex(ValueError, 'Unsafe or missing file'):
            module.verify(self.root)

    def test_license_change_is_rejected(self):
        (self.root / 'LICENSES/GPL-3.0.txt').write_text('Incorrect license\n')
        with self.assertRaisesRegex(ValueError, 'Canonical license mismatch'):
            module.verify(self.root)

    def test_secret_in_documentation_is_rejected(self):
        (self.root / 'docs/new.md').write_text('ghp_' + 'c' * 36)
        with self.assertRaisesRegex(ValueError, 'Private-data pattern'):
            module.verify(self.root)

    def test_overlay_destination_escape_is_rejected(self):
        path = self.root / 'config/dvbridge-overlay.json'
        manifest = json.loads(path.read_text())
        manifest['files']['../outside'] = '0' * 64
        manifest['source_map']['../outside'] = 'README.md'
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Unsafe overlay destination'):
            module.verify(self.root)

    def test_unknown_patch_is_rejected(self):
        (self.root / 'patches/libplacebo/unmapped.patch').write_text('unmapped\n')
        with self.assertRaisesRegex(ValueError, 'Unmapped patch'):
            module.verify(self.root)


if __name__ == '__main__':
    unittest.main()
