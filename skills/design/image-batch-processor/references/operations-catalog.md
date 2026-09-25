# Operations Catalog & Platform Notes

Companion notes for `scripts/batch_process.py`. Details kept here so the
SKILL.md body stays short.

## Pipeline order

Operations always apply in this fixed order, which matters for the result:

1. **resize** (fit, keep aspect ratio)
2. **crop** (exact WxH+X+Y box)
3. **watermark** (text or image, with opacity and position)
4. **save** (compress quality and/or target format)

If you crop after watermarking you could cut the watermark off, which is why
watermark is always last.

## Resize semantics

- `--resize 1920x1080` treats the box as a maximum: the image is scaled to fit
  inside it, preserving aspect ratio, and is never upscaled beyond its source.
- `--resize 1080` sets the longest edge to 1080 and scales the other edge
  proportionally; again, never upscales.
- For exact output pixels (e.g. a strict 1080x1440 cover), resize to fit then
  `--crop` to the exact box.

## Watermark

- Position anchors with a 12px margin from the chosen edge.
- Opacity 0.1-1.0 is multiplied onto the overlay; 0.3 is a readable default.
- A text watermark uses DejaVuSans (bundled with Pillow) at `--watermark-size`.

## Format notes

- Saving as JPEG flattens alpha onto a white background; use png/webp to keep
  transparency.
- `--compress N` implies JPEG unless `--format` overrides the container.

## OCR

- `--ocr` writes a `.txt` next to each output image.
- Requires `pytesseract` plus a system `tesseract` binary; without them the run
  continues and only warns.
