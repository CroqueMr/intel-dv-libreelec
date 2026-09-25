# SPDX-License-Identifier: MIT
"""Ensure the source release retains automatic eligibility and upstream menus."""
import json
from pathlib import Path
import unittest

LAB = Path(__file__).resolve().parents[1]

class AutomaticPolicy(unittest.TestCase):
    def test_no_custom_settings_sources(self):
        manifest = json.loads((LAB / 'config/dvbridge-overlay.json').read_text())
        self.assertEqual(manifest['settings'], 'upstream_unmodified')
        self.assertFalse(manifest['runtime_opt_in_required'])
        self.assertFalse(any('LibreELEC-settings' in path or path.endswith('kodi.service')
                             for path in manifest['files']))

    def test_no_player_environment_switch(self):
        source = LAB / 'patches/kodi/kodi-9990-native-dv.patch'
        self.assertNotIn('DVBRIDGE_KODI_ENABLE', source.read_text())
        self.assertNotIn('DVBRIDGE_CM4_TRACE', source.read_text())

    def test_automatic_kernel_default(self):
        paths = list((LAB / 'patches/linux').glob('*intel_display_params.h.patch'))
        self.assertEqual(len(paths), 1)
        self.assertIn('param(bool, enable_dv_lab, true, 0)', paths[0].read_text())

if __name__ == '__main__':
    unittest.main()
