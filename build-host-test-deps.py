# SPDX-License-Identifier: MIT
"""Build pinned native test dependencies from an existing LibreELEC source cache."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

SOURCES = {
    'ffmpeg': ('ffmpeg-9.0.tar.xz', '7f607a00dd0d28a729d5a4811205812eef01cf6ef6155025febb6f36a9062d52'),
    'libplacebo': ('libplacebo-e2972fdd09adacd383656738d7d280f0cd84a761.tar.gz',
                   '2dc029b7686455054fb5e76dd8c084cbf4fa4159f33364c5b7f9afc8b3611811'),
}


def build(bundle, cache, output, jobs):
    manifest = json.loads((bundle / 'dvbridge-overlay.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((bundle / manifest['source_map'][name]).read_bytes()).hexdigest() != digest:
            raise ValueError('Overlay hash mismatch: ' + name)
    archives = {}
    for component, (name, digest) in SOURCES.items():
        archive = cache / component / name
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError('Source archive hash mismatch: ' + name)
        archives[component] = archive
    output.mkdir(parents=True, exist_ok=False)
    prefix = output / 'prefix'
    with (output / 'build.log').open('w') as log:
        def run(command, cwd):
            print(' '.join(map(str, command)), file=log, flush=True)
            subprocess.run(list(map(str, command)), cwd=cwd, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        trees = {}
        for component, archive in archives.items():
            with tarfile.open(archive) as source:
                source.extractall(output, filter='data')
            tree = next(p for p in output.glob(component + '-*') if p.is_dir())
            trees[component] = tree
            directory = ('projects/Generic/patches/ffmpeg' if component == 'ffmpeg' else
                         'packages/addons/addon-depends/multimedia-tools-depends/libplacebo/patches')
            for patch in sorted((bundle / 'patches' / component).glob('*.patch')):
                run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', patch], tree)
        run(['./configure', '--disable-everything', '--disable-programs', '--disable-doc',
             '--disable-x86asm', '--enable-decoder=hevc', '--enable-protocol=file',
             '--enable-demuxer=mov,matroska', '--enable-parser=hevc', '--enable-bsf=dovi_split',
             '--disable-autodetect', '--prefix=' + str(prefix)], trees['ffmpeg'])
        run(['make', '-j' + str(jobs)], trees['ffmpeg'])
        run(['make', 'install'], trees['ffmpeg'])
        plbuild = output / 'placebo-build'
        run(['meson', 'setup', plbuild, trees['libplacebo'], '--prefix=' + str(prefix),
             '--libdir=lib', '-Dopengl=enabled', '-Dgl-proc-addr=enabled', '-Ddovi=enabled',
             '-Dlibdovi=disabled', '-Dvulkan=disabled', '-Dglslang=disabled',
             '-Dshaderc=disabled', '-Dlcms=enabled', '-Dtests=true', '-Ddemos=false',
             '-Dc_args=-DCI_ALLOW_SW'], output)
        run(['meson', 'compile', '-C', plbuild, '-j', str(jobs)], output)
        run(['meson', 'install', '-C', plbuild], output)
    print('Native test prefix: ' + str(prefix))
    print('This minimal host FFmpeg is for software tests, not hardware playback.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--source-cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 64:
        parser.error('jobs must be between 1 and 64')
    build(args.bundle.resolve(), args.source_cache.resolve(), args.output.resolve(), args.jobs)
