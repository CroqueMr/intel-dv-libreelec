# Playback diagnostics

**R0.2.1a-opt1 records compact DV diagnostics automatically in `kodi.log`.**
There is no diagnostic menu to enable and no need to turn on Kodi's global
debug mode before reproducing a problem. No upload is performed.

Leave global debug logging off for normal playback measurements. Its native
overlay and verbose component logs can change rendering workload; closing the
player OSD does not necessarily remove that overlay. This build does not change
Kodi's debug controls, overlay behavior or logging of unrelated components.

## What is recorded

- Stream profile, compatibility ID and native-DV eligibility for each decoder
  candidate. A selection probe is explicitly distinguished from active output.
- Accepted signal changes: connector/CRTC, DV, HDR metadata blob, colorspace,
  RGB range, timing and requested maximum bpc. Maximum bpc is not a measured
  HDMI bit depth; an accepted commit is not a wire capture.
- Renderer capabilities and the first prepared frame, including FEL/CM4 presence.
- Coarse direct/composed/presented counts, approximately every 30 seconds and
  on reset/closure when new work exists. These are renderer counters, not a
  replacement for Kodi's dropped-frame counters or an HDMI capture.
- First output failure and bounded summaries: stage, error, connector, CRTC,
  timing and retry interval. The first failure per sink identity includes
  evaluated sink capabilities, up to 1024 raw EDID bytes and at most 48 relevant
  requested DRM properties.
- Error-only graphics-backend details, bounded without shader/debug dumps.
- Recent kernel-origin DV rejection reasons and selected Intel GPU/display faults,
  copied in a background job with
  original sequence and boot timestamp. The render thread never reads `/dev/kmsg`.
- Recovery summaries, without a new log burst on every success/failure alternation.

The prefixes are `DVBridge stream`, `DVBridge renderer`, `DVBridge setup`,
`DVBridge output`, `DVBridge signal`, `DVBridge graphics`, `DVBridge sink` and
`DVBridge kernel`. A successful transaction
does not prove that the TV displays the correct pixels.

## Bounds and overhead

Each failure limiter permits at most four first/change reports per 30-second
window. An unchanged failure is summarized no more than once every 30 seconds.
Recoveries are separately limited to one report per 30 seconds. The kernel
allows one DV link rejection message per connector per 30 seconds and four
scanout-guard messages per 30 seconds across CRTCs. Accepted signal changes have
an eight-message budget per 30 seconds, plus one suppression notice. These budgets
are independent of playback/retry decisions.

Kernel collection has at most one queued/running job. Each pass uses nonblocking
reads and a 50 ms / 4096-record ceiling. Up to three batches, separated by short
yields, can advance a busy cursor; all batches share eight copied messages and
two truncation/overrun notices per 30 seconds. Only kernel-origin DV records or
allowlisted warning/error Intel display incidents at most 60 seconds old are eligible; repeated sequence
numbers and recent repeated content are rejected. It does not consume or clear
other kernel readers, and there is no kernel polling during healthy playback.
Native atomic failures also trigger the bounded collector without changing
Kodi's original fallback behavior. Unrelated kernel messages are excluded.
No GPU readback, extra GPU synchronization or timing query is added.

This is not a full copy of the system journal. Permission failures, ring overruns,
expired records and bounded collection can leave evidence unavailable. The
optional `dv-diagnostics collect` command still collects a local full report;
it is not required to activate the automatic Kodi diagnostics.

Scanout rejection masks use these bit positions (bit 0 first): `crtc` = color
processing, dithering, VRR, DSC, scaler, plane mask; `primary-layout` = route or
visibility, pixel format, allocation size, source rectangle, destination rectangle,
rotation, alpha; `plane-processing` = color processing, scaler, forced black,
linked plane. `primary-missing` means no plane or framebuffer. These diagnostics
explain existing guards; they do not relax or add transport restrictions.

## Sharing a report

Share `kodi.log` first. Include the release version, CPU, HDMI route, TV/model,
source profile, and whether menus, subtitles or a debug overlay were visible.

**Review before sharing:** native Kodi logs can contain media paths, server
addresses or stream URLs. Raw EDID can contain display identifiers. This is not
an automatic anonymizer.

For a larger local report over SSH:

```sh
dv-diagnostics collect
```

The command prints the report location under `/storage`. It changes no playback
settings, starts no network upload and restarts no service.

## Developer removal boundary

Set `DVBRIDGE_DIAGNOSTICS=0` in Kodi's service environment and restart Kodi to
disable the added Kodi supplement, including kernel copying. It is enabled by
default; this switch is for developers, not a requirement for users reporting bugs.
Native Kodi and kernel logs are unaffected.

The old Kodi 9991/9992 diagnostic patches and Linux 9902 diagnostics were removed.
The replacement starts from the functional source baseline, not from those old
logging changes. Omit `kodi-9995-diagnostics.patch` and
`linux-9903-diagnostics.patch` (plus their manifest/index entries) to remove the
new diagnostic implementation. Compatibility/retry patches do not depend on it.

## Native playback information

**O** opens Kodi's player-process information; **Ctrl+Shift+O** opens its debug
counters, and **Alt+O** opens video-debug information. **I** remains the normal
media-information action; loose test files may have no rich library metadata.
FEL/CM4 and HDMI DV in the native HDR detail describe successfully presented DV
output. Stopping playback clears that active output status.
