# SPDX-License-Identifier: MIT
"""Inspect a built experimental image without executing target binaries."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def resolve_image_path(image, path):
    """Resolve symlinks against the target root, never the build host's root."""
    image = image.resolve()
    parts = list(path.relative_to(image).parts)
    resolved = []
    links = 0
    while parts:
        part = parts.pop(0)
        if part in ('', '.'):
            continue
        if part == '..':
            if not resolved:
                raise ValueError('Image symlink escapes its root')
            resolved.pop()
            continue
        candidate = image.joinpath(*resolved, part)
        if candidate.is_symlink():
            links += 1
            if links > 40:
                raise ValueError('Image symlink cycle')
            target = candidate.readlink()
            if target.is_absolute():
                resolved = []
                parts = list(target.parts[1:]) + parts
            else:
                parts = list(target.parts) + parts
        else:
            resolved.append(part)
    return image.joinpath(*resolved)


def dependency_closure(image, player, readelf):
    """Check DT_NEEDED recursively; runtime-loaded plugins need separate tests."""
    pending = [player]
    checked = {}
    while pending:
        binary = resolve_image_path(image, pending.pop())
        relative = binary.relative_to(image).as_posix()
        if relative in checked:
            continue
        dynamic = subprocess.check_output([str(readelf), '-d', str(binary)], text=True)
        needed = re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic)
        rpaths = re.findall(r'\((?:RPATH|RUNPATH)\).*?\[(.*?)\]', dynamic)
        search = [image / 'usr/lib', image / 'lib', image / 'usr/lib64', image / 'lib64']
        for rpath in rpaths:
            for directory in rpath.split(':'):
                directory = directory.replace('${ORIGIN}', '$ORIGIN')
                if directory == '$ORIGIN' or directory.startswith('$ORIGIN/'):
                    search.insert(0, binary.parent / directory[len('$ORIGIN/'):])
                elif directory.startswith('/') and not re.search(r'/home/|/mnt/|build\.LibreELEC', directory):
                    search.insert(0, image / directory.lstrip('/'))
                else:
                    raise ValueError('Unreviewed runtime search path in ' + relative)
        dependencies = {}
        for name in needed:
            if '/' in name:
                raise ValueError('Path-dependent library requirement in ' + relative)
            candidates = [resolve_image_path(image, directory / name) for directory in search]
            library = next((candidate for candidate in candidates if candidate.is_file()), None)
            if library is None:
                raise ValueError('Missing image dependency: ' + relative + ' -> ' + name)
            dependencies[name] = library.relative_to(image).as_posix()
            pending.append(library)
        checked[relative] = dependencies
    return checked


def audit(tree, selected_image=None):
    builds = list(tree.glob('build.LibreELEC-Generic.x86_64-*'))
    if len(builds) != 1:
        raise ValueError('Expected one Generic build directory')
    build = builds[0]
    image = build / 'image/system'
    player = image / 'usr/lib/kodi/kodi.bin'
    if not player.is_file():
        raise ValueError('No assembled Kodi player')
    readelf = build / 'toolchain/bin/x86_64-libreelec-linux-gnu-readelf'
    dynamic = subprocess.check_output([str(readelf), '-d', str(player)], text=True)
    needed = re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic)
    if 'libplacebo.so.372' not in needed:
        raise ValueError('Kodi is not linked to the pinned shared DV renderer')
    if re.search(r'\((?:RPATH|RUNPATH)\).*?(?:/home/|/mnt/|build\.LibreELEC)', dynamic):
        raise ValueError('Build-host path leaked into runtime library lookup')
    libraries = {}
    for name in needed:
        candidates = [p for p in (image / 'usr/lib').rglob(name)
                      if resolve_image_path(image, p).is_file()]
        if not candidates:
            raise ValueError('Direct player dependency is absent from the image: ' + name)
        libraries[name] = [str(p.relative_to(image)) for p in candidates]
    closure = dependency_closure(image, player, readelf)
    kernels = list((build / 'build').glob('linux-*/vmlinux'))
    if len(kernels) != 1:
        raise ValueError('Expected one linked kernel for the image')
    nm = build / 'toolchain/bin/x86_64-libreelec-linux-gnu-nm'
    symbols = subprocess.check_output([str(nm), str(kernels[0])], text=True)
    for name in ('__param_enable_dv_lab', 'intel_dv_lab_scanout_check'):
        if not re.search(r'\b' + name + r'$', symbols, re.M):
            raise ValueError('Expected DV kernel policy symbol is absent: ' + name)
    sources = list((build / 'build').glob('kodi-*'))
    caches = [p for source in sources for p in source.glob('.x86_64-libreelec-linux-gnu/CMakeCache.txt')]
    if len(caches) != 1 or 'ENABLE_DVBRIDGE:BOOL=ON' not in caches[0].read_text():
        raise ValueError('Experimental Kodi configuration was not built')
    service = image / 'usr/lib/systemd/system/kodi.service'
    if service.exists() and ('DVBRIDGE_KODI_ENABLE' in service.read_text() or
                             'dvbridge/kodi.conf' in service.read_text()):
        raise ValueError('Obsolete manual DV activation remains in the service')
    addon = image / 'usr/share/kodi/addons/service.libreelec.settings'
    if list(addon.rglob('dvbridge_settings*')):
        raise ValueError('Obsolete DV settings module remains in the image')
    system_bytecode = addon / 'resources/lib/modules/system.pyc'
    if not system_bytecode.is_file() or b'dvbridge_settings' in system_bytecode.read_bytes():
        raise ValueError('Native System menu bytecode is missing or still imports the removed helper')
    manifest = json.loads((tree / 'dvbridge-overlay.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((tree / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Build overlay changed since its recorded snapshot: ' + name)
    images = ([selected_image.resolve()] if selected_image else
              sorted((tree / 'target').glob('*.img.gz')))
    if selected_image and selected_image.resolve().parent != (tree / 'target').resolve():
        raise ValueError('Selected image must be an artifact from this build tree')
    if len(images) != 1:
        raise ValueError('Expected one completed image, not ambiguous/stale build products')
    digest = hashlib.sha256(images[0].read_bytes()).hexdigest()
    sidecar = Path(str(images[0]) + '.sha256')
    if not sidecar.is_file() or sidecar.read_text().split()[0] != digest:
        raise ValueError('Image checksum sidecar missing or inconsistent')
    return {'image': images[0].name, 'sha256': digest, 'direct_dependencies': libraries,
            'elf_dependency_closure': closure,
            'source_pins': {'libreelec': manifest['libreelec'], 'kodi': manifest['kodi']},
            'adapter_compiled': True, 'automatic_eligible_dv': True,
            'stock_service_enables_dv': False,
            'kernel_opt_in_compiled': True,
            'hardware_validated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--image', type=Path)
    args = parser.parse_args()
    result = json.dumps(audit(args.tree, args.image), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    print(result, end='')
