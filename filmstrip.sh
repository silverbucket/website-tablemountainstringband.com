#!/usr/bin/env bash
# filmstrip.sh — Manage photos in the horizontal filmstrip on index.html
#
# Usage:
#   ./filmstrip.sh add <source-image> <alt-text>
#   ./filmstrip.sh remove <name>
#   ./filmstrip.sh list
#
# Examples:
#   ./filmstrip.sh add ~/Photos/concert.jpg "Nick playing banjo at Kaštán"
#   ./filmstrip.sh remove gallery-park-03
#   ./filmstrip.sh list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHOTO_DIR="$SCRIPT_DIR/res/photos"
INDEX="$SCRIPT_DIR/index.html"
FILMSTRIP_WIDTH=1400
THUMB_QUALITY=80

die() { echo "Error: $1" >&2; exit 1; }

# --- LIST ---
cmd_list() {
    echo "Current filmstrip photos:"
    echo "========================="
    # Extract photo-scroll-item entries
    perl -ne 'while (/(gallery-[a-z0-9-]+)\.jpg" alt="([^"]*)/g) { print "  $1  —  \"$2\"\n" }' "$INDEX" \
        | grep -v "thumb" | head -20
}

# --- ADD ---
cmd_add() {
    local src="$1"
    local alt="$2"

    [ -f "$src" ] || die "File not found: $src"

    # Generate a name from the filename
    local basename
    basename="$(basename "$src" | sed 's/\.[^.]*$//' | tr '[:upper:]' '[:lower:]' | tr ' _' '-' | sed 's/[^a-z0-9-]//g')"
    local name="gallery-${basename}"

    # Check for collision
    if [ -f "$PHOTO_DIR/${name}.jpg" ]; then
        echo "Photo $name already exists. Overwrite? [y/N]"
        read -r answer
        [[ "$answer" =~ ^[Yy] ]] || exit 0
    fi

    echo "Processing $src → $name ..."

    # Convert/resize to jpg for filmstrip
    sips -s format jpeg --resampleWidth "$FILMSTRIP_WIDTH" "$src" --out "$PHOTO_DIR/${name}.jpg" >/dev/null 2>&1
    echo "  Created ${name}.jpg (${FILMSTRIP_WIDTH}px wide)"

    # Create webp version
    if command -v cwebp &>/dev/null; then
        cwebp -q "$THUMB_QUALITY" "$PHOTO_DIR/${name}.jpg" -o "$PHOTO_DIR/${name}.webp" >/dev/null 2>&1
        echo "  Created ${name}.webp"
    else
        echo "  Warning: cwebp not found, skipping webp generation"
    fi

    # Build the HTML snippet
    local snippet
    snippet="                <div class=\"photo-scroll-item\">\n                    <picture><source srcset=\"res/photos/${name}.webp\" type=\"image/webp\" /><img src=\"res/photos/${name}.jpg\" alt=\"${alt}\" loading=\"lazy\" /></picture>\n                </div>"

    # Insert before the closing </div> of the photo-scroll container
    # Find the last photo-scroll-item and add after it
    if grep -q "photo-scroll-item" "$INDEX"; then
        # Use perl for reliable multiline insertion (insert before the closing </div> after last scroll item)
        perl -i -0pe "s|(.*class=\"photo-scroll-item\">.*?</div>)|\\1\n${snippet}|s" "$INDEX"
        echo "  Added to filmstrip in index.html"
    else
        die "Could not find photo-scroll section in index.html"
    fi

    echo "Done! Added $name to the filmstrip."
}

# --- REMOVE ---
cmd_remove() {
    local name="$1"

    # Strip .jpg/.webp extension if provided
    name="${name%.jpg}"
    name="${name%.webp}"

    # Check it exists in index.html
    if ! grep -q "${name}" "$INDEX"; then
        die "$name not found in filmstrip"
    fi

    echo "Removing $name from filmstrip..."

    # Remove the HTML block (the photo-scroll-item div containing this name)
    perl -i -0pe "s|\s*<div class=\"photo-scroll-item\">\s*<picture>.*?${name}.*?</picture>\s*</div>||s" "$INDEX"
    echo "  Removed from index.html"

    # Remove image files
    for ext in jpg webp; do
        if [ -f "$PHOTO_DIR/${name}.${ext}" ]; then
            rm "$PHOTO_DIR/${name}.${ext}"
            echo "  Deleted ${name}.${ext}"
        fi
    done

    echo "Done! Removed $name."
}

# --- MAIN ---
case "${1:-}" in
    add)
        [ $# -ge 3 ] || die "Usage: $0 add <source-image> <alt-text>"
        cmd_add "$2" "$3"
        ;;
    remove|rm)
        [ $# -ge 2 ] || die "Usage: $0 remove <name>"
        cmd_remove "$2"
        ;;
    list|ls)
        cmd_list
        ;;
    *)
        echo "Usage: $0 {add|remove|list}"
        echo ""
        echo "  add <source-image> <alt-text>   Add a photo to the filmstrip"
        echo "  remove <name>                   Remove a photo (e.g. gallery-park-03)"
        echo "  list                            Show current filmstrip photos"
        exit 1
        ;;
esac
