#!/usr/bin/env bash
set -euo pipefail

# Create a GitHub Release for each git tag in this repo.
# Requires: GitHub CLI (gh) authenticated with access to the repo.
# Notes strategy (to avoid noisy auto-generated notes):
#   1) Prefer README section: "#### What's New in <tag>"
#   2) Else, curated notes at docs/releases/<tag>.md
#   3) Else, annotated tag message (subject + body)
#   4) Else, concise diff summary + compare link

# args
PREVIEW=0
for arg in "$@"; do
  case "$arg" in
    --preview|-n|--dry-run) PREVIEW=1 ;;
  esac
done

# Ensure we are in a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not inside a git repository." >&2
  exit 1
fi

if [ "$PREVIEW" -eq 0 ]; then
  # For creating releases, require gh
  if ! command -v gh >/dev/null 2>&1; then
    echo "Error: GitHub CLI 'gh' not found. Install from https://cli.github.com/" >&2
    exit 1
  fi
  # Verify gh can see the repo (and you are authenticated)
  if ! gh repo view >/dev/null 2>&1; then
    echo "Error: 'gh' cannot view this repo. Run 'gh auth login' and ensure 'origin' points to GitHub." >&2
    exit 1
  fi
fi

tags=$(git tag --list --sort=creatordate)

if [ -z "${tags}" ]; then
  echo "No tags found. Nothing to release."
  exit 0
fi

echo "Found tags:" >&2
echo "$tags" | sed 's/^/  - /' >&2

echo
if [ "$PREVIEW" -eq 1 ]; then
  echo "Previewing release notes for tags..." >&2
else
  echo "Creating releases (skipping if already exist)..." >&2
fi

# Obtain repo URL for compare links without requiring gh
origin_url=$(git remote get-url origin 2>/dev/null || echo "")
# Normalize to https://github.com/owner/repo
repo_url=""
if echo "$origin_url" | grep -qE '^git@github.com:'; then
  repo_url="https://github.com/$(echo "$origin_url" | sed -E 's#git@github.com:([^/]+/[^.]+)(\.git)?#\1#')"
  repo_url="https://github.com/${repo_url}"
elif echo "$origin_url" | grep -qE '^https?://github.com/'; then
  repo_url=$(echo "$origin_url" | sed -E 's#(https?://github.com/[^.]+/[^.]+)(\.git)?#\1#')
fi
if [ -z "$repo_url" ]; then
  # Fallback: try gh if available
  if command -v gh >/dev/null 2>&1; then
    repo_url=$(gh repo view --json url -q .url 2>/dev/null || echo "")
  fi
fi

# Iterate tags in order (compatible with older bash)
prev_tag=""
save_ifs="$IFS"; IFS=$'\n'
for tag in $tags; do
  [ -z "$tag" ] && continue
  release_exists=0
  if [ "$PREVIEW" -eq 0 ] && command -v gh >/dev/null 2>&1; then
    if gh release view "$tag" >/dev/null 2>&1; then
      release_exists=1
    fi
  fi

  tmpfile=$(mktemp)

  # helper: try extract notes from README's changelog
  extract_readme_notes() {
    local t="$1"
    # Match heading like: #### What's New in v1.4.0
    awk -v tag="$t" '
      BEGIN {found=0}
      /^####[[:space:]]+What\x27s New in[[:space:]]/ {
        if (index($0, tag) > 0) {found=1; next}
        else if (found==1) {exit}
      }
      /^### / { if (found==1) exit }
      { if (found==1) print }
    ' README.md
  }

  # 1) Prefer README section
  readme_notes=$(extract_readme_notes "$tag" || true)
  if [ -n "$readme_notes" ]; then
    printf "What's New in %s\n\n%s\n" "$tag" "$readme_notes" > "$tmpfile"
  elif [ -f "docs/releases/${tag}.md" ]; then
    # 2) curated notes under docs/releases/<tag>.md
    cat "docs/releases/${tag}.md" > "$tmpfile"
  else
    # 3) If annotated tag, use its subject + body
    otype=$(git for-each-ref "refs/tags/${tag}" --format='%(objecttype)' || true)
    if [ "$otype" = "tag" ]; then
      # subject/body only exist for annotated tags
      subj=$(git for-each-ref "refs/tags/${tag}" --format='%(subject)' || true)
      body=$(git for-each-ref "refs/tags/${tag}" --format='%(body)' || true)
      if [ -n "${subj}${body}" ]; then
        printf "%s\n\n%s\n" "$subj" "$body" > "$tmpfile"
      fi
    fi

    # 4) If still empty, write a concise diff summary and compare link
    if [ ! -s "$tmpfile" ]; then
      if [ -n "$prev_tag" ]; then
        # Gather brief diff stats
        diff_ns=$(git diff --name-status "${prev_tag}...${tag}" || true)
        total_changed=$(printf "%s\n" "$diff_ns" | sed '/^$/d' | wc -l | tr -d ' ')
        add_count=$(printf "%s\n" "$diff_ns" | awk '$1 ~ /^A/ {c++} END{print c+0}')
        mod_count=$(printf "%s\n" "$diff_ns" | awk '$1 ~ /^M/ {c++} END{print c+0}')
        del_count=$(printf "%s\n" "$diff_ns" | awk '$1 ~ /^D/ {c++} END{print c+0}')
        ren_count=$(printf "%s\n" "$diff_ns" | awk '$1 ~ /^R/ {c++} END{print c+0}')

        {
          echo "Changes since ${prev_tag}"
          echo
          echo "- Files changed: ${total_changed} (A:${add_count} M:${mod_count} D:${del_count} R:${ren_count})"
          echo "- Compare: ${repo_url}/compare/${prev_tag}...${tag}"
        } > "$tmpfile"
      else
        {
          echo "Initial public release"
          echo
          echo "- Tag: ${repo_url}/releases/tag/${tag}"
        } > "$tmpfile"
      fi
    fi
  fi

  # Prepare DCTL asset from the tag's content
  dctl_tmp=""
  desired_asset_name="FadedBalancerDCTL.dctl"
  # Candidates in tag history: prefer new name, fall back to old
  for candidate in "FadedBalancerDCTL.dctl" "FadedBalancerOFX.dctl"; do
    if git show "${tag}:${candidate}" >/dev/null 2>&1; then
      dtmp_dir=$(mktemp -d)
      dctl_tmp="${dtmp_dir}/${desired_asset_name}"
      if git show "${tag}:${candidate}" > "$dctl_tmp"; then
        break
      else
        rm -f "$dctl_tmp"; rmdir "$dtmp_dir" 2>/dev/null || true; dctl_tmp=""
      fi
    fi
  done

  if [ "$PREVIEW" -eq 1 ]; then
    echo "---"
    echo "Tag: $tag"
    echo "Title: $tag"
    if [ -n "$prev_tag" ]; then
      echo "Compare: ${repo_url}/compare/${prev_tag}...${tag}"
    else
      echo "Compare: (initial tag)"
    fi
    echo
    if [ -n "$dctl_tmp" ]; then
      size=$(wc -c < "$dctl_tmp" | tr -d ' ')
      echo "Asset: ${desired_asset_name} (${size} bytes)"
    else
      echo "Asset: ${desired_asset_name} (not found in tag; will skip upload)"
    fi
    echo
    echo "Notes:"
    sed 's/^/  /' "$tmpfile"
  else
    if [ $release_exists -eq 1 ]; then
      echo "[update] $tag (release exists; ensuring asset present)"
    else
      echo "[create] $tag"
      gh release create "$tag" \
        --title "$tag" \
        --notes-file "$tmpfile"
    fi

    # Upload DCTL asset if available and not already present
    if [ -n "$dctl_tmp" ]; then
      asset_list=$(gh release view "$tag" --json assets -q '.assets[].name' 2>/dev/null || true)
      if echo "$asset_list" | grep -qx "$desired_asset_name"; then
        echo "[asset] ${desired_asset_name} already attached"
      else
        echo "[asset] uploading ${desired_asset_name}"
        gh release upload "$tag" "${dctl_tmp}#${desired_asset_name}" --clobber >/dev/null
      fi
    else
      echo "[asset] ${desired_asset_name} not found at tag; skipped"
    fi

    # Cleanup: remove any other assets except the desired DCTL asset
    # Get repo nameWithOwner for gh api path
    nwo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
    # Enumerate asset IDs and delete those not matching desired name
    for asset_id in $(gh release view "$tag" --json assets -q '.assets[].id'); do
      asset_name=$(gh api -H "Accept: application/vnd.github+json" \
        repos/$nwo/releases/assets/$asset_id --jq .name 2>/dev/null || echo "")
      if [ -n "$asset_name" ] && [ "$asset_name" != "$desired_asset_name" ]; then
        echo "[asset] deleting stray asset: $asset_name"
        gh api -X DELETE -H "Accept: application/vnd.github+json" \
          repos/$nwo/releases/assets/$asset_id >/dev/null || true
      fi
    done
  fi

  rm -f "$tmpfile"
  if [ -n "$dctl_tmp" ]; then
    ddir=$(dirname "$dctl_tmp")
    rm -f "$dctl_tmp"; rmdir "$ddir" 2>/dev/null || true
  fi
  prev_tag="$tag"
done
IFS="$save_ifs"

echo "Done."
