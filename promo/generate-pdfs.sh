#!/usr/bin/env bash
# generate-pdfs.sh — Regenerate promo PDFs from HTML sources
#
# Usage: ./generate-pdfs.sh

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

for html in "$DIR"/*.html; do
    basename="$(basename "$html")"
    # Skip the web-facing index.html
    [ "$basename" = "index.html" ] && continue
    name="${basename%.html}"
    pdf="$DIR/${name}.pdf"
    echo "Generating ${name}.pdf ..."
    weasyprint "file://${html}" "$pdf"
done

echo "Done."
