# Intel DV for LibreELEC 0.1.0-rc1

Native Dolby Vision in Kodi, automatically selected for compatible Intel HDMI
systems. Includes profile-7 FEL reconstruction, synchronized CM2.9/CM4 metadata
and the normal Kodi player interface. No external player or activation menu.

Based on LibreELEC 13.0-devel, Kodi 22 Beta 2, Linux 7.2.6, FFmpeg 9.0 and the
pinned libplacebo 7.372.0 revision. The hardware reference for this LE port is
i7-11390H / Iris Xe; other eligible Intel models require their own performance
and HDMI-route checks. Read the profile matrix before installing.

## Assets

| Asset | Use |
| --- | --- |
| `LibreELEC-Generic.x86_64-13.0-intel-dv-0.1.0-rc1.img.gz` | Write to a spare installation medium. |
| Matching `.tar` | Standard LibreELEC manual update archive. |
| `intel-dv-libreelec-0.1.0-rc1-source.zip` | Repository, patches, version pins, notices and tests. |
| `corresponding-sources.tar` parts | Exact pinned upstream/build-source material accompanying the binary image. Reassemble in filename order before extraction. |
| `SHA256SUMS` and `build-receipt.json` | Verify the downloaded artifacts and their validation scope. |

This is an independent experimental community build, not an official LibreELEC,
Kodi, Dolby or Intel release. Back up before updating. Source assets and their
licenses are part of the release, not optional substitutes for the image.
