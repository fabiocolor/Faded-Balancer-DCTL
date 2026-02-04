#!/usr/bin/env bash
# Build macOS installer .pkg for Faded Balancer DCTL (single package: run to install, run again to uninstall).
# Run from repo root. Requires pkgbuild (Xcode command line tools).
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
OUT_DIR="$REPO_ROOT/installers"
PKG_NAME="FadedBalancerDCTL-${VERSION}.pkg"
IDENTIFIER="com.fabiocolor.FadedBalancerDCTL"
INSTALL_LOCATION="/tmp/FadedBalancerDCTL_payload"

if [ ! -f "$DCTL_SRC" ]; then
  echo "Error: DCTL not found: $DCTL_SRC" >&2
  exit 1
fi
if [ ! -f "$SCRIPTS_DIR/postinstall" ]; then
  echo "Error: postinstall script not found: $SCRIPTS_DIR/postinstall" >&2
  exit 1
fi

chmod +x "$SCRIPTS_DIR/postinstall"
mkdir -p "$PAYLOAD_ROOT"
cp "$DCTL_SRC" "$PAYLOAD_ROOT/FadedBalancerDCTL.dctl"
mkdir -p "$OUT_DIR"

pkgbuild \
  --root "$PAYLOAD_ROOT" \
  --install-location "$INSTALL_LOCATION" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --scripts "$SCRIPTS_DIR" \
  "$OUT_DIR/$PKG_NAME"

rm -rf "$PAYLOAD_ROOT"
echo "Built: $OUT_DIR/$PKG_NAME"
