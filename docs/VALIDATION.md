# Validation

## R0.2.1a-opt1

Software checks and real HDMI playback are separate evidence. The qualified
image was installed on i7-11390H with a modern LG Standard-DV display. The public
image was then repackaged under the R0.2.1a-opt1 name; kernel and playback
binaries are unchanged. This naming-only package was not separately replayed.

| Area | Result |
| --- | --- |
| Software regression checks | 21 C/C++ checks with ASan/UBSan and 33 Python checks passed in the internal qualification suite. |
| HDMI packets and capabilities | Actual kernel packet pack/unpack checks and malformed-input tests passed; modern and legacy DV active-state guards checked. |
| Source reproducibility | All 29 patches apply without fuzz; 93 modified kernel/Kodi source files match the build after reconstructing stock LibreELEC plus this overlay. |
| Playback transitions | 19 software-state scenarios passed across SDR, HDR10, HLG, P5, P7 FEL, P8.1, P8.4 and P10, including direct file changes, pause/resume, seeks and return to SDR. Kodi did not restart. |
| Continuous playback | Two-minute P8.1 playback at 4K23.976 completed with no reported renderer presentation or stage failures; returned to the 4K60 SDR interface. These counters are not a measurement of every dropped/skipped frame. |
| Diagnostics | Automatic state changes and bounded summaries recorded; filtering, continuation through a busy kernel log and diagnostics-disabled transactions checked. |
| Packaging | Image dependency audit and complete-source inventory checks passed. Kernel and playback binaries match the qualified image; release identification files changed for the public name. |
| Native behavior | Original menus retained. SDR/HDR10/HLG sources use Kodi's native path, with HDMI-DV disabled. |

The internal build/test harnesses and lab reports are not distributed in this
repository. Reproducible image build scripts, pinned sources, patches, licenses
and corresponding sources remain available.

## Rendering evidence retained

The unchanged optimized renderer was previously checked against its separate
full-precision path on twelve deterministic 4K cases and six real-frame sources.
Lanczos sampling checks compared 288 FP32 cases, including fallback conditions.
FEL seek checks compared 2,876 reference enhancement pictures and repeated seeks;
successful physical runs verified picture order and continued playback.

CM2.9/CM4 transport and the tested profile paths remain unchanged by this release.
Startup and user-interaction disturbances are evaluated separately from steady
playback. A DV logo alone never proves correct image reconstruction or metadata.

## Limits

- No physical v0/v1 sink or the reported 12400T/matrix route was available for
  this qualification. Their capability/signaling code is tested in software,
  not certified across all receivers, switches or televisions.
- No new N100 performance measurement was made.
- P7 MEL and P8.2 do not have dedicated physical LibreELEC qualification here.
  P9 is not supported by the pinned H.264 metadata path; P10 evidence does not
  qualify every compatibility variant or refresh rate.
- Software display-state checks are not an external HDMI capture, visual
  certification or a guarantee of zero dropped frames.
- Diagnostics are deliberately bounded. Unavailable or truncated kernel
  evidence is reported where detectable; this is not a full system journal.

## Source checks

On Linux with Python 3.12 or newer:

```sh
python3 tools/verify.py
python3 tools/check-patches.py --source-cache /path/to/LibreELEC-DV/sources \
  --output /path/to/new-source-check
```

These checks verify source inputs, license records and patch application, not
physical HDMI playback. See [BUILD.md](BUILD.md) to reproduce the image.
