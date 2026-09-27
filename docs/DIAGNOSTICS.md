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

For an HDMI rejection, include **both `kodi.log` and `kernel.log`**. Kodi records
the failed operation and errno; the Intel driver's `DVBridge: link rejected`
message records the evaluated policy flags, including Standard-DV EDID support,
native HDMI/LSPCON, display generation, range, bit depth and mode. Those flags
describe the rejected configuration, not necessarily the TV's intrinsic abilities.

## Scope

This revision adds diagnostics only. It does **not** fix unsupported HDMI routes,
relax eligibility, alter shaders/metadata, or introduce an HDR fallback. The known
repeated rejection is now observable without flooding Kodi's log, but retry
behavior itself is unchanged. Kernel messages use the existing DRM rate limiter;
Kodi reports at most once every five seconds per failing diagnostic object.

The changes are isolated in `kodi-9991-diagnostics.patch` and
`linux-9902-dv-diagnostics.patch` for review or removal at build time; normal users
should simply turn off Kodi debug logging. Runtime decisions never depend on the
diagnostic counters or on whether logging is enabled.
