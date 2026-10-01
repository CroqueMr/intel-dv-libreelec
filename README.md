# Intel Dolby Vision for LibreELEC

Experimental Native Dolby Vision playback in Kodi on compatible Intel HDMI systems.

An independent **LibreELEC Generic x86_64 community build**, using Kodi's own
VideoPlayer, VAAPI decoder and GBM/GLES display path. **No external player, or proprietary Dolby SDK is required.**

**R0.3.0.** Built on LibreELEC 13 development sources and
Kodi 22 RC1, not on a stable LibreELEC release. Not affiliated with or
certified by LibreELEC, Kodi, Dolby or Intel. Report this build's issues here,
not to upstream projects unless reproduced with their unmodified releases.

## New in R0.3.0

- Convert Dolby Vision to HDR10, including Profile 7 FEL reconstruction and L1-guided tone mapping.
- Choose Standard Dolby Vision (TV-Led), HDR10 conversion, or Disable Dolby Vision support in **Kodi > Settings > Player > Videos**, at the **Basic** level.
- Optional **Player information** panel with source format, bit depth, DV metadata and GPU render usage. Press **O** during playback.
- Lightweight automatic diagnostics for frame drops, skips and playback transitions.

Standard Dolby Vision remains the default. LibreELEC Settings is unmodified.
See [release notes](docs/releases/0.3.0.md) and [conversion details](docs/OUTPUT-MODES.md).

## What changes

| Component | Base used | Patches | Purpose |
| --- | --- | ---: | --- |
| Linux / Intel display driver | 7.2.6 | 14 | Match Standard-DV signaling, protect byte-exact scanout, and require deep color for opt-in HDR10 conversion. |
| FFmpeg | 9.0 | 3 | Preserve extended DV metadata and recognize DV AV1 container tags. |
| libplacebo | 7.372.0, pinned commit | 9 | Preserve rendering precision, correct neutral FEL residual rounding and support an exact, lower-overhead GPU path. |
| Kodi + shared DV renderer | 22.0 RC1, pinned commit | 5 | Reconstruct video layers, select Standard DV or L1-guided HDR10, and expose optional playback information. |
| LibreELEC build recipes | 13.0-devel, pinned commit | 2 recipe overrides | Build and link the matching components. |
| Mesa / Intel Media Driver / libva | 26.2.3 / 26.3.5 / 2.24.1 | 0 | Use the existing graphics and hardware-decoding stack. |
| LibreELEC Settings | Pinned source | 0 | Unmodified. Playback preferences use Kodi's native settings. |
| Kodi Estuary skin | Included in Kodi patch | 0 separate | Optional three-column Player information; the stock panel remains available. |

**31 patches**, with no separate licensing-only patch series.
The two recipe overrides are counted separately, not as patches.
The shared renderer is included in the Kodi patch; it is not another player.
See [every patch and changed file](docs/CHANGES.md), [exact source versions](docs/VERSIONS.md)
and [architecture](docs/ARCHITECTURE.md).

Black screen or playback problem? DV diagnostics are recorded automatically;
share `kodi.log` without enabling global debug logging.
[Diagnostic collection](docs/DIAGNOSTICS.md) includes relevant kernel evidence;
nothing is uploaded automatically.

## Player information

Optional playback information with source pixel format, bit depth, metadata,
output mode and Kodi GPU render usage. SDR and HDR10 hide irrelevant DV fields.
The original Kodi panel remains available.

### Dolby Vision Profile 7 FEL

![Player information during Profile 7 FEL TV-led playback](docs/images/ppi-dv-profile7.png)

### Dolby Vision without FEL

![Player information during Avatar Dolby Vision playback without FEL](docs/images/ppi-dv-avatar.png)

Real playback captures, delivered at 1920x1080 and enlarged from the television's
960x540 capture. Capture brightness and colors
are not a reference for the television's actual rendering.

## Dolby Vision profiles

| Source profile | Supported |
| --- | --- |
| 5 | Yes |
| 7 MEL / FEL | Yes |
| 8.1 / 8.2 / 8.4 | Yes |
| 10 (AV1) | Yes |
| 9 | No |
| Legacy profiles 0–4 and 6 | No |
| 20 | No |

CM2.9 and CM4 metadata transport are implemented. These names describe metadata
generations, not additional video profiles. The HDMI output is **Standard DV**
(TV-led), not LLDV. The television performs display management; this project
does not claim Dolby certification or compatibility with every authored stream.

Hardware performance and compatibility vary. [Validation and limits](docs/VALIDATION.md)
describe the available evidence.

## Intel hardware

The driver gate is Intel **display generation 12 or later**, not a CPU-name
allowlist. A suitable native HDMI route and Standard-DV display are also needed.

| Family | Example CPUs | Release status |
| --- | --- | --- |
| Tiger Lake / Iris Xe | Core i7-11390H, i5-1135G7, i7-1165G7 | Tested on 11390H; other models untested. |
| Rocket Lake | Core i5-11500, i7-11700 with enabled iGPU | Driver-eligible candidate; to be tested |
| Alder Lake / Raptor Lake / refresh | 12th–14th-generation Core with supported iGPU | Driver-eligible candidate; to be tested  |
| Alder Lake-N / Twin Lake | N95, N97, N100, N200, N150, N250 | Driver-eligible candidate; to be tested  |
| Meteor Lake / Arrow Lake | Core Ultra 100 / 200 H, U or S where the display stack qualifies | Driver-eligible candidate; to be tested  |
| Lunar Lake | Core Ultra 200V | Tested on 226V; other models untested. |

**Performance must be analyzed on every setup**, including resolution,
frame rate, FEL workload, subtitles and cooling. Eligibility is not a promise
of real-time 4K playback. Intel F/KF CPUs without an iGPU, older unsupported
display engines, non-Intel GPUs, active DP-to-HDMI/LSPCON paths and LLDV-only
displays are outside the supported DV route. See [hardware requirements](docs/HARDWARE.md).

## Get started

Download [R0.3.0](https://github.com/CroqueMr/intel-dv-libreelec/releases/tag/R0.3.0):
the installation `.img.gz` or the manual-update `.tar`; only one is needed.
See [video output preferences and conversion limits](docs/OUTPUT-MODES.md).
The larger [complete source bundle](docs/SOURCE-BUNDLE.md) is for developers and
redistribution, not installation.

- [Install, update and recover](docs/INSTALL.md): use a spare device first.
- [Build from the pinned sources](docs/BUILD.md): the repository contains the patches and recipes.
- [Validation and limitations](docs/VALIDATION.md).
- [Licenses and source attribution](docs/LICENSING.md).


## Repository layout

- `patches/` - changes to Linux, FFmpeg, libplacebo and Kodi.
- `overlay/` - LibreELEC package recipes.
- `tools/` - scripts to apply, build-check and export the sources.
- `config/` - pinned versions and patch/overlay manifests.
- `docs/` - build guides, hardware notes and [release notes](docs/releases/0.3.0.md).
- `LICENSES/` - license texts and third-party notices.
