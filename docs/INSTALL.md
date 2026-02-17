# Install Faded Balancer DCTL

## Windows (Preferred)

1. Install with winget:
   - `winget install FabioColor.FadedBalancerDCTL`
2. Restart DaVinci Resolve.
3. In the Color page, add a **DCTL** effect and select `FadedBalancerDCTL`.

## Installer ZIP (Windows/macOS Fallback)

1. Download from the latest release:
   - `FadedBalancerDCTL-Setup-<version>-win64.zip` (Windows)
   - `FadedBalancerDCTL-<version>-macos.zip` (macOS)
2. Extract the ZIP.
3. Run the installer inside (`.exe` on Windows, `.pkg` on macOS).
4. Restart DaVinci Resolve.

## Manual `.dctl` Install (Fallback)

1. Download `FadedBalancerDCTL.dctl` from the latest release.
2. Copy it to your DaVinci Resolve LUT folder:
   - Windows: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
   - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
3. Restart DaVinci Resolve.
4. Add a `DCTL` node/effect and choose `FadedBalancerDCTL`.

## Uninstall

- If installed with winget: `winget uninstall FabioColor.FadedBalancerDCTL`
- If installed with installer ZIP: run the same installer again and choose uninstall if prompted.
- If installed manually: delete `FadedBalancerDCTL.dctl` from the LUT folder, then restart Resolve.
