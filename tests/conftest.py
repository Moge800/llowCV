"""pytest 共通フィクスチャ。

テスト画像はすべてプログラムで生成する（ネット不要・ライセンス問題なし）。
4色クワドラント画像を基本とし、flip / crop / rotate の検証に使いやすい構成にしている。
"""

import pathlib

import pytest
from PIL import Image, ImageDraw


@pytest.fixture()
def rgb_image() -> Image.Image:
    """256x256 の 4色クワドラント RGB 画像。

    左上=赤  右上=緑
    左下=青  右下=黄
    """
    img = Image.new("RGB", (256, 256))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 127, 127), fill=(255, 0, 0))  # 左上: 赤
    draw.rectangle((128, 0, 255, 127), fill=(0, 255, 0))  # 右上: 緑
    draw.rectangle((0, 128, 127, 255), fill=(0, 0, 255))  # 左下: 青
    draw.rectangle((128, 128, 255, 255), fill=(255, 255, 0))  # 右下: 黄
    return img


@pytest.fixture()
def gray_image() -> Image.Image:
    """256x256 のグレースケール画像（左から右へグラデーション）。"""
    img = Image.new("L", (256, 256))
    for x in range(256):
        for y in range(256):
            img.putpixel((x, y), x)
    return img


@pytest.fixture()
def rgba_image() -> Image.Image:
    """128x128 の RGBA 画像（半透明赤）。"""
    img = Image.new("RGBA", (128, 128), (255, 0, 0, 128))
    return img


@pytest.fixture()
def tmp_jpg(tmp_path: pathlib.Path) -> str:
    """書き出し用の一時 JPEG パス。"""
    return str(tmp_path / "out.jpg")


@pytest.fixture()
def tmp_png(tmp_path: pathlib.Path) -> str:
    """書き出し用の一時 PNG パス。"""
    return str(tmp_path / "out.png")


@pytest.fixture()
def sample_jpg(tmp_path: pathlib.Path, rgb_image: Image.Image) -> str:
    """RGB 画像を JPEG として保存したパスを返す。"""
    path = str(tmp_path / "sample.jpg")
    rgb_image.save(path)
    return path
