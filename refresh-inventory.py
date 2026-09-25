# SPDX-License-Identifier: MIT
"""Regenerate only the repository byte inventory after reviewed source changes."""
import hashlib
from pathlib import Path
from verify import source_files

root = Path(__file__).resolve().parent
(root / 'SOURCE-FILES.sha256').write_text(''.join(
    hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + name + '\n'
    for name, path in sorted(source_files(root).items())), encoding='utf-8', newline='\n')
print('Source inventory refreshed; overlay/provenance/license hashes were not rewritten.')
