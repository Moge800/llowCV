from PIL import Image

_INTERPOLATION = {
    "nearest": Image.Resampling.NEAREST,
    "linear": Image.Resampling.BILINEAR,
    "bilinear": Image.Resampling.BILINEAR,
    "cubic": Image.Resampling.BICUBIC,
    "bicubic": Image.Resampling.BICUBIC,
    "lanczos": Image.Resampling.LANCZOS,
}


def resize(
    img: Image.Image,
    dsize: tuple[int, int],
    interpolation: str = "linear",
) -> Image.Image:
    """画像をリサイズする。

    Args:
        img: 入力画像。
        dsize: 出力サイズ (width, height)。
        interpolation: 補間方法。'nearest' / 'linear' / 'bilinear' /
            'cubic' / 'bicubic' / 'lanczos'。デフォルトは 'linear'。

    Returns:
        リサイズされた新しい PIL.Image。

    Raises:
        ValueError: 不明な interpolation が指定された場合。
    """
    resample = _INTERPOLATION.get(interpolation)
    if resample is None:
        raise ValueError(f"Unknown interpolation: {interpolation!r}")
    return img.resize(dsize, resample=resample)


def crop(img: Image.Image, rect: tuple[int, int, int, int]) -> Image.Image:
    """画像を切り抜く。

    Args:
        img: 入力画像。
        rect: 切り抜き領域 (x, y, w, h)。左上座標 + 幅・高さ。

    Returns:
        切り抜かれた新しい PIL.Image。
    """
    x, y, w, h = rect
    return img.crop((x, y, x + w, y + h))


def rotate(
    img: Image.Image,
    angle: float,
    expand: bool = False,
    center: tuple[int, int] | None = None,
) -> Image.Image:
    """画像を回転する。

    Args:
        img: 入力画像。
        angle: 回転角度（度）。正の値で反時計回り（cv2 準拠）。
        expand: True の場合、回転後の全体が収まるよう出力サイズを拡張する。
        center: 回転中心ピクセル座標。None で画像中心。

    Returns:
        回転された新しい PIL.Image。
    """
    return img.rotate(angle, expand=expand, center=center)


def flip(img: Image.Image, flipCode: int) -> Image.Image:
    """画像を反転する。

    Args:
        img: 入力画像。
        flipCode: 反転方向。0=上下、1=左右、-1=上下+左右。cv2.flip 完全互換。

    Returns:
        反転された新しい PIL.Image。

    Raises:
        ValueError: flipCode が 0 / 1 / -1 以外の場合。
    """
    if flipCode == 0:
        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    elif flipCode == 1:
        return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif flipCode == -1:
        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM).transpose(
            Image.Transpose.FLIP_LEFT_RIGHT
        )
    raise ValueError(f"Invalid flipCode: {flipCode!r}. Must be 0, 1, or -1.")
