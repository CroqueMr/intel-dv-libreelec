# SPDX-License-Identifier: MIT
"""Boot a disposable copy of a local image; no physical disk or network access."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import socket
import subprocess
import time


def boot(image, kernel, output, graphical=False):
    output.mkdir(parents=True, exist_ok=False)
    raw = output / 'source.img'
    with gzip.open(image, 'rb') as source, raw.open('xb') as target:
        shutil.copyfileobj(source, target, length=1024 * 1024)
    overlay = output / 'guest.qcow2'
    subprocess.run(['qemu-img', 'create', '-f', 'qcow2', '-F', 'raw', '-b',
                    str(raw.resolve()), str(overlay)], check=True)
    serial = output / 'serial.log'
    qmp = output / 'qmp.sock'
    command = ['qemu-system-x86_64', '-enable-kvm', '-cpu', 'host', '-smp', '2', '-m', '2048',
               '-display', 'none', '-vga', 'virtio' if graphical else 'std', '-nic', 'none', '-monitor', 'none',
               '-qmp', 'unix:' + str(qmp) + ',server=on,wait=off',
               '-serial', 'file:' + str(serial), '-no-reboot', '-kernel', str(kernel),
               '-append', 'boot=/dev/vda1 disk=/dev/vda2 console=tty0 '
                          'systemd.log_target=console' +
                          ('' if graphical else ' systemd.unit=multi-user.target'),
               '-drive', 'file=' + str(overlay) + ',format=qcow2,if=virtio']
    timed_out = False
    with (output / 'qemu.log').open('w') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(60):
                if process.poll() is not None:
                    break
                time.sleep(1)
            if process.poll() is None:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                    client.settimeout(5)
                    client.connect(str(qmp))
                    stream = client.makefile('rwb')
                    stream.readline()
                    for request in [{'execute': 'qmp_capabilities'},
                                    {'execute': 'screendump', 'arguments': {
                                        'filename': str(output / 'screen.png'), 'format': 'png'}}]:
                        stream.write((json.dumps(request) + '\n').encode())
                        stream.flush()
                        while True:
                            answer = json.loads(stream.readline())
                            if 'error' in answer:
                                raise RuntimeError(answer)
                            if 'return' in answer:
                                break
                timed_out = True
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                return_code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                return_code = process.wait()
    text = serial.read_text(errors='replace') if serial.exists() else ''
    report = {'image': image.name, 'kernel': kernel.name, 'timeout': timed_out,
              'qemu_return_code': return_code,
              'serial_systemd_seen': 'systemd[' in text,
              'serial_multi_user_seen': 'Reached target Multi-User System' in text,
              'framebuffer_capture': (output / 'screen.png').is_file(),
              'serial_kernel_panic_seen': 'Kernel panic' in text,
              'framebuffer_review_required': True,
              'graphical_boot_requested': graphical,
              'scope': ('Disposable virtual-GPU boot; framebuffer review required; no Intel decoder or HDMI validation'
                        if graphical else 'Disposable VM boot only; no Kodi, Intel decoder or HDMI validation')}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('kernel', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--graphical', action='store_true')
    args = parser.parse_args()
    boot(args.image.resolve(strict=True), args.kernel.resolve(strict=True), args.output.resolve(), args.graphical)
