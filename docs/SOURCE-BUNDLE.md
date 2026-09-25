# Corresponding build sources

This source bundle accompanies Intel DV for LibreELEC 0.1.0-rc1. It includes:

- The exact pinned upstream LibreELEC Git tree, with its build scripts, package
  recipes, upstream patches and notices. The snapshot is intentionally shallow.
- The additional Intel DV repository, patches, notices, tests and recipe overrides.
- The verified source archive cache used by the build, including build-time
  dependencies and upstream firmware/driver distributions. Unused cached dependencies
  may be present; this is not a minimal software bill of materials.
- The generated Linux kernel configuration and source-content checksums.

The cache contains upstream firmware and the original NVIDIA driver archive
used by the stock Generic build; their individual redistribution terms remain
applicable. The NVIDIA agreement is also available under `third-party-notices/`.
This does not add NVIDIA support to the Intel DV implementation.
The bundle does not contain a Dolby SDK, personal
configuration, media or the build host's compiled toolchain.

## Reassemble and verify

Download all `corresponding-sources.tar.part-*` files, `SHA256SUMS` and
`corresponding-sources.tar.sha256` from the same release. In an empty directory:

```sh
sha256sum --check SHA256SUMS
cat corresponding-sources.tar.part-* > corresponding-sources.tar
sha256sum --check corresponding-sources.tar.sha256
tar -xf corresponding-sources.tar
cd corresponding-sources
sha256sum --check BUNDLE-SHA256SUMS
```

The release-wide checksum file also lists the image and other assets. Download
them too, or verify only the lines corresponding to the files you downloaded.

## Reconstruct the source tree

Use a Linux filesystem and install the normal LibreELEC host prerequisites:

```sh
git clone LibreELEC-upstream.git LibreELEC-DV
git -C LibreELEC-DV remote set-url origin https://github.com/LibreELEC/LibreELEC.tv.git
python3 intel-dv-libreelec/verify.py
python3 intel-dv-libreelec/apply-overlay.py LibreELEC-DV
cp -a sources LibreELEC-DV/sources
cd LibreELEC-DV
PROJECT=Generic ARCH=x86_64 OFFICIAL=no \
  BUILDER_NAME=Intel-DV CUSTOM_VERSION=13.0-intel-dv-0.1.0-rc1 \
  CUSTOM_IMAGE_NAME=LibreELEC-Generic.x86_64-13.0-intel-dv-0.1.0-rc1 make image
```

The source inputs are fixed; bit-for-bit identical output across different build
hosts is not asserted. Host prerequisites are not bundled. Preserve this source
bundle and notices when redistributing the accompanying binary image.

## Maintainer export

After a successful image build, from the Intel DV repository:

```sh
python3 export-sources.py --tree /path/to/LibreELEC-DV \
  --output /path/to/new-output/corresponding-sources
```

This fails on source-hash drift and refuses an existing output directory. It
does not package private logs, runtime state or media, and never publishes files.
