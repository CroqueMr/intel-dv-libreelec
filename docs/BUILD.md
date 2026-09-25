# Build the image

Use an unprivileged Linux build user on a supported LibreELEC build host. Follow
the [official build prerequisites](https://wiki.libreelec.tv/development/build-basics).
Use a Linux filesystem with ample free space, not a Windows-mounted source tree.
This overlay targets **Generic**, not Generic-legacy/X11, ARM or CoreELEC.

## Reproduce this source revision

After obtaining this repository as `intel-dv-libreelec`:

```sh
python3 intel-dv-libreelec/verify.py
git clone https://github.com/LibreELEC/LibreELEC.tv.git LibreELEC-DV
git -C LibreELEC-DV checkout --detach 3de4708704041ead8ae1531092efb7ea5da9d355
python3 intel-dv-libreelec/apply-overlay.py LibreELEC-DV
cd LibreELEC-DV
PROJECT=Generic ARCH=x86_64 OFFICIAL=no \
  BUILDER_NAME=Intel-DV CUSTOM_VERSION=13.0-intel-dv-0.1.0-rc1 \
  CUSTOM_IMAGE_NAME=LibreELEC-Generic.x86_64-13.0-intel-dv-0.1.0-rc1 make image
```

The installer validates every overlay file before writing anything, checks the
exact LibreELEC revision and refuses a dirty checkout. The source manifest
records both repository paths and their LibreELEC destinations. Do not apply
this on top of another community build or reuse an older overlay silently.

Patches are applied by LibreELEC's native package pipeline, in filename order.
The two complete package-recipe overrides come from the pinned upstream files;
their changes are documented in [CHANGES.md](CHANGES.md). No component is
downloaded from an unpinned development branch by this overlay.

Build outputs are under `target/`: `.img.gz` for installation and `.tar` for
updates. The build also emits license texts and checksums. Never put a personal
`/storage` tree, media library, SSH key or test recording into an image.

## Verify source patches without a full build

```sh
python3 intel-dv-libreelec/check-patches.py \
  --source-cache LibreELEC-DV/sources --output /path/to/new-check-directory
```

This checks archive hashes, extracts fresh component trees and applies the
additional patches with zero fuzz. It is not a compiler or HDMI test.

## Distribution

Keep images out of Git. Attach the image, update archive and matching upstream
source bundle to the same release. Group the build receipt and notices inside
the source bundle rather than publishing separate download assets. The
source bundle must include build scripts, the pinned upstream tree, the source
archives and patches actually used, plus notices. Merely linking to an upstream
website is not our binary-release source-delivery plan.

Do not label a newly rebuilt image as physically tested merely because its
source predecessor passed HDMI tests. Record artifact identity and validation
scope in its receipt. See [LICENSING.md](LICENSING.md).
