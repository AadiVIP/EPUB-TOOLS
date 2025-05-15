#!/usr/bin/env bash

TITLE="The Weakest Link Book One"
AUTHOR="D. Dillon"
PUBLISHER="No Headphone Gamerz"
OUT="The Weakest Link Book One.epub"

# clean up any leftovers
rm -f temp_ch*.md "$OUT"

for i in $(seq -w 1 21); do
  FILE="ch${i}.docx"
  RAW="raw${i}.md"
  BODY="body${i}.md"

  # 1) convert to markdown
  pandoc "$FILE" -t markdown -o "$RAW"

  # 2) grab first non-empty line (real chapter title)
  HEAD_LINE=$(sed -n '/./{p;q;}' "$RAW")

  # 3) if it isn’t already a markdown heading, turn it into one
  if [[ "$HEAD_LINE" != \#* ]]; then
    HEAD="# $HEAD_LINE"
  else
    HEAD="$HEAD_LINE"
  fi

  # 4) strip that line out of the body
  tail -n +2 "$RAW" > "$BODY"

  # 5) write a cleaned temp file
  {
    echo "$HEAD"
    echo
    cat "$BODY"
  } > "temp_ch${i}.md"
done

# now stitch them together into one EPUB
pandoc temp_ch*.md \
  --metadata title="$TITLE" \
  --metadata author="$AUTHOR" \
  --metadata publisher="$PUBLISHER" \
  --toc \
  --split-level=1 \
  -o "$OUT"

echo "✓ EPUB ready: $OUT"
