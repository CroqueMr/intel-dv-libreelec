# Patch guide

Apply each component's patches in filename order. Exact pinned versions are in
[`docs/VERSIONS.md`](../docs/VERSIONS.md); the complete file-level index is in
[`config/patch-index.json`](../config/patch-index.json). This guide highlights
the changes prepared for R0.2.1a-opt1.

| Component | Patch count |
| --- | ---: |
| Linux / Intel display | 13 |
| FFmpeg | 3 |
| libplacebo | 9 |
| Kodi / shared DV renderer | 4 |
| **Total** | **29** |

The two LibreELEC recipe overrides are separate build inputs, not patches.
The previous three diagnostic patches are removed, not patched over. Four
focused patches replace them: two for compatibility/recovery, two for logging.

## Linux 9902 and Kodi 9994 — HDMI compatibility and recovery

**Purpose:** agree on sink eligibility and recover transient output failures.

The identical C-compatible EDID parser validates complete block checksums and
bounds, Standard-DV v0/v1/v2 interfaces and the legacy VSIF requirement. The
driver uses HDMI-OUI legacy signaling where needed; modern signaling is retained.
Both packet forms use the same scanout-safety and transition guards.
LLDV-only, malformed and unknown formats remain ineligible. No EDID is rewritten.

Kodi allows the first two failed attempts to retry immediately, then spaces
attempts by 250 ms during the first three seconds and one second thereafter.
It does not sleep on the GUI thread, permanently blacklist a connector or
introduce an automatic HDR fallback. Successful output, modesets and detected
connector/EDID/status changes reset recovery state. Restore requests always run.

These changes do not replace Kodi's general hotplug/mode-selection behavior.
An HDMI matrix can still supply a misleading EDID or modify the transmitted
signal; software validation alone cannot qualify that physical route.

## Linux 9903 and Kodi 9995 — lightweight automatic diagnostics

**Purpose:** preserve useful failure evidence without global debug logging.

The Kodi patch records startup facts, bounded failure/recovery summaries and
coarse rendering counts at normal log level. It schedules nonblocking background
kernel collection only after a reported output failure, including native atomic
failures. Successful signal changes are recorded after the accepted commit.
The driver limits link and scanout rejection messages. There is no per-frame IO
or additional GPU query.

| Source area | Change |
| --- | --- |
| `utils/DVBridgeDiagnosticState.h` | Bound failures and recoveries independently from output policy. |
| `utils/DVBridgeKernelLog.h` | Filter DV causes and allowlisted Intel display faults by origin, age and repeated content. |
| `windowing/gbm/drm/DVBridgeKernelLogReader.h` | Bound background work and continuation; report truncation and ring overruns explicitly. |
| `windowing/gbm/drm/DRMAtomic.cpp` | Record accepted signal changes and collect failure evidence without blocking the renderer. |
| `VideoRenderers/DVBridgeGLES.cpp` | Forward bounded graphics errors without verbose shader logging. |
| `intel_display.c` | Explain scanout rejections with stage/reason masks; preserve the existing restrictions. |

Set `DVBRIDGE_DIAGNOSTICS=0` in Kodi's service environment and restart Kodi to
disable the added Kodi supplement. Downstream builds can omit Kodi 9995 and
Linux 9903 with their manifest/index entries without removing native DV or
the independent compatibility/recovery changes.
See [`docs/DIAGNOSTICS.md`](../docs/DIAGNOSTICS.md) for collection and privacy.

## Kodi 9993 — FEL picture pairing and seek recovery

**Purpose:** keep base and enhancement pictures aligned when their coding order
or random-access boundaries differ, including after a seek.

| Changed file | High-level responsibility |
| --- | --- |
| `tools/dvbridge/dvbridge_fel.c` | Parse HEVC picture order using FFmpeg, map matching timestamps before enhancement decoding, bound queues and resynchronize after reset. |
| `tools/dvbridge/dvbridge_fel.h` | Distinguish paired pictures, pending input, discardable preroll and failure/EOF. |
| `tools/dvbridge/dvbridge_fel_seek.h` | Probe compressed headers for an eligible preroll entry point; bounded by time, bytes and packet count, without decoding pixels. |
| `DVDDemuxers/DVDDemuxFFmpeg.cpp` | Use that entry point only for eligible native dual-layer DV and preserve Kodi's requested start time. |
| `DVDDemuxers/CMakeLists.txt` | Expose the helper include directory only when building the DV bridge. |
| `DVDCodecs/Video/DVDVideoCodecFFmpeg.cpp` | Discard pre-anchor pictures through the existing player queue and diagnose exhausted enhancement input. |

The recovery anchor is a common layer keyframe identity, or an enhancement IDR
with a base layer declared non-reordered. No nearest-picture substitution is
allowed. The probe scans progressively earlier windows, with a three-second
deadline, a 256 MiB cumulative read cap and 12,000 packets per window. The input
reader retains its native interrupt handling. Decoder preroll is also bounded.
These bounds are safeguards, not a promise that malformed or unusual streams
will always recover.

No new CPU pixel processing, shader, metadata serialization or HDMI signaling
is introduced. HDR/SDR playback outside native DV retains the original route.
The fix is not a general GPU-performance optimization or new profile support.

Internal checks cover ownership, order, reset, preroll, error bounds,
entry-point selection, malformed headers, absent anchors and the reordered-base
guard. Real-file comparisons and physical-player
results are described in [`docs/VALIDATION.md`](../docs/VALIDATION.md).

All patches retain their source notices. Test harnesses and development
captures are not installed in the playback image.
