# Patch guide

Apply each component's patches in filename order. Exact pinned versions are in
[`docs/VERSIONS.md`](../docs/VERSIONS.md); the complete file-level index is in
[`config/patch-index.json`](../config/patch-index.json). This guide highlights
the two additions prepared for R0.1.0-rc3-opt1.

## Kodi 9992 — kernel diagnostic bridge

**Purpose:** make relevant HDMI/DV rejection reasons available in `kodi.log`.

The patch schedules a bounded, nonblocking background read after a rate-limited
output failure. It copies recent kernel-origin DV records, preserves their
sequence/timestamp, suppresses duplicates and reports unavailable access. It
does not copy the entire kernel journal, run every frame, change playback
decisions or upload logs.

| Source area | Change |
| --- | --- |
| `utils/DVBridgeKernelLog.h` | Filter eligible records by origin, age and identity. |
| `windowing/gbm/drm/DVBridgeKernelLogReader.h` | Read records in the background with bounded work and ownership. |
| `windowing/gbm/drm/DRMAtomic.cpp` | Schedule collection after output rejection without blocking the renderer. |

Set `DVBRIDGE_KERNEL_LOG=0` in Kodi's service environment and restart Kodi to
disable collection. Downstream builds can omit 9992 and its manifest/index
entries without removing native DV. It depends on the diagnostic hook in 9991.
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

`tests/fel_queue.c` covers ownership, order, reset, preroll and error bounds.
`tests/fel_seek.c` covers entry-point selection, malformed headers, absent
anchors and the reordered-base guard. Real-file comparisons and physical-player
results are described in [`docs/VALIDATION.md`](../docs/VALIDATION.md).

Both patches retain their source notices. Test harnesses and development
captures are not installed in the playback image.
