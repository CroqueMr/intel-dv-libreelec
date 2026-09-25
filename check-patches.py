# SPDX-License-Identifier: MIT
"""Apply the release patch series to fresh, checksum-verified upstream sources."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

SOURCES = {
    'linux': ('linux-7.2.6.tar.xz', '039aef84f2b0994aeda3f4fcfc3d02ec9d7a9bbb9020ea264c43f446c860f606'),
    'kodi': ('kodi-b7afba240133a570145466cfaf6a6825f84c6ad1.tar.gz', '0b01a5168764cd95930f294bd0e9f19f8b160577d8d20b58538f4cb99ea98f78'),
    'ffmpeg': ('ffmpeg-9.0.tar.xz', '7f607a00dd0d28a729d5a4811205812eef01cf6ef6155025febb6f36a9062d52'),
    'libplacebo': ('libplacebo-e2972fdd09adacd383656738d7d280f0cd84a761.tar.gz', '2dc029b7686455054fb5e76dd8c084cbf4fa4159f33364c5b7f9afc8b3611811'),
}

def check(root, cache, output):
    # Validate all inputs before extracting any component. Python 3.12's data
    # filter also rejects archive paths escaping the dedicated output directory.
    archives = {}
    for component, (name, digest) in SOURCES.items():
        archive = cache / component / name
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError('Wrong upstream archive: ' + name)
        archives[component] = archive
    output.mkdir(parents=True, exist_ok=False)
    result = {}
    for component, archive in archives.items():
        directory = output / component
        directory.mkdir()
        with tarfile.open(archive) as source:
            source.extractall(directory, filter='data')
        roots = list(directory.iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise ValueError('Unexpected source archive layout')
        patches = sorted((root / 'patches' / component).glob('*.patch'))
        log = []
        for patch in patches:
            proc = subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(patch)],
                                  cwd=roots[0], capture_output=True, text=True)
            log.append(proc.stdout + proc.stderr)
            if proc.returncode:
                (output / (component + '.log')).write_text('\n'.join(log))
                raise RuntimeError('Patch failed: ' + patch.name)
        (output / (component + '.log')).write_text('\n'.join(log))
        result[component] = {'patches': len(patches), 'archive_sha256': SOURCES[component][1],
                             'applied': True, 'compiled': False}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(Path(__file__).resolve().parent, args.source_cache.resolve(), args.output.resolve())
