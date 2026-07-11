# Development and build tools

## Release preflight

Run the source-level checks from the repository root before building a release:

```bash
python3 tools/validate_presets.py
python3 tools/test_range_recovery.py
python3 tools/test_dctl_pipeline.py
```

`validate_presets.py` treats the ten preset blocks embedded in
`FadedBalancerDCTL.dctl` as authoritative. It verifies the selector labels and
implementation blocks, finite numeric values, live UI slider ranges, combo-box
enum/label mappings where source definitions are available, and preset headings
in `docs/presets_companion.md`. The optional positional JSON path is retained for
backward compatibility:

```bash
python3 tools/validate_presets.py presets/presets.json
```

That JSON file is intentionally a deprecation pointer, not a second preset
database. The validator accepts the pointer and rejects a reintroduced external
preset list.

`test_range_recovery.py` exercises the progressive dark-then-bright recovery
math against a sequential two-stage oracle. `test_dctl_pipeline.py` covers the
full source contract and numerically mirrors the other processing stages,
including extended-range and overflow stress cases.

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

## Tool index

- **Releases:** [create_releases.sh](create_releases.sh) — creates or updates GitHub releases from tags and uploads release assets.
- **macOS installer:** [build_mac_installer.sh](build_mac_installer.sh) — builds the macOS package.
- **Presets:** [validate_presets.py](validate_presets.py) — validates the authoritative preset blocks embedded in the DCTL.
- **Range recovery:** [test_range_recovery.py](test_range_recovery.py) — regression-tests progressive dark-then-bright channel recovery.
- **Full pipeline:** [test_dctl_pipeline.py](test_dctl_pipeline.py) — performs adversarial numerical and source-contract checks across the DCTL pipeline.
