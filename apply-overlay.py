# SPDX-License-Identifier: MIT
"""Apply a checksummed DV overlay to a fresh, pinned LibreELEC checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def apply(bundle, tree):
    manifest = json.loads((bundle / 'dvbridge-overlay.json').read_text())
    tree = tree.resolve(strict=True)
    git = ['git', '-C', str(tree)]
    if subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip() != manifest['libreelec']:
        raise ValueError('LibreELEC revision does not match the pinned overlay')
    if subprocess.check_output(git + ['status', '--porcelain', '--untracked-files=normal']):
        raise ValueError('Use a clean checkout; existing modifications will not be overwritten')
    validated = []
    for relative, digest in manifest['files'].items():
        source = (bundle / manifest.get('source_map', {}).get(relative, 'overlay/' + relative)).resolve(strict=True)
        destination = (tree / relative).resolve()
        if not source.is_relative_to(bundle.resolve()) or not destination.is_relative_to(tree):
            raise ValueError('Overlay path escapes its root')
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError('Overlay checksum mismatch: ' + relative)
        validated.append((source, destination))
    for source, destination in validated:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    shutil.copyfile(bundle / 'dvbridge-overlay.json', tree / 'dvbridge-overlay.json')
    print(f'Applied {len(validated)} checked files. No build or installation was started.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    args = parser.parse_args()
    apply(Path(__file__).resolve().parent, args.checkout)
