# Exact versions

These are the release inputs, not a promise to follow moving upstream HEADs.
Build all patched components together: the FFmpeg metadata extension is an ABI change.

| Component | Version | Pinned revision | Modified here |
| --- | --- | --- | --- |
| LibreELEC | 13.0-devel | `3de4708704041ead8ae1531092efb7ea5da9d355` | Yes |
| Kodi | 22.0 Beta 2 | `b7afba240133a570145466cfaf6a6825f84c6ad1` | Yes |
| Linux | 7.2.6 | `release archive; hash checked by recipe` | Yes |
| FFmpeg | 9.0 | `release archive; hash checked by recipe` | Yes |
| libplacebo | 7.372.0 | `e2972fdd09adacd383656738d7d280f0cd84a761` | Yes |
| Mesa | 26.2.3 | `release archive; hash checked by recipe` | No |
| Intel Media Driver | 26.3.5 | `release archive; hash checked by recipe` | No |
| libva | 2.24.1 | `release archive; hash checked by recipe` | No |
| LibreELEC Settings | Pinned source | `9cf5f9868c48878a31ee9f97d290af889dd1c879` | No |

The checksummed upstream archives for the four patched components are listed
in `check-patches.py`. LibreELEC pins the rest of the distribution, including
its compiler, graphics stack, bootloader, firmware and settings addon.

The recipe/patch installation map is `dvbridge-overlay.json`; the complete
source-repository byte inventory is `SOURCE-FILES.sha256`. A binary release
also carries its own image receipt and corresponding-source archive inventory.
