# Maintainer Release Notes

This page is for repository maintainers only.

End-user docs:
- `docs/INSTALL.md`

Maintainer/build/release references:
- `.github/workflows/release-on-tag.yml`
- `tools/create_releases.sh`
- `tools/build_win_installer.ps1`
- `tools/build_mac_installer.sh`
- `tools/README.md`

Policy:
- Public release assets: ZIP installers + `FadedBalancerDCTL.dctl` + `INSTALL.md`
- Internal security/check files: workflow artifacts (maintainer-only)

Winget/automation note (Windows installer):
- Use explicit Inno silent switches in manifests:
- `Silent: /VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /SP-`
- `SilentWithProgress: /SILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /SP-`
