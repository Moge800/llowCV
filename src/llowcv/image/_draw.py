from PIL import Image, ImageDraw, ImageFont


def put_text(
    img: Image.Image,
    text: str,
    org: tuple[int, int],
    font: str,
    size: int,
    color: tuple[int, int, int],
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
