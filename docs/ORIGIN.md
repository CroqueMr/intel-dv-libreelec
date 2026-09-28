# Source credits

This native Kodi port reuses the Intel DV Linux transport implementation rather
than replacing it with an unrelated player. Its common C renderer can be reused
by other players; this release builds it directly into Kodi.

| Origin | Use in this repository |
| --- | --- |
| Linux / Intel DRM and HDMI contributors | Existing driver implementation plus the connector, signaling and scanout-policy patches. |
| FFmpeg contributors | Parser/decoder integration and metadata structures, with extension-byte preservation patches. |
| Kodi contributors | Native VideoPlayer, VAAPI, GBM, GLES and player-information integration. |
| libplacebo contributors | Video reshaping and rendering, with precision and dispatch changes. |
| Intel DV Linux / mpv adapter | Metadata serialization and CM4 helper ancestry; extracted into player-independent helpers. No mpv executable is included. |
| quietvoid / dovi_tool contributors | CM4 grammar reference, revision `d4ad4ba7`; MIT attribution retained. |
| Riccardo Biasiotto / PGenerator-Plus and ofxRPI4Window contributors | Inherited transport reference; PGenerator-Plus revision `835b9b9d336ada701d8fa5552889921849886e04`, GPLv3-or-later. |
| ETSI GS CCM 001 V1.1.1 | Public metadata transport reference; no copy of the specification is bundled. |

The two inherited metadata headers carry a derivation receipt in
`tools/dvbridge/PROVENANCE.json`, inside the Kodi patch. It records their exact
content, not a claim that every algorithm was independently invented.
Source versions, archive hashes and per-file changes make the integration
reviewable. These credits are not endorsements or certification.

Repository organization follows established community-build practice: a pinned
upstream base, separate patches, explicit build instructions and release assets.
Examples reviewed: [LibreELEC community-build policy](https://libreelec.tv/2018/04/30/community-builds/),
[VDRSternELEC](https://github.com/Zabrimus/VDRSternELEC),
[LibreELEC-RR](https://github.com/5schatten/LibreELEC-RR).
Their README presentation/build structure informed this repository organization;
their implementation code was not imported for that purpose.

## Standard-DV display compatibility (R0.2.1a-opt1)

The shared `dvbridge_edid.h` / `DVBridgeEdid.h` parser is an original, bounded
implementation of public EDID fields. Its two copies are byte-identical and
tested in C and C++. Field layouts were checked against libdisplay-info 0.4.0
(`cta.c`, Dolby video block parsing) and its
[public header documentation](https://emersion.pages.freedesktop.org/libdisplay-info/libdisplay-info/cta.h.html).
No libdisplay-info parser implementation was copied into the kernel.

Legacy HDMI-OUI Standard-DV packet selection was cross-checked against the
[public Amlogic HDMI implementation](https://nest-open-source.googlesource.com/manifest_repos/kernel/+/1650886512330522da41d487bb2ce75fd5da5ec8/drivers/amlogic/media/vout/hdmitx/hdmi_tx_20/hdmi_tx_main.c)
at revision `1650886512330522da41d487bb2ce75fd5da5ec8`, in its v0/v1 signaling
branch: 24-byte payload, HDMI OUI and the legacy 4K VIC mapping. Only the protocol
facts were used; the vendor driver/control flow was not imported. The Linux
patch extends the existing kernel packet structures and canonical serializer.
Its source notices are preserved. This reference is not a proprietary Dolby SDK
and is not a claim of vendor endorsement or physical compatibility.
