# Install Faded Balancer DCTL

These instructions apply to Faded Balancer DCTL 1.7.0. Restart DaVinci Resolve after installing, replacing, or removing the DCTL.

## Windows installer

Download either of these assets from the official GitHub release:

- `FadedBalancerDCTL-Setup-1.7.0.exe`
- `FadedBalancerDCTL-Setup-1.7.0-win64.zip` (contains the same installer)

Run the `.exe`, then add a **DCTL** effect on the Color page and select `FadedBalancerDCTL`.

The current Windows installer is not code-signed, so Microsoft Defender SmartScreen may show an unrecognized-app warning. Only continue if the file came from the official release and you trust it. The manual installation below avoids running an installer.

### Winget

After the Winget manifest has been updated to 1.7.0, install with:

```powershell
winget install FabioColor.FadedBalancerDCTL
```

Winget publication can lag behind the GitHub release. Check the version Winget offers before using it for this update.

## macOS installer

Download either of these assets from the official GitHub release:

- `FadedBalancerDCTL-1.7.0.pkg`
- `FadedBalancerDCTL-1.7.0-macos.zip` (contains the same package)

Run the `.pkg`, then add a **DCTL** effect on the Color page and select `FadedBalancerDCTL`.

The current macOS package is not signed or notarized. Gatekeeper may block the first launch. Only if you obtained the package from the official release and trust it, try opening it once, then use **System Settings > Privacy & Security > Open Anyway**. The manual installation below avoids running a package.

If an older version is present, the package offers **Replace & Install** or **Uninstall Only**.

## Manual `.dctl` installation

1. Download `FadedBalancerDCTL.dctl` from the official release.
2. Copy that exact file to the Resolve LUT folder:

   - Windows: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
   - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`

3. Restart Resolve.
4. Add a **DCTL** effect and select `FadedBalancerDCTL`.

## Uninstall

- Winget: `winget uninstall FabioColor.FadedBalancerDCTL`
- Windows installer: use **Settings > Apps > Installed apps**, or run the same `.exe` and choose uninstall.
- macOS package: run the same `.pkg` and choose **Uninstall Only** when prompted.
- Manual installation: delete `FadedBalancerDCTL.dctl` from the LUT folder.

If Resolve still lists an old version after replacement, confirm that there is only one file named `FadedBalancerDCTL.dctl` in the system and user LUT locations, then restart Resolve.
