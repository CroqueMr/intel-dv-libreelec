# Changelog

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
