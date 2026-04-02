from PIL import Image, ImageEnhance, ImageFilter


def blur(img: Image.Image, ksize: tuple[int, int]) -> Image.Image:
    """画像をぼかす（ボックスブラー）。

    Args:
        img: 入力画像。
        ksize: カーネルサイズ (width, height)。cv2.blur 準拠。
            各要素は 1 以上の整数。

    Returns:
        ぼかされた新しい PIL.Image。

    Raises:
        ValueError: ksize の要素が 0 以下の場合。
    """
    w, h = ksize
    if w <= 0 or h <= 0:
        raise ValueError(f"ksize elements must be > 0, got {ksize!r}")
    return img.filter(ImageFilter.BoxBlur((w // 2, h // 2)))


def sharpen(img: Image.Image, amount: float = 1.0) -> Image.Image:
    """画像をシャープにする。

    Args:
        img: 入力画像。
        amount: シャープネスの強度。1.0 が標準、0.0 でぼかし、2.0 で強くシャープ。

    Returns:
        シャープ化された新しい PIL.Image。
    """
    return ImageEnhance.Sharpness(img).enhance(amount)
