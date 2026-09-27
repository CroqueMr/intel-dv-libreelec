# Changelog

## 0.1.0-rc1-opt1-diag1

- Add optional DV startup/render/output diagnostics using Kodi's existing debug switch.
- Explain Intel HDMI policy rejection with evaluated flags in the kernel log.
- Rate-limit repeated DV errors and add a local `dv-diagnostics collect` command.
- Retain Opt1 optimizations; no change to rendering, metadata or HDMI eligibility.
- Diagnostic revision, not a fix for unsupported HDMI routes or repeated retry behavior.

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
