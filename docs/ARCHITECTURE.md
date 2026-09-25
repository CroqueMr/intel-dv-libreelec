# Architecture

```text
Kodi VideoPlayer → FFmpeg / VAAPI → owned frame metadata + paired BL/EL surfaces
                → shared DV renderer / libplacebo → RGB8 HDMI transport
                → Kodi GBM atomic presentation → Intel DRM/KMS → Standard-DV TV
```

## Responsibilities

- **FFmpeg** parses source metadata. The patch preserves extension bytes needed
  for CM4 and recognizes the AV1 DV container tag. It does not implement the
  complete HDMI transport or replace the television's display management.
- **Shared renderer** owns metadata, checks its bounds, reconstructs video with
  libplacebo, pairs FEL surfaces by timestamp and serializes the frame's display
  metadata. Reconstruction uses full precision before final transport packing.
- **Kodi** keeps its normal decoding, buffering, refresh-rate selection,
  controls and GUI. The DV adapter is selected only for eligible source,
  decoder, display and transport combinations. Its normal stream-information
  field reports the active DV output, FEL and CM generation after presentation.
- **Intel display driver** advertises the connector control, validates EDID and
  HDMI topology, constructs signaling and rejects display processing that could
  alter transport bytes. The existing i915/xe display code is reused.

The RGB8 framebuffer is a transport container, **not SDR output or an 8-bit
reduction of the reconstructed image**. Scaling, GUI composition and active-area
handling happen before transport packing. The packed surface must not undergo
ordinary color correction, dithering or scaling afterwards.

## Safety and lifecycle

Metadata state is prepared separately from presentation. Failed atomic commits
cannot advance it as if a frame had been displayed. Seek/reset discards stale
layer pairing and metadata. The adapter captures and restores display state;
ending DV playback returns control to Kodi's normal path.

The optimized full-screen path fuses reconstruction and packing only when the
GPU's fragment subgroup capabilities and frame geometry permit exact output.
GUI/subtitle composition, unsupported capabilities and shader failure retain
the full-precision composition path. Overlays are never omitted for speed.

Ordinary SDR/HDR playback and software metadata probes do not enter the DV
renderer. This does not remove the independent Intel HDR10 link-precision
correction included in the kernel patches; see the component change index.

## Deliberately unchanged

No external mpv process, launch wrapper, custom Kodi skin, settings dialog,
private activation service, patched Mesa or modified Intel Media Driver.
LibreELEC's original settings addon and Kodi service remain upstream files.

The low-level `enable_dv_lab` parameter and `DVBRIDGE_DV_STANDARD_LAB` property
retain their existing names because they are the kernel/userspace interface.
They are enabled by policy in this dedicated image and are not an end-user
activation menu. Renaming an interface solely for appearance would break
compatibility with existing clients and diagnostic tools.
