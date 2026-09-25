# Hardware requirements

The tested LE platform is an Intel Core i7-11390H Geekom IT11 / Iris Xe system, connected
through native HDMI to an LG G5. Results apply to that route, not every mini-PC
sold with the same CPU.

## Conditions for automatic DV output

1. Intel display engine generation 12 or later, handled by the patched display
   driver; the CPU marketing generation alone is not sufficient.
2. Native HDMI, without active DisplayPort/LSPCON conversion. A native HDMI
   level shifter is not rejected merely for exposing a dual-mode identifier.
3. A valid Dolby EDID v2 block advertising Standard DV. LLDV-only and older
   EDID variants are not accepted by this release's policy.
4. A supported progressive 3840 × 2160 display mode in Kodi, atomic GBM/GLES
   output and the required texture/rendering precision.
5. Hardware decoding and import of the actual stream format. FEL additionally
   requires enhancement-layer decoding and matched surfaces.

The driver policy accepts CTA 24/25/30/50/60 Hz timings and their fractional
variants, including 23.976 Hz. Acceptance is not a performance certification at
every rate. Kodi's renderer currently uses a 4K transport raster; a lower
resolution source does not make this a qualified 1080p-output implementation.

## Performance reporting

Report the exact CPU, PCI/display driver, HDMI route, TV, source profile/codec,
resolution/rate, visible subtitles.

GPU engine-busy percentages are not additive and are not power measurements.
Dynamic GPU clocks can reduce power/work without producing a proportional
change in a single utilization number. Do not compare them directly to Android
decoder-chip utilization.

N100/N150 and other small iGPUs are candidates for validation and optimization,
not advertised as guaranteed real-time FEL/4K60 devices. No CPU offload is used
as a substitute for the GPU reconstruction path.
