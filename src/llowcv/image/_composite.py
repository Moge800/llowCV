from PIL import Image


def blend(img1: Image.Image, img2: Image.Image, alpha: float) -> Image.Image:
    """2枚の画像をアルファブレンドする。

    cv2.addWeighted(img1, 1-alpha, img2, alpha, 0) 相当。

    Args:
        img1: ブレンド元画像。
        img2: ブレンド先画像。
        alpha: ブレンド係数。0.0 = img1、1.0 = img2。

    Returns:
        ブレンドされた新しい PIL.Image。

    Raises:
        ValueError: alpha が 0.0〜1.0 の範囲外の場合。
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be between 0.0 and 1.0, got {alpha!r}")
    return Image.blend(img1, img2, alpha)


def composite(
    img1: Image.Image,
    img2: Image.Image,
    mask: Image.Image,
) -> Image.Image:
    """マスクを使って2枚の画像を合成する。

    Args:
        img1: マスク値 0 の領域に使われる画像（背景）。
        img2: マスク値 255 の領域に使われる画像（前景）。
        mask: 合成マスク（mode='L' のグレースケール画像）。

    Returns:
        合成された新しい PIL.Image。
    """
    # Pillow の Image.composite(a, b, mask) は mask=255 で a が出る仕様のため
    # cv2 ライクな「mask=255 → img2」にするために引数を入れ替える
    return Image.composite(img2, img1, mask)


def alpha_composite(dst: Image.Image, src: Image.Image) -> Image.Image:
    """アルファチャンネルを使って画像を合成する。

    Args:
        dst: 背景画像（mode='RGBA'）。
        src: 前景画像（mode='RGBA'）。dst の上に合成される。

    Returns:
        合成された新しい PIL.Image（mode='RGBA'）。

    Raises:
        ValueError: dst または src の mode が 'RGBA' でない場合。
    """
    if dst.mode != "RGBA":
        raise ValueError(f"dst.mode must be 'RGBA', got {dst.mode!r}")
    if src.mode != "RGBA":
        raise ValueError(f"src.mode must be 'RGBA', got {src.mode!r}")
    return Image.alpha_composite(dst, src)
