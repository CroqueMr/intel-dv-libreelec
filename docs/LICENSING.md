# Licensing and redistribution

This repository is a collection of patches and build tooling, **not a blanket
relicensing of LibreELEC or its dependencies**. Original copyright and license
notices remain in the resulting source files.

| Material | Applicable terms |
| --- | --- |
| Repository documentation, build/check tooling and original test harness | MIT, except files retaining another explicit notice. |
| Linux as a combined kernel | GPL-2.0-only; Intel display/HDMI files and new policy helpers retain their MIT notices where applicable. |
| FFmpeg source modifications | LGPL-2.1-or-later for the affected source files; the pinned LibreELEC FFmpeg recipe builds with GPL and version3 enabled and declares GPL-3.0-or-later. |
| libplacebo changes | LGPL-2.1-or-later. |
| Existing Kodi integration files | Their original notices, generally GPL-2.0-or-later. |
| Shared transport/rendering helpers and native DV adapter | GPL-3.0-or-later, as marked in their source headers. |
| Combined DV-enabled Kodi build | GPL-3.0-or-later, because it includes those helpers. |
| Other image packages and firmware | Their own upstream terms, recorded by the pinned LibreELEC recipes and retained in the matching source distribution. |

Full primary license texts and retained third-party notices are under
`LICENSES/`. Their canonical hashes are checked by `verify.py`. The existing
Kodi functional patch already includes its combined-build notice and GPLv3
text; no additional licensing-only patch is added by this release preparation.

See [ORIGIN.md](ORIGIN.md) for source credits and derivation. Inherited notices
must not be removed when copying, splitting or renaming the patches. A name
change does not change the license of inherited code.

## Source and binary releases

The source ZIP contains our patch set, exact recipes, build instructions and
tests. An image contains many more components; its matching source delivery
must therefore also include the pinned LibreELEC source tree, the exact source
archives used, relevant build scripts/configuration and package notices.

Release images and corresponding source assets together, with cryptographic
checksums and a build receipt. Keep them available together for recipients.
Do not call a patch-only ZIP the complete corresponding source of an entire
LibreELEC image. Check firmware redistribution terms separately from GPL source
obligations. Do not include DRM addons or media in a clean image.

No proprietary Dolby
SDK, confidential specification, content-decryption key or media is included in
the source repository. No official certification or endorsement is claimed.

References: [kernel licensing](https://docs.kernel.org/process/license-rules.html),
[FFmpeg licensing](https://ffmpeg.org/legal.html),
[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).
