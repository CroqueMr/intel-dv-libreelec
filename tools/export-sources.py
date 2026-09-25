# SPDX-License-Identifier: MIT
"""Stage the pinned source material accompanying a binary release, without build outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(*command):
    return subprocess.check_output(command, text=True).strip()


def export(tree, output):
    manifest = json.loads((ROOT / 'config/dvbridge-overlay.json').read_text())
    if run('git', '-C', str(tree), 'rev-parse', 'HEAD') != manifest['libreelec']:
        raise ValueError('Build tree does not use the pinned LibreELEC revision')
    for destination, digest in manifest['files'].items():
        if sha(tree / destination) != digest:
            raise ValueError('Build overlay differs from the release: ' + destination)
    builds = list(tree.glob('build.LibreELEC-Generic.x86_64-*'))
    if len(builds) != 1:
        raise ValueError('Expected one build configuration')
    kernel_config = builds[0] / 'build/linux-7.2.6/.config'
    if not kernel_config.is_file():
        raise ValueError('Missing generated kernel configuration')

    # Do not export the checkout's .git/config, build caches, logs, credentials
    # or local history. The bare clone below contains only the pinned upstream.
    cache = tree / 'sources'
    cache_files = sorted(p for p in cache.rglob('*') if p.is_file())
    if any(p.is_symlink() for p in cache.rglob('*')):
        raise ValueError('Source cache must not contain symlinks')
    archives = [p for p in cache_files if p.suffix not in ('.sha256', '.url')]
    if not archives:
        raise ValueError('Empty source cache')
    checksums = {}
    for archive in archives:
        # Generic also downloads the stock NVIDIA redistributable. Preserve it
        # verbatim with its separate terms; it is not part of our Intel DV code.
        nvidia = archive.relative_to(cache).as_posix() == 'nvidia/nvidia-580.178.04.run'
        if not nvidia and not re.search(r'\.(?:tar\.(?:gz|xz|bz2|zst)|tgz|zip)$', archive.name):
            raise ValueError('Unreviewed source archive type: ' + archive.name)
        sidecar = Path(str(archive) + '.sha256')
        expected = sidecar.read_text().strip()
        if not re.fullmatch('[0-9a-f]{64}', expected) or sha(archive) != expected:
            raise ValueError('Invalid cached source checksum: ' + archive.name)
        origin = Path(str(archive) + '.url')
        url = urlsplit(origin.read_text().strip())
        if url.scheme not in ('http', 'https', 'ftp') or not url.hostname or url.username or url.password:
            raise ValueError('Private or unsupported source origin: ' + archive.name)
        checksums[archive.relative_to(cache).as_posix()] = expected

    output.mkdir(parents=True, exist_ok=False)
    bare = output / 'LibreELEC-upstream.git'
    subprocess.run(['git', 'clone', '--bare', '--no-hardlinks', str(tree), str(bare)], check=True)
    subprocess.run(['git', '--git-dir=' + str(bare), 'remote', 'remove', 'origin'], check=True)
    # A shallow upstream clone is intentional; no private development history
    # is required to reproduce the pinned tree and its separately shipped overlay.
    if run('git', '--git-dir=' + str(bare), 'rev-list', '--count', 'HEAD') != '1':
        raise ValueError('Expected the reviewed single-commit upstream snapshot')
    for path in cache_files:
        target = output / 'sources' / path.relative_to(cache)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copytree(ROOT, output / 'intel-dv-libreelec',
                    ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    shutil.copy2(kernel_config, output / 'kernel.config')
    notices = output / 'third-party-notices'
    notices.mkdir()
    shutil.copy2(builds[0] / 'build/nvidia-580.178.04/LICENSE', notices / 'NVIDIA-driver-LICENSE.txt')
    shutil.copy2(ROOT / 'docs/SOURCE-BUNDLE.md', output / 'README.md')
    (output / 'source-cache.json').write_text(json.dumps({
        'libreelec': manifest['libreelec'],
        'description': 'Verified build source cache; may include unused build dependencies.',
        'archives': checksums,
    }, indent=2) + '\n')
    inventory = []
    for path in sorted(output.rglob('*')):
        if path.is_file():
            inventory.append(sha(path) + '  ' + path.relative_to(output).as_posix())
    (output / 'BUNDLE-SHA256SUMS').write_text('\n'.join(inventory) + '\n')
    return {'archives': len(archives), 'inventoried_files': len(inventory),
            'upstream_revision': manifest['libreelec']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.tree.resolve(strict=True), args.output.resolve()), indent=2))
