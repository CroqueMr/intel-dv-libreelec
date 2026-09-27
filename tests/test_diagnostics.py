# SPDX-License-Identifier: MIT
"""Check diagnostic isolation and failure throttling without GPU hardware."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Diagnostics(unittest.TestCase):
    def test_rate_limit(self):
        compiler = shutil.which('g++')
        if not compiler:
            self.skipTest('C++ compiler required; Linux release/CI runs this test')
        spec = importlib.util.spec_from_file_location('verify_diagnostics', ROOT / 'tools/verify.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        patch = (ROOT / 'patches/kodi/kodi-9991-diagnostics.patch').read_text()
        header = module.new_file(patch, 'xbmc/utils/DVBridgeDiagnosticState.h')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'utils').mkdir()
            (root / 'utils/DVBridgeDiagnosticState.h').write_bytes(header)
            subprocess.run([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                            '-UNDEBUG', '-I' + str(root), str(ROOT / 'tests/diagnostic_rate_limit.cpp'),
                            '-o', str(root / 'check')], check=True)
            subprocess.run([str(root / 'check')], check=True)

    def test_no_shader_or_metadata_changes(self):
        for component, name in [('kodi', 'kodi-9991-diagnostics.patch'),
                                ('linux', 'linux-9902-dv-diagnostics.patch')]:
            text = (ROOT / 'patches' / component / name).read_text()
            self.assertNotIn('+++ b/tools/dvbridge/', text)
            self.assertNotIn('+++ b/drivers/gpu/drm/i915/display/intel_dv_lab_policy.h', text)
            self.assertNotIn('glReadPixels', text)
            self.assertNotIn('glFinish', '\n'.join(line for line in text.splitlines()
                                                   if line.startswith('+')))

    def test_collector_does_not_upload_or_restart(self):
        text = (ROOT / 'overlay/projects/Generic/filesystem/usr/bin/dv-diagnostics').read_text()
        for command in ['curl ', 'wget ', 'systemctl ', 'reboot', 'pastekodi']:
            self.assertNotIn(command, text)
        self.assertIn('umask 077', text)
        self.assertIn('journalctl -k -b', text)
