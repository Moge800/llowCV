from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

# 色の型エイリアス（RGB または RGBA タプル）
_Color = tuple[int, int, int] | tuple[int, int, int, int]


def put_text(
    img: Image.Image,
    text: str,
    org: tuple[int, int],
    font: str,
    size: int,
    color: _Color,
) -> Image.Image:
    """画像にテキストを描画する。

    Args:
        img: 入力画像。
        text: 描画するテキスト。Unicode 対応（日本語等）。
        org: テキストの左下基準座標 (x, y)。cv2.putText 準拠。
        font: TrueType / OpenType フォントファイルのパス。
        size: フォントサイズ（px）。
        color: テキストの色（RGB タプル）。例: (255, 255, 255)。

    Returns:
        テキストが描画された新しい PIL.Image。

    Raises:
        FileNotFoundError: フォントファイルが存在しない場合。
    """
    out = img.copy()
    draw = ImageDraw.Draw(out)
    pil_font = ImageFont.truetype(font, size)
    # anchor="ls": left-baseline。cv2.putText の org（左下基準）と同じ挙動
    draw.text(org, text, font=pil_font, fill=color, anchor="ls")
    return out


def draw_rectangle(
    img: Image.Image,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: _Color,
    thickness: int = 1,
) -> Image.Image:
    """矩形を描画する。

    cv2.rectangle(img, pt1, pt2, color, thickness) 相当。

    Args:
        img: 入力画像。
        pt1: 左上頂点座標 (x, y)。
        pt2: 右下頂点座標 (x, y)。
        color: 線の色（RGB タプル）。例: (0, 255, 0)。
        thickness: 線の太さ（px）。-1 で塗りつぶし。

    Returns:
        矩形が描画された新しい PIL.Image。
    """
    out = img.copy()
    draw = ImageDraw.Draw(out)
    if thickness == -1:
        draw.rectangle([pt1, pt2], fill=color)
    else:
        draw.rectangle([pt1, pt2], outline=color, width=thickness)
    return out


def draw_circle(
    img: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: _Color,
    thickness: int = 1,
) -> Image.Image:
    """円を描画する。

    cv2.circle(img, center, radius, color, thickness) 相当。

    Args:
        img: 入力画像。
        center: 円の中心座標 (x, y)。
        radius: 半径（px）。
        color: 線の色（RGB タプル）。例: (255, 0, 0)。
        thickness: 線の太さ（px）。-1 で塗りつぶし。

    Returns:
        円が描画された新しい PIL.Image。

    Raises:
        ValueError: radius が 0 以下の場合。
    """
    if radius <= 0:
        raise ValueError(f"radius must be > 0, got {radius!r}")
    cx, cy = center
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    out = img.copy()
    draw = ImageDraw.Draw(out)
    if thickness == -1:
        draw.ellipse(bbox, fill=color)
    else:
        draw.ellipse(bbox, outline=color, width=thickness)
    return out


def draw_line(
    img: Image.Image,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: _Color,
    thickness: int = 1,
) -> Image.Image:
    """直線を描画する。

    cv2.line(img, pt1, pt2, color, thickness) 相当。

    Args:
        img: 入力画像。
        pt1: 始点座標 (x, y)。
        pt2: 終点座標 (x, y)。
        color: 線の色（RGB タプル）。例: (255, 255, 0)。
        thickness: 線の太さ（px）。

    Returns:
        直線が描画された新しい PIL.Image。
    """
    out = img.copy()
    draw = ImageDraw.Draw(out)
    draw.line([pt1, pt2], fill=color, width=thickness)
    return out
