#!/usr/bin/env bash
# Build macOS installer .pkg for Faded Balancer DCTL (single package: run to install, run again to uninstall).
# Run from repo root. Requires pkgbuild and productbuild (Xcode command line tools).
# Usage: ./tools/build_mac_installer.sh [version]
# Example: ./tools/build_mac_installer.sh 1.6.0

set -euo pipefail
VERSION="${1:-1.6.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DCTL_SRC="$REPO_ROOT/FadedBalancerDCTL.dctl"
INSTALLERS_MAC="$REPO_ROOT/installers/mac"
PAYLOAD_ROOT="$INSTALLERS_MAC/root"
SCRIPTS_DIR="$INSTALLERS_MAC/scripts"
DIST_DIR="$INSTALLERS_MAC"
OUT_DIR="$REPO_ROOT/installers"
COMPONENT_PKG="$OUT_DIR/FadedBalancerDCTL-component.pkg"
FINAL_PKG_NAME="FadedBalancerDCTL-${VERSION}.pkg"
IDENTIFIER="com.fabiocolor.FadedBalancerDCTL"
INSTALL_LOCATION="/tmp/FadedBalancerDCTL_payload"
DIST_XML="$DIST_DIR/distribution.xml"

if [ ! -f "$DCTL_SRC" ]; then
  echo "Error: DCTL not found: $DCTL_SRC" >&2
  exit 1
fi
if [ ! -f "$SCRIPTS_DIR/postinstall" ]; then
  echo "Error: postinstall script not found: $SCRIPTS_DIR/postinstall" >&2
  exit 1
fi
if [ ! -f "$DIST_XML" ]; then
  echo "Error: distribution.xml not found: $DIST_XML" >&2
  exit 1
fi

chmod +x "$SCRIPTS_DIR/postinstall"
if [ -f "$SCRIPTS_DIR/preinstall" ]; then
  chmod +x "$SCRIPTS_DIR/preinstall"
fi
mkdir -p "$PAYLOAD_ROOT"
# Use ditto to copy without resource forks, or cp and clean up
if command -v ditto >/dev/null 2>&1; then
  ditto "$DCTL_SRC" "$PAYLOAD_ROOT/FadedBalancerDCTL.dctl"
else
  cp "$DCTL_SRC" "$PAYLOAD_ROOT/FadedBalancerDCTL.dctl"
fi
# Remove any resource fork files and extended attributes
find "$PAYLOAD_ROOT" -name "._*" -delete 2>/dev/null || true
xattr -rc "$PAYLOAD_ROOT" 2>/dev/null || true
# Also clean scripts directory
find "$SCRIPTS_DIR" -name "._*" -delete 2>/dev/null || true
xattr -rc "$SCRIPTS_DIR" 2>/dev/null || true
mkdir -p "$OUT_DIR"

# Build component package
echo "Building component package..."
pkgbuild \
  --root "$PAYLOAD_ROOT" \
  --install-location "$INSTALL_LOCATION" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --scripts "$SCRIPTS_DIR" \
  "$COMPONENT_PKG"

# Update distribution.xml with correct version and package name
# Only update version in pkg-ref, not in XML declaration
sed -i '' "s/<pkg-ref id=\"com.fabiocolor.FadedBalancerDCTL\" version=\"[^\"]*\"/<pkg-ref id=\"com.fabiocolor.FadedBalancerDCTL\" version=\"${VERSION}\"/g" "$DIST_XML"
sed -i '' "s/FadedBalancerDCTL.pkg/FadedBalancerDCTL-component.pkg/g" "$DIST_XML"

# Build distribution package
echo "Building distribution package..."
productbuild \
  --distribution "$DIST_XML" \
  --package-path "$OUT_DIR" \
  --resources "$DIST_DIR" \
  "$OUT_DIR/$FINAL_PKG_NAME"

# Clean up
rm -rf "$PAYLOAD_ROOT"
rm -f "$COMPONENT_PKG"
echo "Built: $OUT_DIR/$FINAL_PKG_NAME"
