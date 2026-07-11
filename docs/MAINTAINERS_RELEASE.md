# Maintainer release process

This page describes the 1.7.0 release path. End-user instructions are in `docs/INSTALL.md`.
The feature-by-feature engineering verdict is recorded in `docs/FEATURE_AUDIT_v1.7.0.md`.

## Required preflight

From the repository root, run:

```bash
python3 tools/test_range_recovery.py
python3 tools/test_dctl_pipeline.py
python3 tools/validate_presets.py presets/presets.json
bash -n tools/build_mac_installer.sh
bash -n tools/create_releases.sh
bash -n installers/mac/scripts/preinstall
bash -n installers/mac/scripts/postinstall
git diff --check
```

The tag workflow repeats these gates before creating a release and requires the first DCTL line to match the pushed tag exactly (for example, `// FadedBalancerDCTL v1.7.0`). A `-dev` header cannot be released. Do not tag if any gate fails.

Also complete a DaVinci Resolve host smoke test with the release-candidate `FadedBalancerDCTL.dctl`. Confirm default identity, progressive dark/bright recovery, the mixing masks and donor adjustment, and the diagnostic log preview on representative footage.

## Version and asset checklist

For v1.7.0, confirm that version references and release notes say `1.7.0`, then verify these exact public assets:

- `FadedBalancerDCTL.dctl`
- `INSTALL.md`
- `FadedBalancerDCTL-Setup-1.7.0.exe`
- `FadedBalancerDCTL-Setup-1.7.0-win64.zip`
- `FadedBalancerDCTL-1.7.0.pkg`
- `FadedBalancerDCTL-1.7.0-macos.zip`

The raw Windows `.exe` is required for Winget. The ZIP assets are convenience downloads. The package builders source the exact repository-root `FadedBalancerDCTL.dctl`; the workflow also compares the DCTL extracted from the macOS package with that source before upload.

## Release lifecycle

Pushing a `v*` tag runs `.github/workflows/release-on-tag.yml`:

1. Run numerical, preset, shell, and whitespace preflight checks.
2. Create the tagged GitHub release as a **draft** and attach the source DCTL and install guide.
3. Build Windows and macOS installers in parallel and attach their exact filenames to the draft.
4. Publish only after both installer jobs succeed.

If a build or upload fails, the release remains a draft instead of exposing a partial public release. Correct the problem and rerun the failed workflow jobs. Do not manually publish until all expected assets have been verified.

For a local notes/assets preview without creating anything:

```bash
./tools/create_releases.sh --tag v1.7.0 --preview
```

`tools/create_releases.sh --tag v1.7.0 --draft` is the CI creation path. It requires an authenticated GitHub CLI and does not publish the draft.

## Local package checks

Build the macOS package on a Mac with the Xcode command-line tools:

```bash
./tools/build_mac_installer.sh 1.7.0
pkgutil --check-signature installers/FadedBalancerDCTL-1.7.0.pkg
pkgutil --payload-files installers/FadedBalancerDCTL-1.7.0.pkg
```

The payload listing must contain `./FadedBalancerDCTL.dctl` exactly once and no `._` AppleDouble metadata entry.

The current Windows installer is unsigned, and the current macOS package is unsigned and not notarized. SmartScreen and Gatekeeper warnings are therefore expected. This must remain explicit in end-user documentation until signing and notarization are implemented. Do not claim that the installers are trusted or verified by the operating-system vendor.

The workflow stores SHA-256 manifests and both installer forms as internal Actions artifacts for maintainer verification. Treat code-signing certificates, notarization credentials, and any future public checksum publication as separate release work.

## Winget follow-up

After the GitHub release is public, update the Winget manifest to the raw `.exe` URL and its SHA-256. Use the existing Inno switches:

- `Silent: /VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /SP-`
- `SilentWithProgress: /SILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /SP-`

Verify the Winget manifest targets exactly v1.7.0 before describing Winget as current in public announcements.
