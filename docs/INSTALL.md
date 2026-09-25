# Install, update and recover

This is an independent experimental community image based on development
LibreELEC/Kodi versions. Start on a spare drive and keep a known-good boot medium.
Do not overwrite your only working installation without a backup.

## New installation

1. Download this release's Generic x86_64 `.img.gz` and `SHA256SUMS`.
2. Verify its SHA-256. Use LibreELEC's USB-SD Creator in **Select file** mode or
   another trusted image writer. Writing an image erases the selected drive;
   check the model and capacity before confirming.
3. Boot it on the intended Intel machine and use LibreELEC's normal setup wizard.
4. Connect a qualifying Standard-DV TV through native HDMI. Configure Kodi's
   ordinary refresh-rate adjustment/whitelist for the modes your TV supports.
5. Play a compatible file through Kodi. There is no experimental-DV toggle:
   selection is automatic. Kodi's existing player information reports the
   source and active DV transport; the display's own DV indicator is a separate
   confirmation.

This image does not include personal accounts, SSH keys, saved remote-control
credentials, personal addons, media sources or movies. Configure access and
choose your own password using upstream LibreELEC settings. Do not expose Kodi
JSON-RPC or SSH to the public internet.

## Update an existing test installation

Use the matching `.tar` with LibreELEC's normal manual update procedure, after
backing up settings. Do not mix a KERNEL from one build with SYSTEM from another.
An upstream auto-update can replace this custom stack; choose update behavior
deliberately in LibreELEC's existing settings. This project adds no update service.

## Recovery

Keep the previous complete update archive and your LibreELEC backup separately.
If the device still boots, restore a known-good matching KERNEL/SYSTEM using the
standard updater. If it does not, boot your recovery/install medium and restore
the previous installation. Major Kodi-version downgrades may require restoring
the matching userdata backup; an OS rollback is not a database downgrade tool.

For diagnosis, the existing Intel kernel parameter can disable experimental
transport (`i915.enable_dv_lab=0` or `xe.enable_dv_lab=0`, according to the active
driver). This is a recovery control, not a custom UI requirement. Keep all
unrelated boot arguments unchanged.

Official reference: [LibreELEC manual updates](https://wiki.libreelec.tv/support/update).
