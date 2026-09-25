# Changes by component and file

This index describes the actual exported patches, not an upstream fork history.
Apply patches in filename order within each component. The Kodi patch includes
the shared renderer; its internal files are listed individually below.

## linux

| Patch | Purpose |
| --- | --- |
| [linux-9900-00-drivers__gpu__drm__i915__display__intel_atomic.c.patch](../patches/linux/linux-9900-00-drivers__gpu__drm__i915__display__intel_atomic.c.patch) | Expose the validated Dolby Vision connector control. |
| [linux-9900-01-drivers__gpu__drm__i915__display__intel_display.c.patch](../patches/linux/linux-9900-01-drivers__gpu__drm__i915__display__intel_display.c.patch) | Protect Dolby Vision transport from display processing. |
| [linux-9900-02-drivers__gpu__drm__i915__display__intel_display_params.c.patch](../patches/linux/linux-9900-02-drivers__gpu__drm__i915__display__intel_display_params.c.patch) | Retain the low-level Dolby Vision recovery parameter. |
| [linux-9900-03-drivers__gpu__drm__i915__display__intel_display_params.h.patch](../patches/linux/linux-9900-03-drivers__gpu__drm__i915__display__intel_display_params.h.patch) | Enable automatic eligible Dolby Vision in this image. |
| [linux-9900-04-drivers__gpu__drm__i915__display__intel_display_types.h.patch](../patches/linux/linux-9900-04-drivers__gpu__drm__i915__display__intel_display_types.h.patch) | Track Dolby Vision state on Intel HDMI connectors. |
| [linux-9900-05-drivers__gpu__drm__i915__display__intel_dv_lab_policy.h.patch](../patches/linux/linux-9900-05-drivers__gpu__drm__i915__display__intel_dv_lab_policy.h.patch) | Validate TV capabilities and supported Dolby Vision modes. |
| [linux-9900-06-drivers__gpu__drm__i915__display__intel_dvbridge_hdr_policy.h.patch](../patches/linux/linux-9900-06-drivers__gpu__drm__i915__display__intel_dvbridge_hdr_policy.h.patch) | Preserve HDR10 precision when HDMI bandwidth is limited. |
| [linux-9900-07-drivers__gpu__drm__i915__display__intel_hdmi.c.patch](../patches/linux/linux-9900-07-drivers__gpu__drm__i915__display__intel_hdmi.c.patch) | Connect Intel HDMI negotiation to Dolby Vision output. |
| [linux-9900-08-drivers__video__hdmi.c.patch](../patches/linux/linux-9900-08-drivers__video__hdmi.c.patch) | Encode and validate Dolby Vision HDMI signaling. |
| [linux-9900-09-include__linux__hdmi.h.patch](../patches/linux/linux-9900-09-include__linux__hdmi.h.patch) | Define shared Dolby Vision HDMI signaling structures. |
| [linux-9901-native-hdmi-level-shifter.patch](../patches/linux/linux-9901-native-hdmi-level-shifter.patch) | Recognize native HDMI level shifters without allowing active DP conversion. |

| Changed source file | High-level change |
| --- | --- |
| `drivers/gpu/drm/i915/display/intel_atomic.c` | Expose/read/write the per-connector DV property in atomic state. |
| `drivers/gpu/drm/i915/display/intel_display.c` | Validate byte-preserving scanout and reject incompatible display processing. |
| `drivers/gpu/drm/i915/display/intel_display_params.c` | Describe the low-level recovery control; no user-facing activation menu. |
| `drivers/gpu/drm/i915/display/intel_display_params.h` | Default the dedicated LE image to automatic capability detection. |
| `drivers/gpu/drm/i915/display/intel_display_types.h` | Store DV property and transport state on the Intel connector. |
| `drivers/gpu/drm/i915/display/intel_dv_lab_policy.h` | Validate EDID, modes and native-HDMI topology, including level shifters. |
| `drivers/gpu/drm/i915/display/intel_dvbridge_hdr_policy.h` | Retry eligible HDR10 links in deep-color 4:2:0 instead of losing precision to 8-bit RGB; exclude the DV tunnel. |
| `drivers/gpu/drm/i915/display/intel_hdmi.c` | Connect hardware eligibility, HDMI timing, signaling and HDR precision policy. |
| `drivers/video/hdmi.c` | Initialize, validate, pack and unpack the HDMI DV vendor information frame. |
| `include/linux/hdmi.h` | Define the HDMI DV signaling fields shared by the driver helpers. |

## ffmpeg

| Patch | Purpose |
| --- | --- |
| [ffmpeg-9900-00-libavcodec__dovi_rpudec.c.patch](../patches/ffmpeg/ffmpeg-9900-00-libavcodec__dovi_rpudec.c.patch) | Preserve extended Dolby Vision metadata during decoding. |
| [ffmpeg-9900-01-libavformat__isom_tags.c.patch](../patches/ffmpeg/ffmpeg-9900-01-libavformat__isom_tags.c.patch) | Recognize Dolby Vision AV1 tracks in MP4 containers. |
| [ffmpeg-9900-02-libavutil__dovi_meta.h.patch](../patches/ffmpeg/ffmpeg-9900-02-libavutil__dovi_meta.h.patch) | Carry extended Dolby Vision metadata to the player. |

| Changed source file | High-level change |
| --- | --- |
| `libavcodec/dovi_rpudec.c` | Retain parsed extension bytes so the output stage can preserve CM4 metadata. |
| `libavformat/isom_tags.c` | Recognize the dav1 MP4 sample entry for DV AV1 tracks. |
| `libavutil/dovi_meta.h` | Carry validated original extension bytes alongside parsed metadata. |

## libplacebo

| Patch | Purpose |
| --- | --- |
| [libplacebo-9900-0-src__dispatch.c.patch](../patches/libplacebo/libplacebo-9900-0-src__dispatch.c.patch) | Optimize eligible full-screen GPU rendering passes. |
| [libplacebo-9900-1-src__opengl__gpu.c.patch](../patches/libplacebo/libplacebo-9900-1-src__opengl__gpu.c.patch) | Discover supported OpenGL subgroup capabilities. |
| [libplacebo-9910-0.patch](../patches/libplacebo/libplacebo-9910-0.patch) | Expose supported full-precision GLES render targets. |
| [libplacebo-9910-1.patch](../patches/libplacebo/libplacebo-9910-1.patch) | Preserve high-bit-depth texture sampling precision. |
| [libplacebo-9910-2.patch](../patches/libplacebo/libplacebo-9910-2.patch) | Require full-precision intermediate rendering when requested. |
| [libplacebo-9910-3.patch](../patches/libplacebo/libplacebo-9910-3.patch) | Enable float texture filtering only when supported. |
| [libplacebo-9910-4.patch](../patches/libplacebo/libplacebo-9910-4.patch) | Prevent rounding noise from creating false FEL residuals. |
| [libplacebo-9910-5-custom-prelude.patch](../patches/libplacebo/libplacebo-9910-5-custom-prelude.patch) | Place custom GLES extension directives before shader declarations. |

| Changed source file | High-level change |
| --- | --- |
| `src/dispatch.c` | Optimize eligible dispatch and emit custom GLSL extension directives in the required order. |
| `src/include/libplacebo/renderer.h` | Expose an explicit minimum intermediate precision without silently reducing quality. |
| `src/opengl/formats.c` | Advertise renderable float textures and filtering only when GLES supports them. |
| `src/opengl/gpu.c` | Expose actual subgroup, float texture, filtering and framebuffer capabilities. |
| `src/renderer.c` | Honor full-precision intermediate render-target requirements. |
| `src/shaders/colorspace.c` | Keep neutral FEL residuals zero despite normalization/filtering roundoff. |

## kodi

| Patch | Purpose |
| --- | --- |
| [kodi-9990-native-dv.patch](../patches/kodi/kodi-9990-native-dv.patch) | Integrate automatic native Dolby Vision playback and exact GPU transport. |

| Changed source file | High-level change |
| --- | --- |
| `CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `LICENSES/GPL-3.0-or-later` | Retain the existing combined-build GPLv3 license text. |
| `LICENSES/README.md` | Retain the existing DV-enabled combined-build licensing notice. |
| `tools/dvbridge/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `tools/dvbridge/PROVENANCE.json` | Record the exact content and derivation of inherited metadata helpers. |
| `tools/dvbridge/dvbridge_core.c` | Prepare owned metadata and commit its state only after successful presentation. |
| `tools/dvbridge/dvbridge_core.h` | Define the player-independent metadata transaction and geometry API. |
| `tools/dvbridge/dvbridge_dmabuf.c` | Validate VAAPI descriptors and import DMA-BUF planes without CPU video copies. |
| `tools/dvbridge/dvbridge_dmabuf.h` | Describe the imported hardware-plane ownership and layout. |
| `tools/dvbridge/dvbridge_fel.c` | Split/decode the enhancement stream and pair surfaces by exact presentation time. |
| `tools/dvbridge/dvbridge_fel.h` | Define bounded enhancement-layer queue and reset operations. |
| `tools/dvbridge/dvbridge_gl_frame.c` | Map hardware texture planes into libplacebo frame descriptors. |
| `tools/dvbridge/dvbridge_gl_frame.h` | Define imported frame layout and release operations. |
| `tools/dvbridge/dvbridge_gl_pack.c` | Pack HDMI transport bytes with explicit GL state preservation. |
| `tools/dvbridge/dvbridge_gl_pack.h` | Define the final transport-packing API. |
| `tools/dvbridge/dvbridge_metadata.h` | Serialize frame-matched display metadata, active area, packet identifiers and CRCs. |
| `tools/dvbridge/dvbridge_placebo.c` | Validate and map DV reshaping parameters to libplacebo. |
| `tools/dvbridge/dvbridge_placebo.h` | Define the validated color/reshaping representation. |
| `tools/dvbridge/dvbridge_render.c` | Reconstruct full-precision video and select exact fused or composed transport rendering. |
| `tools/dvbridge/dvbridge_render.h` | Define the shared renderer lifecycle and prepare/commit boundary. |
| `tools/dvbridge/mpv_dvbridge_cm4.h` | Preserve and serialize supported extended CM4 metadata fields with strict bounds. |
| `tools/dvbridge/pack_gles300.frag` | Pack reconstructed video and metadata into the Standard-DV RGB8 transport. |
| `tools/dvbridge/pack_gles300.vert` | Generate full-screen transport geometry with the required orientation. |
| `xbmc/cores/VideoPlayer/DVDCodecs/DVDFactoryCodec.cpp` | Select the native DV decoder only when the stream and output are eligible. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodec.cpp` | Copy/reset owned DV metadata and enhancement-layer references with video pictures. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodec.h` | Add owned metadata and enhancement-surface state to the video picture. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodecFFmpeg.cpp` | Carry frame metadata and pair the hardware-decoded enhancement layer across decode/flush/seek. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVDVideoCodecFFmpeg.h` | Declare the decoder-side DV metadata and layer-pairing state. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVMetadataBuffer.h` | Own and bounds-check metadata independently of decoder buffer reuse. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVPlaybackInfo.h` | Publish coherent active-output information only after successful presentation. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/DVPlaybackPolicy.h` | Keep probes, interlaced/stereo and ineligible outputs outside the native DV path. |
| `xbmc/cores/VideoPlayer/DVDCodecs/Video/VAAPI.cpp` | Preserve decoded DV frame metadata through the native hardware surface path. |
| `xbmc/cores/VideoPlayer/DVDDemuxers/DVDDemux.h` | Expose source codec parameters required for enhancement-layer decoding. |
| `xbmc/cores/VideoPlayer/DVDDemuxers/DVDDemuxFFmpeg.cpp` | Capture the original stream parameters for the DV decode pipeline. |
| `xbmc/cores/VideoPlayer/DVDStreamInfo.cpp` | Copy and compare the additional stream parameters consistently. |
| `xbmc/cores/VideoPlayer/DVDStreamInfo.h` | Own the stream parameters passed from demuxing to decoding. |
| `xbmc/cores/VideoPlayer/VideoPlayer.cpp` | Keep native DV routing and source stream state consistent during playback setup. |
| `xbmc/cores/VideoPlayer/VideoRenderers/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/cores/VideoPlayer/VideoRenderers/DVBridgeGLES.cpp` | Integrate exact reconstruction/packing with native textures, FEL surfaces and GUI composition. |
| `xbmc/cores/VideoPlayer/VideoRenderers/DVBridgeGLES.h` | Define the native renderer lifecycle and frame/layer input contract. |
| `xbmc/cores/VideoPlayer/VideoRenderers/DVBridgeShaders.h.in` | Embed the shared transport shaders at build time. |
| `xbmc/cores/VideoPlayer/VideoRenderers/HwDecRender/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/cores/VideoPlayer/VideoRenderers/HwDecRender/RendererVAAPIGLES.cpp` | Import hardware planes and submit eligible frames to the DV renderer. |
| `xbmc/cores/VideoPlayer/VideoRenderers/HwDecRender/RendererVAAPIGLES.h` | Declare native hardware DV render integration. |
| `xbmc/cores/VideoPlayer/VideoRenderers/LinuxRendererGL.cpp` | Preserve the ordinary renderer path and guarded DV routing. |
| `xbmc/cores/VideoPlayer/VideoRenderers/LinuxRendererGL.h` | Declare the guarded rendering hook without changing ordinary output. |
| `xbmc/cores/VideoPlayer/VideoRenderers/LinuxRendererGLES.cpp` | Handle software/native texture input and choose DV output only when eligible. |
| `xbmc/cores/VideoPlayer/VideoRenderers/LinuxRendererGLES.h` | Track DV geometry and texture-rendering state. |
| `xbmc/cores/VideoPlayer/VideoRenderers/RenderManager.cpp` | Choose DV-aware modes and retain full composition when player overlays are visible. |
| `xbmc/cores/VideoPlayer/VideoRenderers/RenderManager.h` | Pass the DV mode requirement through the existing render configuration. |
| `xbmc/guilib/guiinfo/VideoGUIInfo.cpp` | Extend the existing stream-information value with active HDMI DV, FEL and CM generation. |
| `xbmc/platform/linux/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/utils/DisplayInfo.cpp` | Parse and expose Standard-DV display capability from the existing EDID information. |
| `xbmc/utils/DisplayInfo.h` | Store the detected DV display capability. |
| `xbmc/windowing/Resolution.cpp` | Constrain DV mode selection while keeping the existing non-DV policy. |
| `xbmc/windowing/Resolution.h` | Declare the DV-aware mode-selection parameter. |
| `xbmc/windowing/gbm/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/windowing/gbm/GBMUtils.cpp` | Manage explicit front-buffer ownership for safe presentation/rollback. |
| `xbmc/windowing/gbm/GBMUtils.h` | Declare the buffer lifecycle used by atomic presentation. |
| `xbmc/windowing/gbm/WinSystemGbm.cpp` | Report native DV eligibility and preserve normal output outside the DV path. |
| `xbmc/windowing/gbm/WinSystemGbm.h` | Expose the native-output capability to VideoPlayer. |
| `xbmc/windowing/gbm/WinSystemGbmEGLContext.cpp` | Allow the DV transport to request the required EGL output depth. |
| `xbmc/windowing/gbm/WinSystemGbmEGLContext.h` | Declare the output-depth hook used by the GLES DV adapter. |
| `xbmc/windowing/gbm/WinSystemGbmGLESContext.cpp` | Compose GUI before packing, perform transactional DV presentation and restore the normal display path. |
| `xbmc/windowing/gbm/WinSystemGbmGLESContext.h` | Own native DV rendering, composition and presentation state. |
| `xbmc/windowing/gbm/drm/CMakeLists.txt` | Build/link the native DV adapter and shared helpers behind the existing build-time feature boundary. |
| `xbmc/windowing/gbm/drm/DRMAtomic.cpp` | Perform checked atomic test/commit and preserve state on presentation failure. |
| `xbmc/windowing/gbm/drm/DRMAtomic.h` | Declare the atomic property and transaction operations. |
| `xbmc/windowing/gbm/drm/DRMUtils.cpp` | Discover the connector DV property and expose native output support. |
| `xbmc/windowing/gbm/drm/DRMUtils.h` | Declare DV connector capability queries. |
| `xbmc/windowing/gbm/drm/DVBridgeState.cpp` | Snapshot, stage and restore DRM properties without leaking state between streams. |
| `xbmc/windowing/gbm/drm/DVBridgeState.h` | Define ownership of the connector/property transaction. |

## LibreELEC recipes

| File | Change |
| --- | --- |
| `packages/mediacenter/kodi/package.mk` | Build/link libplacebo and enable the native DV adapter; retain the applicable combined-build license declaration; normalize embedded build paths. |
| `packages/addons/addon-depends/multimedia-tools-depends/libplacebo/package.mk` | Pin the tested libplacebo revision, enable DV/GLES and build a shared target library; normalize embedded build paths. |

No LibreELEC Settings, systemd activation service or skin patch is included.
The separate HDR10 precision retry is not a DV metadata or tone-mapping change.
