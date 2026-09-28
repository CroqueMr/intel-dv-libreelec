# Video output

Settings are in **Kodi > Settings > Player > Videos**, available at **Basic** level. Playback preferences apply to the next file.

| Setting | Result |
| --- | --- |
| Standard Dolby Vision (TV-Led) | Default. Sends reconstructed video and frame-matched Dolby Vision metadata to a compatible display. |
| Convert Dolby Vision to HDR10 output | Reconstructs the source, including supported FEL residuals, then applies L1-guided tone mapping to a source-derived mastering target and sends PQ/BT.2020 HDR10. |
| Disable Dolby Vision support | Uses Kodi's ordinary playback and HDR handling without the custom Dolby Vision output path. |

HDR10 conversion uses libplacebo's spline tone mapping with frame-matched L1 maximum and average luminance. The target peak comes from valid RPU L6 mastering metadata, otherwise from RPU source maximum PQ. Missing usable target metadata rejects conversion rather than inventing a brightness target. Valid streams without usable L1 use static source luminance.

No inverse tone mapping, TV calibration or HGiG setting is required. Highlights above the reference peak are compressed; dim scenes are not expanded to fill it. Processing occurs after FEL reconstruction and before interface composition. The final resolve only applies signal range and quantization.

The HDMI metadata declares the reference peak. MaxCLL and MaxFALL are left unknown because source measurements do not describe the transformed output. The television still applies its normal HDR10 display mapping.

This is an open L1-guided conversion, not Dolby VS10 or a complete CM2.9/CM4 display-management implementation. It does not apply creative trims or guarantee the same rendering as TV-led DV. Software regression tests pass; real-display and hardware performance qualification of this conversion remains pending.

## Rendering information

The enhanced Player information panel separates video/audio, DV metadata and rendering
statistics. Profile, level, configuration version and CM metadata are distinct.
Pixel format describes decoded-source chroma subsampling (for example YUV 4:2:0), not the hardware surface. Source bit depth comes from the decoded
picture and is separate from the output framebuffer and HDMI transport.
GPU render (Kodi) reports this process's render-engine occupancy from DRM fdinfo,
including the visible overlay. It is not whole-device utilization, power or a
measurement of the hardware video decoder. Sampling is limited to twice per
second while the enhanced panel is open; unavailable counters are hidden.

## Output precision

HDR10 conversion uses a 10-bit framebuffer. Output precision is not user-selectable.

Framebuffer precision and HDMI link precision are different. A connector's maximum bit-depth property is a negotiation limit, not proof of the transmitted bit depth. An RGB8 Dolby Vision tunnel is a transport representation, not an SDR8 conversion.

Conversion requests a deep-color HDMI link explicitly. The driver retains its
normal sink and bandwidth validation and can choose supported YCbCr 4:2:0 when
RGB deep color does not fit. It rejects a conversion link below 10 bits rather
than silently reducing precision. This opt-in does not change native Kodi HDR.
The current conversion path targets progressive 3840x2160 output.

## Playback information

**Enhanced player information** replaces the stock information panel. Press **O** to open or close it; **Esc/Back** closes it. Disable the option to restore the stock panel. The existing **Ctrl+Shift+O** diagnostic remains unchanged.

The panel separates source metadata, reconstruction and output. SDR, HDR10 and HLG use a compact video/audio/rendering layout without DV sections. Static HDR metadata appears only when available. Dolby Vision sources retain their detailed panel, including during HDR10 conversion. Missing or inapplicable fields are hidden. FEL presence is not reported as successful reconstruction until a corresponding frame is presented. Drop and skip values are Kodi's own counters; pattern correction is not a dropped-frame counter.

The bottom-aligned panel fits its tallest visible column, with no close-action footer. No Dolby logos or speaker diagram are included. Metadata refresh is limited to twice per second while the panel is open.

## Diagnostics

Output selection, metadata origin, presentation failures and restoration are recorded automatically in kodi.log. A playback-health summary records native frame counters, video queue state and Kodi render-engine usage every 10 seconds, including with the panel closed. Existing bounded kernel diagnostics remain available. No per-frame metadata dumps or image readbacks are added. See [playback diagnostics](PLAYBACK-HEALTH.md).
