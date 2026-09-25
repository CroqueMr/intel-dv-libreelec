# SPDX-License-Identifier: MIT
"""Check build inputs, licenses and accidental private data without freezing docs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def checked(root, name):
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Unsafe or missing file: ' + name)
    return path

def source_files(root):
    """Respect Git's ignore rules, with a source-archive fallback (no Git needed)."""
    if (root / '.git').exists():
        result = subprocess.run(
            ['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
            capture_output=True, check=True)
        names = set(result.stdout.decode('utf-8').split('\0')) - {''}
        return {name: checked(root, name) for name in names
                if (root / name).exists() or (root / name).is_symlink()}
    ignored = {'.git', '__pycache__', 'host-tests', 'build-output', '.venv', 'venv'}
    return {p.relative_to(root).as_posix(): checked(root, p.relative_to(root).as_posix())
            for p in root.rglob('*') if (p.is_file() or p.is_symlink())
            and not ignored.intersection(p.relative_to(root).parts)
            and p.suffix != '.pyc'}

def new_file(patch, name):
    match = re.search(r'--- /dev/null\n\+\+\+ b/' + re.escape(name) + r'\n@@ -0,0 \+1,(\d+) @@\n', patch)
    if not match:
        raise ValueError('Missing new source file: ' + name)
    lines = patch[match.end():].splitlines(True)[:int(match[1])]
    if len(lines) != int(match[1]) or not all(line.startswith('+') for line in lines):
        raise ValueError('Invalid new-file hunk')
    return ''.join(line[1:] for line in lines).encode()

def verify(root):
    files = source_files(root)
    # Git already versions the repository. Only build inputs and canonical
    # license/provenance records need byte-exact validation, not prose or CI files.
    canonical = json.loads((root / 'LICENSES/canonical-checksums.json').read_text())
    for name, digest in canonical['files'].items():
        if sha(checked(root / 'LICENSES', name)) != digest:
            raise ValueError('Canonical license mismatch: ' + name)
    if 'Version 3, 29 June 2007' not in (root / 'LICENSES/GPL-3.0.txt').read_text():
        raise ValueError('Incorrect GPLv3 license text')
    manifest = json.loads((root / 'config/dvbridge-overlay.json').read_text())
    if manifest['files'].keys() != manifest['source_map'].keys():
        raise ValueError('Overlay mapping mismatch')
    for destination, digest in manifest['files'].items():
        if Path(destination).is_absolute() or '..' in Path(destination).parts:
            raise ValueError('Unsafe overlay destination')
        if sha(checked(root, manifest['source_map'][destination])) != digest:
            raise ValueError('Overlay checksum mismatch')
    patches = {p.relative_to(root).as_posix() for p in (root / 'patches').rglob('*.patch')}
    if patches != {p for p in manifest['source_map'].values() if p.endswith('.patch')}:
        raise ValueError('Unmapped patch')
    descriptions = json.loads((root / 'config/patch-index.json').read_text())
    if descriptions.keys() != patches:
        raise ValueError('Missing patch description')
    kodi = (root / 'patches/kodi/kodi-9990-native-dv.patch').read_text()
    receipt = json.loads(new_file(kodi, 'tools/dvbridge/PROVENANCE.json'))
    for name, digest in receipt['files'].items():
        if hashlib.sha256(new_file(kodi, 'tools/dvbridge/' + name)).hexdigest() != digest:
            raise ValueError('Inherited helper receipt mismatch')
    # Scan source text, including this checker. Generic patterns avoid embedding
    # the maintainer's private identifiers in the published security check.
    patterns = [r'(?i)-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----',
                r'(?i)\b(?:ghp|github_pat)_[a-z0-9_]{20,}',
                r'(?i)(?:api[_-]?key|password|token)\s*[=:]\s*["\'][a-z0-9_-]{16,}',
                r'(?i)(?:/home/|[a-z]:[\\/]+Users[\\/]+)[a-z0-9_.-]+[\\/]',
                r'\b192\.168\.\d{1,3}\.\d{1,3}\b']
    for name, path in files.items():
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # An illustration or other binary is not a malformed source tree.
            # This text scanner is not a binary-release or malware audit.
            continue
        for pattern in patterns:
            if re.search(pattern, text):
                raise ValueError('Private-data pattern found in ' + name)
        if path.suffix == '.patch' and re.search(r'^\+.*(?:DVBRIDGE_CM4_TRACE|glReadPixels|/storage/videos/)', text, re.M):
            raise ValueError('Development capture hook in runtime patch: ' + name)
    return {'source_files': len(files), 'functional_patches': len(patches),
            'overlay_files': len(manifest['files']), 'canonical_licenses': len(canonical['files']),
            'checks': 'passed', 'hardware_test': False}

if __name__ == '__main__':
    try:
        print(json.dumps(verify(ROOT), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Source check failed: {error}', file=sys.stderr)
        sys.exit(1)
