# Build tools

## Installer build dependencies

### Windows (for `build_win_installer.ps1`)

- **Inno Setup** (provides `iscc`):
  - **Option A:** `winget install JRSoftware.InnoSetup`  
    After install, you may need to **restart the terminal** (or log out and back in) so `iscc` is on PATH. The build script also checks `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` if not on PATH.
  - **Option B:** Download and install from [jrsoftware.org](https://jrsoftware.org/isinfo.php), then ensure the install directory (e.g. `C:\Program Files (x86)\Inno Setup 6`) is on your PATH.

### macOS (for `build_mac_installer.sh`)

- **Xcode Command Line Tools** (provides `pkgbuild`):
  - Run: `xcode-select --install`  
  - Or install full Xcode from the App Store.

---

- **Releases:** [create_releases.sh](create_releases.sh) — creates/updates GitHub releases from tags and uploads the `.dctl` asset.
- **Presets:** [validate_presets.py](validate_presets.py) — validates `presets/presets.json` against the DCTL.
