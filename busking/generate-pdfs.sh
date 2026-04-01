#!/usr/bin/env bash
# generate-pdfs.sh — Regenerate busking sign PDFs from HTML sources
#
# Usage: ./generate-pdfs.sh

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

for html in "$DIR"/*.html; do
    name="$(basename "$html" .html)"
    pdf="$DIR/${name}.pdf"
    echo "Generating ${name}.pdf ..."
    weasyprint "file://${html}" "$pdf"
done

echo "Done."
