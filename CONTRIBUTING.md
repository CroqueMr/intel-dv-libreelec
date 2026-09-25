# Contributing

Keep changes scoped to the DV path and preserve vanilla SDR/HDR behavior.
Include a small regression test for ownership, bounds, synchronization or state
restoration changes. Never weaken an assertion to turn a failure into a pass.

Before proposing changes, run the source checks and relevant tests described in
docs/VALIDATION.md. State whether results are software-only or measured on real
hardware. Provide exact versions and avoid broad claims based only on a CPU name.

Documentation can be edited normally, including directly on GitHub: no checksum
refresh is required. Build/check scripts live in `tools/`, and version/overlay
manifests live in `config/`. If you intentionally change a patch or recipe, update
its entry in `config/dvbridge-overlay.json` after review; those hashes protect the
actual build inputs, not the wording of documentation.

Use English for code comments, documentation and commit subjects. Explain why a
change is needed and keep patches reviewable. Preserve copyright notices and
identify the source/license of inherited code. Do not submit proprietary SDKs,
confidential material, credentials or copyrighted media without permission.

The intended public patch description is its concise English commit subject;
docs/CHANGES.md provides a longer per-file explanation.
