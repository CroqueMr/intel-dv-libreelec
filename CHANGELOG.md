# Changelog

## Unreleased: Kodi 22.0 RC1

- **Kodi 22.0 RC1:** the Kodi patches are rebased from 22.0 Beta 2 (`b7afba24`) to 22.0 RC1 (`28ea2eac`) and apply with no fuzz. Two needed real changes:
  - *Profile 7 FEL seek:* RC1 skips seeks past the end of a file. The FEL preroll now runs only when a seek actually happens, so a seek past the end still ends playback quickly instead of probing the file for an enhancement-layer anchor.
  - *Display reset while DV is presenting:* the DV and HDR10 paths now send a pending display reset (`kodi-9999`). RC1 keeps the current frame across a display reset, so after a mid-playback mode change the bridge started presenting again before the reset was sent, and video and audio could stay paused.
- **LibreELEC `9902-headers-only.patch`:** carries LibreELEC master's refreshed copy. The pinned copy fuzzes onto RC1 and breaks the Kodi headers install that binary add-ons build against.
- **Unchanged:** FFmpeg 9.0 still meets RC1's minimum for system FFmpeg. The audio sink retry (`kodi-9998`) is still needed; RC1 changes when the error state retries, not what the retry does.

## R0.3.0

- Native Kodi Player settings: Standard Dolby Vision (TV-Led), HDR10 conversion, or vanilla Kodi playback.
- HDR10 conversion with FEL reconstruction and L1-guided tone mapping to a source-derived mastering target.
- Optional Player information panel with source format, bit depth, metadata and GPU render usage.
- Lightweight automatic diagnostics for frame drops, skips and playback transitions.

Standard DV remains the default. The current HDR10 framebuffer is 10-bit;
HDR10 conversion does not reproduce
proprietary target-display CM4 mapping. See [output modes](docs/OUTPUT-MODES.md).

## R0.2.1a-opt1

- **Lighter automatic diagnostics:** DV and relevant kernel details in the normal Kodi log, with bounded summaries instead of repeated output.
- **Standard-DV compatibility:** aligned v0/v1/v2 display checks and matching HDMI signaling.
- **HDMI recovery:** tolerate transient failures and pace persistent retries without permanently excluding a display.

FEL fixes and opt1 optimizations are retained. No new rendering/OSD change.
New HDMI routes remain subject to physical validation.

## R0.2.1-opt1

- **Improved diagnostics:** relevant kernel Dolby Vision errors are now included in `kodi.log`, making playback issues easier to investigate.
- **More reliable Profile 7 FEL playback:** fixes picture-order issues and freezes after seeking in affected files, while preserving the requested playback position.

## R0.1.0-rc2-opt1

- **Enhanced diagnostic logging** to make playback issues easier to investigate.

## 0.1.0-rc1-opt1

- Avoid unnecessary reconstruction outside the Dolby Vision active picture,
  while preserving the exact video and metadata transport bytes.
- Extend the GPU regression check to cover 320-pixel top/bottom active-area masks.
- Avoid redundant bilinear tap interpolation in eligible libplacebo Lanczos3
  passes, including full-frame FEL reconstruction, without changing the filter.
- Check exact FP32 filter output against the original linear-sampling path,
  including shifted/cropped input and the fallback cases.
- No change to decoding, HDMI HDR/SDR selection, metadata or kernel behavior.

## Repository maintenance

- Group scripts in `tools/`, manifests in `config/` and release notes in `docs/releases/`.
- Allow normal documentation edits without regenerating whole-repository hashes.
- Retain checks of build inputs, licenses, inherited code and accidental private data.
- No changes to the DV patches, release image or update archive.

## 0.1.0-rc1

- Automatic native Dolby Vision playback through Kodi's normal player.
- Full enhancement-layer reconstruction for compatible profile-7 FEL streams.
- CM2.9/CM4 metadata synchronized with the presented video frame.
- Exact GPU transport rendering, with normal subtitles and player controls.
- Native HDMI capability detection and safe display-state restoration.
- Original LibreELEC settings and Kodi skin; no additional activation interface.
- Pinned source versions, documented patches and reproducible checks.

See the README for profile/hardware boundaries and docs/VALIDATION.md for the
scope of successful tests. This is an independent community release candidate.
