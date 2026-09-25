# Intel DV for LibreELEC

Native Dolby Vision playback in Kodi on compatible Intel HDMI systems.

An independent **LibreELEC Generic x86_64 community build**, using Kodi's own
VideoPlayer, VAAPI decoder and GBM/GLES display path. No external player, custom
skin, activation menu or proprietary Dolby SDK is required.

**Release candidate: 0.1.0-rc1.** Built on LibreELEC 13 development sources and
Kodi 22 Beta 2, not on a stable LibreELEC release. Not affiliated with or
certified by LibreELEC, Kodi, Dolby or Intel. Report this build's issues here,
not to upstream projects unless reproduced with their unmodified releases.

## What changes

| Component | Base used | Patches | Purpose |
| --- | --- | ---: | --- |
| Linux / Intel display driver | 7.2.6 | 11 | Discover Standard DV displays, signal HDMI DV, protect byte-exact scanout and validate the native HDMI route. |
| FFmpeg | 9.0 | 3 | Preserve extended DV metadata and recognize DV AV1 container tags. |
| libplacebo | 7.372.0, pinned commit | 8 | Preserve rendering precision, correct neutral FEL residual rounding and support an exact, lower-overhead GPU path. |
| Kodi + shared DV renderer | 22.0 Beta 2, pinned commit | 1 | Decode and pair video layers, reconstruct FEL, synchronize metadata, compose the normal player interface and present native HDMI DV. |
| LibreELEC build recipes | 13.0-devel, pinned commit | 2 recipe overrides | Build and link the matching components. |
| Mesa / Intel Media Driver / libva | 26.2.3 / 26.3.5 / 2.24.1 | 0 | Use the existing graphics and hardware-decoding stack. |
| LibreELEC Settings / Kodi skin | Upstream | 0 | Original menus and appearance; DV is selected automatically when eligible. |

**23 functional patches**, with no separate licensing-only patch series.
The shared renderer is included in the Kodi patch; it is not another player.
See [every patch and changed file](docs/CHANGES.md), [exact source versions](docs/VERSIONS.md)
and [architecture](docs/ARCHITECTURE.md).

## Dolby Vision profiles

| Source profile | Status | Current evidence / boundary |
| --- | --- | --- |
| 5 | Supported | Native Kodi/HDMI playback checked on i7-11390H. |
| 7 MEL | Implemented | MEL is distinguished from a non-trivial FEL residual; dedicated LE playback coverage remains to be expanded. |
| 7 FEL | Supported | Base layer + enhancement layer reconstruction + metadata; native playback and exact GPU output checks. |
| 8.1 | Supported | Native Kodi/HDMI playback checked, including CM4. |
| 8.2 | Implemented, qualification pending | Uses the common metadata/reshaping path; not yet a qualified LE playback result. |
| 8.4 | Supported | Native Kodi/HDMI playback checked, including CM4. |
| 9 | Not supported by this release | The pinned H.264 decoder does not supply the required DV metadata to this path. |
| 10 (AV1) | Supported for tested streams | Native Kodi/HDMI playback checked; do not assume every compatibility variant, rate or GPU is qualified. |
| Legacy profiles 0–4 and 6 | Not supported | Outside this implementation's scope. |
| 20 | Not supported | Outside this implementation's scope. |

CM2.9 and CM4 metadata transport are implemented. These names describe metadata
generations, not additional video profiles. The HDMI output is **Standard DV**
(TV-led), not LLDV. The television performs display management; this project
does not claim Dolby certification or compatibility with every authored stream.

No issue was observed under the recorded successful playback protocols for the
tested rows. [Validation and limits](docs/VALIDATION.md) distinguish software
checks, real HDMI playback and untested combinations.

## Intel hardware

The driver gate is Intel **display generation 12 or later**, not a CPU-name
allowlist. A suitable native HDMI route and Standard-DV display are also needed.

| Family | Example CPUs | Release status |
| --- | --- | --- |
| Tiger Lake / Iris Xe | Core i7-11390H, i5-1135G7, i7-1165G7 | **i7-11390H tested with this LE/Kodi implementation**; other models untested. |
| Rocket Lake | Core i5-11500, i7-11700 with enabled iGPU | Driver-eligible candidate; board HDMI route and performance untested. |
| Alder Lake / Raptor Lake / refresh | 12th–14th-generation Core with supported iGPU | Driver-eligible candidates; model-by-model validation required. |
| Alder Lake-N / Twin Lake | N95, N97, N100, N200, N150, N250 | Driver-eligible candidates; smaller GPUs may require further performance work. |
| Meteor Lake / Arrow Lake | Core Ultra 100 / 200 H, U or S where the display stack qualifies | Candidate families, not a blanket compatibility claim. |
| Lunar Lake | Core Ultra 200V, including 226V | Shared driver/transport previously tested on 226V with mpv; **this LE/Kodi image still needs device-specific qualification**. |

**Performance must be assessed on every reference**, including resolution,
frame rate, FEL workload, subtitles and cooling. Eligibility is not a promise
of real-time 4K playback. Intel F/KF CPUs without an iGPU, older unsupported
display engines, non-Intel GPUs, active DP-to-HDMI/LSPCON paths and LLDV-only
displays are outside the supported DV route. See [hardware requirements](docs/HARDWARE.md).

## Get started

- [Install, update and recover](docs/INSTALL.md): use a spare device first.
- [Build from the pinned sources](docs/BUILD.md): the repository contains the patches and recipes.
- [Run the checks](docs/VALIDATION.md): software tests do not require a television.
- [Licenses and source attribution](docs/LICENSING.md).

Images belong in **GitHub Releases**, not in Git history. A binary release must
be accompanied by its checksums and matching source bundle; never substitute an
older image just because its filename looks similar.
