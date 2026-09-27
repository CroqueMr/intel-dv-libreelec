# Playback diagnostics

Normal playback keeps detailed DV tracing **off**. Important rendering and HDMI
failures remain visible, with repeated failures rate-limited. No per-frame GPU
readback, timing query, metadata dump or network upload is added.

## Enable / disable detail

Use Kodi's existing **Settings > System > Logging > Enable debug logging**.
Turn it on **before starting the problem video**; reproduce once and turn it off
again. No reboot, reinstallation or new DV settings menu is needed. Disabling it
stops the detailed messages, not the essential failure summaries. Restart playback
after enabling it to capture initialization and the first prepared frame.

The added messages use the `DVBridge:` prefix. They identify stream selection,
GL capabilities, base/enhancement-layer rendering, FEL/CM4 presence, transport
path, captured output properties, atomic rejection stages and display restoration.
They do not claim that an accepted atomic commit proves correct TV rendering.

Ordinary Kodi debug logging is sufficient for these additions. Component-specific
windowing logging can be much noisier and is not required for a first report.

## Collect the evidence

### Native on-screen playback information

During playback, **O** opens Kodi's player-process information; **Ctrl+Shift+O**
opens its debug counters, and **Alt+O** opens video-debug information. **I** is
the ordinary media-information action, not the decoder or dropped-frame view.
Loose test files may have little library information to display.

The native HDR detail reports the source profile and adds FEL, CM2.9/CM4 and
HDMI DV only from the successfully presented DV path. The TV badge alone does
not verify enhancement-layer reconstruction. Stopping playback clears the
active output status; the selected file may retain its source-profile label.

### Log collection

Over SSH, run:

```sh
dv-diagnostics collect
```

It prints the location of a local `.tar.gz` under `/storage`. Retrieve it using
your usual file-transfer method. It contains current/previous Kodi logs, the boot's
kernel log, build identity, connector status/modes, raw EDID and the DV enable
parameter when readable. It does not restart Kodi, change settings or upload
anything. The report directory is also retained.

**Review before sharing:** Kodi itself may log media paths, server addresses,
account details or stream URLs. EDID can contain display identifiers. This is not
an automatic anonymizer; redact sensitive fields before posting publicly.

## Kernel DV messages in kodi.log

Starting with R0.1.0-rc3-opt1, an output rejection schedules a bounded background
read of `/dev/kmsg`. Recent kernel-origin `DVBridge:` records are copied through
Kodi's own logger with the prefix **`DVBridge kernel:`**, original sequence number
and monotonic boot timestamp. For these HDMI rejections, share `kodi.log` first.
The native Kodi debug switch still enables the additional requested-property and
renderer details; essential kernel rejection reasons do not require it.

The Intel driver's `DVBridge: link rejected` message records Standard-DV EDID
support, native HDMI/LSPCON, display generation, range, bit depth and mode.
Those flags describe the rejected configuration, not necessarily the TV's
intrinsic abilities. No accepted configuration or correct TV image is inferred
from their presence.

This is not a copy of the entire kernel journal. Only DV records from the last
15 seconds are eligible; repeats are deduplicated. Collection happens off the
render thread, only after a rate-limited failure, with nonblocking reads and
bounded work/output. It does not consume or clear other kernel readers. If
access is denied, records have expired/been overwritten, or collection is
limited, `dv-diagnostics collect` remains available for the full boot journal.

### Disable or remove the bridge

Set **`DVBRIDGE_KERNEL_LOG=0`** in Kodi's service environment and restart Kodi to
disable kernel copying. For example, the systemd service override's `[Service]`
section can contain `Environment=DVBRIDGE_KERNEL_LOG=0`. Removing that override
restores the default on the next start. This does not disable Dolby Vision or
change normal Kodi diagnostics.

The implementation is isolated in **`kodi-9992-kernel-log.patch`**. A downstream
build can omit it (and its overlay-manifest/index entries) without removing the
renderer or changing HDMI policy. No kernel change is needed for this addition.

## Scope

This revision adds diagnostics only. It does **not** fix unsupported HDMI routes,
relax eligibility, alter shaders/metadata, or introduce an HDR fallback. The known
repeated rejection is now observable without flooding Kodi's log, but retry
behavior itself is unchanged. Kernel messages use the existing DRM rate limiter;
Kodi failure summaries occur at most once every five seconds per failing object;
each resulting kernel collection copies at most 16 matching records.

The initial diagnostics are isolated in `kodi-9991-diagnostics.patch` and
`linux-9902-dv-diagnostics.patch`. The new `kodi-9992-kernel-log.patch` depends on
the Kodi diagnostic hook: omit it as well if removing `kodi-9991` downstream.
Normal users can turn off Kodi debug detail and separately disable kernel copying
as described above. Playback decisions never depend on the diagnostic counters
or on whether logging is enabled.
