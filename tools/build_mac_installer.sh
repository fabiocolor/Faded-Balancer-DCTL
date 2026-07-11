#!/usr/bin/env bash
# Build macOS installer .pkg for Faded Balancer DCTL (single package: run to install, run again to uninstall).
# Run from repo root. Requires pkgbuild and productbuild (Xcode command line tools).
# Usage: ./tools/build_mac_installer.sh [version]
# Example: ./tools/build_mac_installer.sh 1.7.0

set -euo pipefail
# Prevent macOS copyfile/resource-fork metadata from becoming AppleDouble files
# inside the package payload or build inputs.
export COPYFILE_DISABLE=1
VERSION="${1:-1.7.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DCTL_SRC="$REPO_ROOT/FadedBalancerDCTL.dctl"
INSTALLERS_MAC="$REPO_ROOT/installers/mac"
OUT_DIR="$REPO_ROOT/installers"
FINAL_PKG_NAME="FadedBalancerDCTL-${VERSION}.pkg"
IDENTIFIER="com.fabiocolor.FadedBalancerDCTL"
INSTALL_LOCATION="/tmp/FadedBalancerDCTL_payload"
DIST_TEMPLATE="$INSTALLERS_MAC/distribution.xml"
BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/FadedBalancerDCTL-build.XXXXXX")"
PAYLOAD_ROOT="$BUILD_ROOT/payload-volume"
PAYLOAD_IMAGE="$BUILD_ROOT/payload.dmg"
PAYLOAD_MOUNTED=0
SCRIPTS_DIR="$BUILD_ROOT/scripts"
RESOURCES_DIR="$BUILD_ROOT/resources"
COMPONENT_PKG="$BUILD_ROOT/FadedBalancerDCTL-component.pkg"
DIST_XML="$BUILD_ROOT/distribution.xml"

cleanup() {
  if [ "$PAYLOAD_MOUNTED" -eq 1 ]; then
    hdiutil detach -quiet "$PAYLOAD_ROOT" 2>/dev/null || true
  fi
  rm -rf "$BUILD_ROOT"
}
trap cleanup EXIT

case "$VERSION" in
  ""|*[!0-9A-Za-z.-]*)
    echo "Error: Invalid version: $VERSION" >&2
    exit 2
    ;;
esac

if [ ! -f "$DCTL_SRC" ]; then
  echo "Error: DCTL not found: $DCTL_SRC" >&2
  exit 1
fi
if [ ! -f "$INSTALLERS_MAC/scripts/postinstall" ]; then
  echo "Error: postinstall script not found: $INSTALLERS_MAC/scripts/postinstall" >&2
  exit 1
fi
if [ ! -f "$INSTALLERS_MAC/scripts/preinstall" ]; then
  echo "Error: preinstall script not found: $INSTALLERS_MAC/scripts/preinstall" >&2
  exit 1
fi
if [ ! -f "$DIST_TEMPLATE" ]; then
  echo "Error: distribution.xml not found: $DIST_TEMPLATE" >&2
  exit 1
fi
if ! command -v hdiutil >/dev/null 2>&1; then
  echo "Error: hdiutil is required to build a metadata-free payload." >&2
  exit 1
fi

mkdir -p "$PAYLOAD_ROOT" "$SCRIPTS_DIR" "$RESOURCES_DIR" "$OUT_DIR"
cp -X "$INSTALLERS_MAC/scripts/preinstall" "$SCRIPTS_DIR/preinstall"
cp -X "$INSTALLERS_MAC/scripts/postinstall" "$SCRIPTS_DIR/postinstall"
cp -X "$INSTALLERS_MAC/welcome.html" "$RESOURCES_DIR/welcome.html"
cp -X "$INSTALLERS_MAC/conclusion.html" "$RESOURCES_DIR/conclusion.html"
cp -X "$DIST_TEMPLATE" "$DIST_XML"
chmod +x "$SCRIPTS_DIR/postinstall"
if [ -f "$SCRIPTS_DIR/preinstall" ]; then
  chmod +x "$SCRIPTS_DIR/preinstall"
fi

# Build the one-file payload on a temporary FAT volume. macOS 15 can attach a
# synthetic com.apple.provenance xattr even after xattr -c; pkgbuild serializes
# that metadata as a virtual ._ file. FAT exposes it as a removable AppleDouble
# sidecar, allowing the shipped payload to contain exactly one DCTL.
hdiutil create -quiet -size 4m -fs MS-DOS -volname FADEDPAYLOAD -type UDIF "$PAYLOAD_IMAGE"
hdiutil attach -quiet -nobrowse -mountpoint "$PAYLOAD_ROOT" "$PAYLOAD_IMAGE"
PAYLOAD_MOUNTED=1

# Copy the exact repository DCTL without extended attributes/resource forks.
cp -X "$DCTL_SRC" "$PAYLOAD_ROOT/FadedBalancerDCTL.dctl"
find "$PAYLOAD_ROOT" -mindepth 1 -maxdepth 1 ! -name "FadedBalancerDCTL.dctl" -exec rm -rf {} +
if ! cmp -s "$DCTL_SRC" "$PAYLOAD_ROOT/FadedBalancerDCTL.dctl"; then
  echo "Error: staged DCTL differs from repository source." >&2
  exit 1
fi

# Clean temporary packaging inputs without mutating the repository.
find "$PAYLOAD_ROOT" -name "._*" -delete 2>/dev/null || true
xattr -rc "$PAYLOAD_ROOT" 2>/dev/null || true
find "$SCRIPTS_DIR" -name "._*" -delete 2>/dev/null || true
xattr -rc "$SCRIPTS_DIR" 2>/dev/null || true
find "$RESOURCES_DIR" -name "._*" -delete 2>/dev/null || true
xattr -rc "$RESOURCES_DIR" 2>/dev/null || true

# Build component package
echo "Building component package..."
pkgbuild \
  --root "$PAYLOAD_ROOT" \
  --install-location "$INSTALL_LOCATION" \
  --identifier "$IDENTIFIER" \
  --version "$VERSION" \
  --scripts "$SCRIPTS_DIR" \
  "$COMPONENT_PKG"

hdiutil detach -quiet "$PAYLOAD_ROOT"
PAYLOAD_MOUNTED=0

# Update the temporary distribution file, leaving the tracked template untouched.
sed -i '' "s/<pkg-ref id=\"com.fabiocolor.FadedBalancerDCTL\" version=\"[^\"]*\"/<pkg-ref id=\"com.fabiocolor.FadedBalancerDCTL\" version=\"${VERSION}\"/g" "$DIST_XML"
sed -i '' "s/FadedBalancerDCTL.pkg/FadedBalancerDCTL-component.pkg/g" "$DIST_XML"

# Build distribution package
echo "Building distribution package..."
rm -f "$OUT_DIR/$FINAL_PKG_NAME"
productbuild \
  --distribution "$DIST_XML" \
  --package-path "$BUILD_ROOT" \
  --resources "$RESOURCES_DIR" \
  "$OUT_DIR/$FINAL_PKG_NAME"

echo "Built: $OUT_DIR/$FINAL_PKG_NAME"
