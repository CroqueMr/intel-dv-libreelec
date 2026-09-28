# Validation

## R0.3.0

The final image was installed on i7-11390H. Native Kodi Player > Videos exposes
both preferences at Basic level; all values passed read/write checks. The
LibreELEC settings addon contains no DV helper or custom DV settings. Standard
DV Profile 7 FEL and Avatar Profile 8 playback supplied the release screenshots.
The final 31-patch series applies to fresh pinned sources with zero fuzz.

The HDR10 conversion adds L1-guided libplacebo mapping. Sanitized software
tests cover metadata-driven output changes, unchanged native DV, FEL reference
agreement, target selection and output quantization. Kodi compilation passes.
Short real HDMI playback checks pass for Standard DV FEL, converted FEL, HDR10
and SDR. Calibrated visual fidelity and sustained hardware performance of this
new mapping have not been qualified. Earlier playback results below concern
the previous conversion path, not the new mapping.

The playback qualification below was run on the complete `0.3.0-dev4` image on
the i7-11390H test system.
No temporary player or skin overlay is required.

| Area | Evidence |
| --- | --- |
| Build and sources | Complete Linux/Kodi/LibreELEC image build passed. Source and canonical-license checks passed. The final release contains 31 patches; the LibreELEC Settings modification was removed. |
| Pixel preservation | Sanitized renderer tests passed for full/limited range and 1000, 2000, 4000 and 10000 nit PQ values without a 1000-nit mastering-metadata cap. |
| Conversion playback | P5, P8.1, P8.4, P10.1 and two P7 FEL samples passed HDMI signaling and presentation checks, including repeated Woman-at-80s seeks. |
| Output depth | The conversion pipe reports 30 bpp at 4K25 and 4K60. The 60 Hz case uses a retimed stress sample and the driver's validated deep-color format selection; it is not a full 60 fps profile-coverage claim. |
| Native behavior | SDR remains SDR under each preference. Disabled mode uses the native HDR10/HLG path. At 4K60, its previous 24-bpp behavior is retained rather than globally altered. |
| Preferences | Values persist across Kodi restart. A changed output mode does not alter an active session or a seek; it applies to the next playback. Native LibreELEC selection was exercised. |
| Information | Enhanced and stock panels open and close with the existing player actions. No Dolby logos or speaker diagram are added. |
| Render telemetry | Sanitized parser/delta tests cover duplicate clients, counter regression, capacity changes, missing data and sampling resets. Physical TV-Led and HDR10 FEL playback reports valid occupancy with unchanged drop/skip counters; properties stop refreshing when the panel closes. |
| Steady playback | Final-image P7 FEL CM4 runs measured 90 seconds per output mode with unchanged native drop/skip counters. Mean render-engine occupancy was 51.38% TV-Led and 51.99% HDR10; total CPU was 1.38% and 1.42%. These are sample-specific engine measurements, not total GPU power or N100 results. |
| Final restoration | No active player or failed service. The 4K60 desktop has DV signaling, conversion deep-color and HDR metadata cleared. Standard TV-Led defaults restored. |

The HDR10 path preserves reconstructed source values, including supported FEL
residuals. It does not claim proprietary target-display CM4 mapping or visual
equivalence to a licensed Dolby conversion engine. The framebuffer is currently
10-bit. The tested conversion output is
progressive 3840x2160. No additional N100 or legacy-TV qualification is claimed.

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
# Format-aware information panel

The adaptive panel was exercised with SDR, HDR10, HLG, Standard Dolby Vision and Dolby Vision converted to HDR10. Native formats select the compact panel; both DV paths retain source metadata. Missing metadata rows are hidden. HDR10 static mastering and content-light values were verified against the source. This UI change does not modify video processing or output selection.
