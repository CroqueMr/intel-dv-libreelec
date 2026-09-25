# Validation

## What the evidence means

Source checks, software tests and physical HDMI playback are separate results.
The i7-11390H/LG G5 implementation passed the recorded successful native playback
protocols without an observed playback problem. That is not universal hardware
qualification or certification. A freshly packaged release image is identified
separately in its build receipt; prior hardware results are not silently
relabelled as tests of a different binary.

| Area | Recorded coverage |
| --- | --- |
| Native HDMI playback | P5, P7 FEL, P8.1 CM4, P8.4 CM4 and P10 CM4 on i7-11390H. |
| FEL reconstruction | Demonstrable enhancement-layer contribution; exact GPU output comparisons, including active-area masking and orientation. |
| Optimized renderer | Eight deterministic 4K cases, 33,177,600 transport bytes per case, equal to the separate full-precision path. Additional real-frame comparisons on six sources. |
| Steady playback | Bounded uninterrupted cadence checks, including 23.976 fps; no observed increasing steady drop counters or irregular new-frame intervals in successful runs. |
| Controls and restore | Pause, resume, seek, player OSD, subtitles, audio-track switching, stop and return to the 4K60 interface. |
| Non-DV control | HDR10 source without RPU stays on Kodi's native HDR path, with the DV connector property disabled. |
| Upstream menus | Original LibreELEC settings/service; no activation addon or environment switch. |
| Software | 14 C/C++ host checks with ASan/UBSan; 14 Python source/installer/image-path checks. |

P7 MEL has explicit code/software coverage; P8.2 shares the metadata/reshaping
pipeline. Neither has a dedicated physical LE qualification result in this
release. P9 is not supported by the pinned H.264 metadata pipeline. P10 playback
evidence does not qualify every profile-10 compatibility variant or 4K60 workload.

Startup, final-frame and user-interaction disturbances are recorded separately.
Uncommanded drops/duplicates during steady playback remain failures. A missing
image, wrong colors, lost enhancement layer or stale frame metadata is never
accepted as a successful DV result merely because the TV shows a DV logo.

## Run the portable checks

Run the test suite on Linux, including a Linux filesystem in WSL. The image-path
tests require Linux symlink semantics; native Windows is not a supported test or
build host. The checks do not require the target Intel PC or an attached TV.

```sh
python3 tools/verify.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Use Python 3.12 or later for archive extraction. The source checker verifies
build-input hashes, patch mappings, descriptions, canonical license texts,
inherited-header receipts and generic private-data patterns. It is a useful
gate, not a substitute for code review. Editing documentation or adding a normal
source file does not require regenerating a repository-wide checksum inventory.
Ignored local build outputs are not scanned in a Git checkout.

For C/C++ tests, install CMake, Ninja, compilers, pkg-config, Mesa EGL/GLES/GBM
development files, libdrm development files and llvmpipe. Build native-host
dependencies from the same source cache with Meson, Make, LCMS2 development
files and glad/Jinja2 available:

```sh
python3 tools/build-host-test-deps.py --source-cache /path/to/LibreELEC-DV/sources \
  --output /path/to/new-host-dependencies --jobs 4
python3 tools/check-patches.py --source-cache /path/to/LibreELEC-DV/sources \
  --output /path/to/new-source-check
export HOST_PREFIX=/path/to/new-host-dependencies/prefix
export KODI_SOURCE=/path/to/new-source-check/kodi/xbmc-b7afba240133a570145466cfaf6a6825f84c6ad1
export PKG_CONFIG_PATH="$HOST_PREFIX/lib/pkgconfig"
cmake -S tests/host-build -B host-tests -G Ninja \
  -DDVBRIDGE_KODI_SOURCE="$KODI_SOURCE" \
  -DDVBRIDGE_COMMON_SOURCE="$KODI_SOURCE/tools/dvbridge"
cmake --build host-tests --parallel 4
ctest --test-dir host-tests --output-on-failure
```

The host-only minimal FFmpeg and llvmpipe renderer are **not** the target VAAPI
stack. Decoder responses are mocked in the layer-queue test. DRM transaction
tests inject failures; they do not certify an HDMI output. Assertions stay
enabled even for Release test builds.

On a suitable real GPU, `-DDVBRIDGE_TEST_GPU_EXACT=ON` adds the strict 4K
fused-versus-composed byte comparison. It requires fragment basic/quad subgroup
support and is not enabled for the default software-only suite.

## Image checks

```sh
python3 tools/audit-image.py --tree /path/to/LibreELEC-DV \
  --image /path/to/LibreELEC-DV/target/selected-image.img.gz \
  --output image-audit.json
```

This checks the built image's dependencies, runtime search paths, DV build
configuration, native settings, source manifest and compressed-image checksum.
Dynamic drivers/plugins still need runtime checks. The optional `tools/boot-smoke.py`
boots a disposable copy in QEMU, without network or physical disks; its virtual
GPU cannot validate Intel decoding or DV reception.

Tests under `tests/` are intentionally distributed so reviewers can reproduce
the checks. They are not installed in the image and are not runtime debug hooks.
