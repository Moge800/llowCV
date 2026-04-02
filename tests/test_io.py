"""imread / imwrite / imshow のテスト。"""

import pathlib
from unittest.mock import patch

import pytest
from PIL import Image

import llowcv as lcv


class TestImread:
    def test_returns_rgb(self, sample_jpg: str) -> None:
        img = lcv.imread(sample_jpg)
        assert img.mode == "RGB"

    def test_size_preserved(self, sample_jpg: str, rgb_image: Image.Image) -> None:
        img = lcv.imread(sample_jpg)
        assert img.size == rgb_image.size

    def test_grayscale_mode(self, sample_jpg: str) -> None:
        img = lcv.imread(sample_jpg, mode="L")
        assert img.mode == "L"

    def test_rgba_mode(self, tmp_png: str, rgb_image: Image.Image) -> None:
        rgb_image.save(tmp_png)
        img = lcv.imread(tmp_png, mode="RGBA")
        assert img.mode == "RGBA"

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            lcv.imread("nonexistent_file.jpg")

    def test_invalid_format(self, tmp_path: pathlib.Path) -> None:
        p = str(tmp_path / "bad.xyz")
        with open(p, "wb") as f:
            f.write(b"not an image")
        with pytest.raises(ValueError):
            lcv.imread(p)

    def test_returns_new_object(self, sample_jpg: str) -> None:
        img1 = lcv.imread(sample_jpg)
        img2 = lcv.imread(sample_jpg)
        assert img1 is not img2


class TestImwrite:
    def test_roundtrip_jpg(self, rgb_image: Image.Image, tmp_jpg: str) -> None:
        lcv.imwrite(tmp_jpg, rgb_image)
        reloaded = lcv.imread(tmp_jpg)
        assert reloaded.mode == "RGB"
        assert reloaded.size == rgb_image.size

    def test_roundtrip_png(self, rgb_image: Image.Image, tmp_png: str) -> None:
        lcv.imwrite(tmp_png, rgb_image)
        reloaded = lcv.imread(tmp_png)
        assert reloaded.mode == "RGB"
        assert reloaded.size == rgb_image.size

    def test_invalid_extension(
        self, rgb_image: Image.Image, tmp_path: pathlib.Path
    ) -> None:
        p = str(tmp_path / "out.xyz")
        with pytest.raises(ValueError):
            lcv.imwrite(p, rgb_image)

    def test_returns_none(self, rgb_image: Image.Image, tmp_jpg: str) -> None:
        result = lcv.imwrite(tmp_jpg, rgb_image)
        assert result is None


class TestImshow:
    def test_returns_none_pillow(self, rgb_image: Image.Image) -> None:
        with patch.object(rgb_image.__class__, "show", return_value=None):
            result = lcv.imshow(rgb_image, backend="pillow")
        assert result is None

    def test_returns_none_default(self, rgb_image: Image.Image) -> None:
        with patch.object(rgb_image.__class__, "show", return_value=None):
            result = lcv.imshow(rgb_image, backend=None)
        assert result is None

    def test_mpl_backend(self, rgb_image: Image.Image) -> None:
        plt = pytest.importorskip("matplotlib.pyplot")
        with patch.object(plt, "show", return_value=None):
            result = lcv.imshow(rgb_image, backend="mpl")
        assert result is None
        plt.close("all")

    def test_block_false_on_pillow_warns(self, rgb_image: Image.Image) -> None:
        with patch.object(rgb_image.__class__, "show", return_value=None):
            with pytest.warns(UserWarning, match="no effect"):
                lcv.imshow(rgb_image, backend="pillow", block=False)

    def test_invalid_backend(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.imshow(rgb_image, backend="unknown")
