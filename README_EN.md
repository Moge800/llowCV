# llowCV

[日本語](https://github.com/llowcv/llowcv/blob/main/README.md)

**A lightweight, cv2-like image processing library powered by Pillow.**

OpenCV + NumPy is too heavy for edge devices and PyInstaller executables.
llowCV uses only Pillow as its core dependency and mirrors cv2's API names, argument order, and coordinate system — minimizing migration cost.

```python
import llowcv as lcv

img = lcv.imread("input.jpg")
img = lcv.resize(img, (640, 480))
img = lcv.put_text(img, "Hello World", (10, 30), font="Arial.ttf", size=24, color=(255, 255, 255))
lcv.imwrite("out.jpg", img)
```

## Why llowCV?

| | OpenCV | llowCV |
|---|:---:|:---:|
| Core dependency | OpenCV + NumPy | **Pillow only** |
| Install size | ~100 MB | ~10 MB |
| PyInstaller exe | Painful | Easy |
| Raspberry Pi / Edge | Heavy | Lightweight |
| cv2-compatible API | — | ✅ |
| Unicode text rendering | Requires config | Just pass a TTF path |
| Real-time / Video | ✅ | Out of scope |

## Installation

```bash
pip install llowcv
```

For Matplotlib display support:

```bash
pip install llowcv[mpl]
```

For NumPy / OpenCV interop:

```bash
pip install llowcv[cv2]
```

## Color Formats

llowCV uses **RGB as its internal format** — the opposite of cv2's BGR.

| mode | Use case | Channel order |
|---|---|---|
| `"RGB"` | Color image (default) | R, G, B |
| `"RGBA"` | Color with transparency | R, G, B, A |
| `"L"` | Grayscale | Luminance only |

```python
img = lcv.imread("input.jpg")               # → mode='RGB'
img = lcv.imread("input.png", mode="RGBA")  # → mode='RGBA' (transparency preserved)
img = lcv.imread("input.jpg", mode="L")     # → mode='L'   (grayscale)
```

**BGR and BGRA are not directly supported.** Use the interop API to exchange data with cv2:

```python
# cv2 (BGR ndarray) → llowcv (RGB PIL.Image)
img = lcv.from_cv2(cv2_bgr_array)   # BGR → RGB conversion happens automatically

# llowcv (RGB PIL.Image) → cv2 (BGR ndarray)
arr = lcv.as_cv2(img)               # RGB → BGR conversion happens automatically
```

`alpha_composite` requires both images to be `mode='RGBA'`.
`blend` and `composite` expect `mode='RGB'`.

### Channel operations

```python
# Swap R and B channels (fix a BGR-ordered PIL.Image, or convert back)
img = lcv.bgr2rgb(img)    # equivalent to cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = lcv.rgb2bgr(img)    # same operation (alias)

# Split and merge channels
r, g, b = lcv.split(img)                   # like cv2.split — each channel is mode='L'
img      = lcv.merge([r, g, b])            # like cv2.merge
img      = lcv.merge([r, g, b, a], mode="RGBA")  # works for RGBA too

# Extract a single channel
r_channel = lcv.split(img)[0]              # R channel only, mode='L'
```

## API Reference

### Image I/O

```python
img = lcv.imread("input.jpg")               # Read as RGB
img = lcv.imread("input.jpg", mode="L")     # Read as grayscale
lcv.imwrite("out.png", img)                 # Format inferred from extension
lcv.imshow(img)                             # Open with OS default viewer
lcv.imshow(img, backend="mpl")              # Display via Matplotlib (pip install llowcv[mpl])
lcv.imshow(img, backend="mpl", block=False) # Non-blocking display (mpl only)
```

### Transforms

```python
img = lcv.resize(img, (640, 480))                              # Resize
img = lcv.resize(img, (640, 480), interpolation="cubic")       # With interpolation
img = lcv.resize(img, img.size, silent=True)                   # Suppress same-size warning
img = lcv.crop(img, (x, y, w, h))                              # Crop (cv2-style xywh)
img = lcv.rotate(img, 90)                                      # Rotate counter-clockwise
img = lcv.rotate(img, 45, expand=True)                         # Expand canvas to fit
img = lcv.flip(img, 0)                                         # Flip vertical
img = lcv.flip(img, 1)                                         # Flip horizontal
img = lcv.flip(img, -1)                                        # Flip both axes
```

Interpolation options: `"nearest"` / `"linear"` (default) / `"bilinear"` / `"cubic"` / `"bicubic"` / `"lanczos"`

### Filters & Color

```python
img = lcv.blur(img, (5, 5))               # Box blur
img = lcv.blur(img, (1, 1))               # radius=0 — no-op, raises UserWarning
img = lcv.blur(img, (1, 1), silent=True)  # Suppress the warning
img = lcv.sharpen(img, amount=1.5)        # Sharpen (1.0 = no change)
img = lcv.to_gray(img)                    # Convert to grayscale (mode='L')
```

### Text Drawing

```python
img = lcv.put_text(
    img,
    text="Hello, World!",
    org=(10, 40),              # Bottom-left origin (cv2-compatible)
    font="path/to/font.ttf",
    size=32,
    color=(255, 255, 255),
)
```

`org` uses the same **bottom-left origin** as `cv2.putText`.
`font` accepts any TTF or OTF file path — Unicode text (CJK, emoji, etc.) works out of the box.

### Compositing

```python
out = lcv.blend(img1, img2, alpha=0.5)        # Alpha blend (0.0=img1, 1.0=img2)
out = lcv.composite(img1, img2, mask)          # Mask composite (mask=0→img1, 255→img2)
out = lcv.alpha_composite(dst, src)            # RGBA alpha compositing
```

### NumPy / OpenCV Interop (opt-in)

Available after `pip install llowcv[cv2]`:

```python
arr = lcv.as_cv2(img)    # PIL.Image (RGB) → ndarray (BGR)
img = lcv.from_cv2(arr)  # ndarray (BGR) → PIL.Image (RGB)
arr = lcv.as_numpy(img)  # PIL.Image → RGB ndarray
arr = lcv.to_bgr(arr)    # RGB ndarray → BGR ndarray
```

### Camera

```python
with lcv.Camera(index=0) as cam:
    frame = cam.capture()          # Returns PIL.Image (RGB)
    lcv.imwrite("frame.jpg", frame)
```

Uses Windows Media Foundation on Windows and v4l2 on Linux.

### Global Configuration

```python
# Suppress all no-op warnings at once
lcv.config.warn_noop = False

# Or control via environment variable (0 / false / no / off to disable)
# LLOWCV_WARN_NOOP=0 python main.py
```

When `warn_noop` is enabled, a `UserWarning` is raised for:
- `resize`: `dsize` matches the input image size
- `blur`: `ksize` results in no blurring (e.g. `(1, 1)`)
- `imshow`: `block=False` used with the `pillow` backend

## Design Principles

- **Pillow-only core** — NumPy and OpenCV are strictly opt-in
- **Immutable returns** — every API returns a new `PIL.Image`; no in-place mutation, no thread-safety concerns
- **cv2-compatible API** — same names, argument order, and coordinate conventions as OpenCV
- **No Video / GUI / ML** — for real-time processing, use OpenCV

## Migrating from cv2

```python
# Before (cv2)
import cv2
img = cv2.imread("input.jpg")
img = cv2.resize(img, (640, 480))
cv2.imwrite("out.jpg", img)

# After (llowcv)
import llowcv as lcv
img = lcv.imread("input.jpg")
img = lcv.resize(img, (640, 480))
lcv.imwrite("out.jpg", img)
```

Key differences:

| | cv2 | llowcv |
|---|---|---|
| Image type | `numpy.ndarray` (BGR) | `PIL.Image` (RGB) |
| In-place ops | Common | None — always returns new image |
| `waitKey` / GUI loop | Required | Not needed |

## Requirements

- Python >= 3.10
- Pillow (core)
- matplotlib (`[mpl]` optional)
- numpy + opencv-python (`[cv2]` optional)
- numpy + opencv-python (`[cv2]` extra, optional)

## License

MIT License
