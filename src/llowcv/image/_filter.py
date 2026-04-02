import warnings

from PIL import Image, ImageEnhance, ImageFilter

from llowcv._config import config


def blur(img: Image.Image, ksize: tuple[int, int], silent: bool = False) -> Image.Image:
    """画像をぼかす（ボックスブラー）。

    Args:
        img: 入力画像。
        ksize: カーネルサイズ (width, height)。cv2.blur 準拠。
            各要素は 1 以上の整数。
        silent: True の場合、no-op 警告を抑制する。

    Returns:
        ぼかされた新しい PIL.Image。

    Raises:
        ValueError: ksize の要素が 0 以下の場合。
    """
    w, h = ksize
    if w <= 0 or h <= 0:
        raise ValueError(f"ksize elements must be > 0, got {ksize!r}")
    rx, ry = w // 2, h // 2
    if rx == 0 and ry == 0 and config.warn_noop and not silent:
        warnings.warn(
            f"ksize={ksize!r} results in no blurring (radius=(0, 0)). "
            "Use ksize >= (3, 3) for a visible effect.",
            UserWarning,
            stacklevel=2,
        )
    return img.filter(ImageFilter.BoxBlur((rx, ry)))


def sharpen(img: Image.Image, amount: float = 1.0) -> Image.Image:
    """画像をシャープにする。

    Args:
        img: 入力画像。
        amount: シャープネスの強度。1.0 が標準、0.0 でぼかし、2.0 で強くシャープ。

    Returns:
        シャープ化された新しい PIL.Image。
    """
    return ImageEnhance.Sharpness(img).enhance(amount)
