from __future__ import annotations

from collections.abc import Sequence

from PIL import Image


def to_gray(img: Image.Image) -> Image.Image:
    """画像をグレースケールに変換する。

    cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) 相当。

    Args:
        img: 入力画像。

    Returns:
        グレースケールの新しい PIL.Image（mode='L'）。
    """
    return img.convert("L")


def bgr2rgb(img: Image.Image) -> Image.Image:
    """R チャンネルと B チャンネルを入れ替える。

    BGR として扱われている PIL.Image を RGB に、または RGB を BGR に変換する。
    B↔R の入れ替えは対称なので rgb2bgr と同一の演算。

    cv2.cvtColor(src, cv2.COLOR_BGR2RGB) 相当。

    Args:
        img: 入力画像（mode='RGB'）。

    Returns:
        R と B を入れ替えた新しい PIL.Image（mode='RGB'）。

    Raises:
        ValueError: img.mode が 'RGB' でない場合。
    """
    if img.mode != "RGB":
        raise ValueError(f"img.mode must be 'RGB', got {img.mode!r}")
    r, g, b = img.split()
    return Image.merge("RGB", (b, g, r))


rgb2bgr = bgr2rgb


def split(img: Image.Image) -> tuple[Image.Image, ...]:
    """画像をチャンネルごとに分離する。

    cv2.split(img) 相当。各チャンネルは mode='L' の PIL.Image として返される。

    Args:
        img: 入力画像。

    Returns:
        チャンネルごとの PIL.Image のタプル。
        RGB → (R, G, B)、RGBA → (R, G, B, A)、L → (L,)。
    """
    return img.split()


def merge(channels: Sequence[Image.Image], mode: str = "RGB") -> Image.Image:
    """チャンネル画像を合成して1枚の画像を生成する。

    cv2.merge(channels) 相当。split() の逆演算。

    Args:
        channels: チャンネルごとの PIL.Image のシーケンス（各 mode='L'）。
        mode: 出力画像のモード（デフォルト 'RGB'）。

    Returns:
        合成された新しい PIL.Image。

    Raises:
        ValueError: channels の数が mode のチャンネル数と一致しない場合。
    """
    expected = len(Image.new(mode, (1, 1)).split())
    if len(channels) != expected:
        raise ValueError(
            f"mode '{mode}' requires {expected} channel(s), got {len(channels)}"
        )
    return Image.merge(mode, channels)
