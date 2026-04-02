"""NumPy / OpenCV 変換 API のテスト。"""

import pytest
from PIL import Image

import llowcv as lcv

numpy = pytest.importorskip("numpy")


class TestAsNumpy:
    def test_returns_ndarray(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_numpy(rgb_image)
        assert isinstance(arr, numpy.ndarray)

    def test_shape(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_numpy(rgb_image)
        assert arr.shape == (rgb_image.height, rgb_image.width, 3)

    def test_dtype(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_numpy(rgb_image)
        assert arr.dtype == numpy.uint8

    def test_rgb_channel_order(self, rgb_image: Image.Image) -> None:
        """左上ピクセルが赤（255,0,0）であることを確認。"""
        arr = lcv.as_numpy(rgb_image)
        assert arr[64, 64, 0] == 255  # R
        assert arr[64, 64, 1] == 0  # G
        assert arr[64, 64, 2] == 0  # B


class TestToBgr:
    def test_channel_order_reversed(self, rgb_image: Image.Image) -> None:
        """RGB の赤ピクセルが BGR では B=0, G=0, R=255 になる。"""
        arr = lcv.as_numpy(rgb_image)
        bgr = lcv.to_bgr(arr)
        assert bgr[64, 64, 0] == 0  # B
        assert bgr[64, 64, 1] == 0  # G
        assert bgr[64, 64, 2] == 255  # R (元の R が末尾へ)

    def test_returns_new_array(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_numpy(rgb_image)
        bgr = lcv.to_bgr(arr)
        assert bgr is not arr

    def test_shape_preserved(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_numpy(rgb_image)
        bgr = lcv.to_bgr(arr)
        assert bgr.shape == arr.shape


class TestAsCv2:
    def test_returns_ndarray(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_cv2(rgb_image)
        assert isinstance(arr, numpy.ndarray)

    def test_bgr_channel_order(self, rgb_image: Image.Image) -> None:
        """左上ピクセルが赤 → BGR では (0, 0, 255)。"""
        arr = lcv.as_cv2(rgb_image)
        assert arr[64, 64, 0] == 0  # B
        assert arr[64, 64, 1] == 0  # G
        assert arr[64, 64, 2] == 255  # R

    def test_shape(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_cv2(rgb_image)
        assert arr.shape == (rgb_image.height, rgb_image.width, 3)


class TestFromCv2:
    def test_returns_pil_image(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_cv2(rgb_image)
        out = lcv.from_cv2(arr)
        assert isinstance(out, Image.Image)

    def test_mode_is_rgb(self, rgb_image: Image.Image) -> None:
        arr = lcv.as_cv2(rgb_image)
        out = lcv.from_cv2(arr)
        assert out.mode == "RGB"

    def test_roundtrip(self, rgb_image: Image.Image) -> None:
        """PIL → cv2 → PIL で元の画像に戻る。"""
        arr = lcv.as_cv2(rgb_image)
        recovered = lcv.from_cv2(arr)
        assert recovered.size == rgb_image.size
        assert recovered.tobytes() == rgb_image.tobytes()
