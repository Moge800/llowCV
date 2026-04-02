"""画像変換・フィルタ・描画・合成 API のテスト。"""

import pytest
from PIL import Image

import llowcv as lcv


class TestResize:
    def test_output_size(self, rgb_image: Image.Image) -> None:
        out = lcv.resize(rgb_image, (100, 80))
        assert out.size == (100, 80)

    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.resize(rgb_image, (100, 80))
        assert out is not rgb_image

    def test_mode_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.resize(rgb_image, (100, 80))
        assert out.mode == rgb_image.mode

    def test_all_interpolations(self, rgb_image: Image.Image) -> None:
        for interp in ("nearest", "linear", "bilinear", "cubic", "bicubic", "lanczos"):
            out = lcv.resize(rgb_image, (64, 64), interpolation=interp)
            assert out.size == (64, 64)

    def test_unknown_interpolation(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.resize(rgb_image, (64, 64), interpolation="invalid")

    def test_same_size(self, rgb_image: Image.Image) -> None:
        out = lcv.resize(rgb_image, rgb_image.size)
        assert out.size == rgb_image.size


class TestCrop:
    def test_output_size(self, rgb_image: Image.Image) -> None:
        out = lcv.crop(rgb_image, (10, 20, 100, 80))
        assert out.size == (100, 80)

    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.crop(rgb_image, (0, 0, 128, 128))
        assert out is not rgb_image

    def test_top_left_quadrant_is_red(self, rgb_image: Image.Image) -> None:
        """左上クワドラント（赤）を切り抜いて中心ピクセルが赤か確認。"""
        out = lcv.crop(rgb_image, (0, 0, 128, 128))
        cx, cy = out.size[0] // 2, out.size[1] // 2
        assert out.getpixel((cx, cy)) == (255, 0, 0)


class TestRotate:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.rotate(rgb_image, 90)
        assert out is not rgb_image

    def test_size_unchanged_without_expand(self, rgb_image: Image.Image) -> None:
        out = lcv.rotate(rgb_image, 45)
        assert out.size == rgb_image.size

    def test_size_changes_with_expand(self, rgb_image: Image.Image) -> None:
        out = lcv.rotate(rgb_image, 45, expand=True)
        assert out.size != rgb_image.size

    def test_360_is_identity(self, rgb_image: Image.Image) -> None:
        out = lcv.rotate(rgb_image, 360)
        assert out.size == rgb_image.size
        assert out.tobytes() == rgb_image.tobytes()


class TestFlip:
    def test_flip_vertical_swaps_rows(self, rgb_image: Image.Image) -> None:
        """flipCode=0（上下反転）: 左上の赤が左下に移動する。"""
        out = lcv.flip(rgb_image, 0)
        # 元の左上（赤）が反転後の左下に来るはず
        assert out.getpixel((64, 192)) == (255, 0, 0)

    def test_flip_horizontal_swaps_cols(self, rgb_image: Image.Image) -> None:
        """flipCode=1（左右反転）: 左上の赤が右上に移動する。"""
        out = lcv.flip(rgb_image, 1)
        assert out.getpixel((192, 64)) == (255, 0, 0)

    def test_flip_both(self, rgb_image: Image.Image) -> None:
        """flipCode=-1（両方）: 左上の赤が右下に移動する。"""
        out = lcv.flip(rgb_image, -1)
        assert out.getpixel((192, 192)) == (255, 0, 0)

    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.flip(rgb_image, 0)
        assert out is not rgb_image

    def test_invalid_flipcode(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.flip(rgb_image, 2)


class TestBlur:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.blur(rgb_image, (5, 5))
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.blur(rgb_image, (5, 5))
        assert out.size == rgb_image.size

    def test_mode_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.blur(rgb_image, (5, 5))
        assert out.mode == rgb_image.mode

    def test_invalid_ksize_zero(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.blur(rgb_image, (0, 5))

    def test_invalid_ksize_negative(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.blur(rgb_image, (5, -1))


class TestSharpen:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.sharpen(rgb_image)
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.sharpen(rgb_image, amount=2.0)
        assert out.size == rgb_image.size

    def test_amount_zero_blurs(self, rgb_image: Image.Image) -> None:
        """amount=0.0 はぼかし方向になる（元画像と異なる）。"""
        out = lcv.sharpen(rgb_image, amount=0.0)
        assert out.tobytes() != rgb_image.tobytes()


class TestToGray:
    def test_mode_is_L(self, rgb_image: Image.Image) -> None:
        out = lcv.to_gray(rgb_image)
        assert out.mode == "L"

    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.to_gray(rgb_image)
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.to_gray(rgb_image)
        assert out.size == rgb_image.size


class TestPutText:
    def test_font_not_found(self, rgb_image: Image.Image) -> None:
        with pytest.raises(OSError):
            lcv.put_text(
                rgb_image, "hello", (10, 30), "nonexistent.ttf", 24, (255, 255, 255)
            )

    def test_returns_new_image(self, rgb_image: Image.Image, tmp_path: object) -> None:
        """システムフォントがあれば描画して新規 Image が返ることを確認。"""
        import os
        import sys

        if sys.platform == "win32":
            font = r"C:\Windows\Fonts\arial.ttf"
        else:
            font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(font):
            pytest.skip("System font not available")
        out = lcv.put_text(rgb_image, "test", (10, 30), font, 16, (255, 255, 255))
        assert out is not rgb_image
        assert out.size == rgb_image.size


class TestDrawRectangle:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_rectangle(rgb_image, (10, 10), (50, 50), (0, 255, 0))
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_rectangle(rgb_image, (10, 10), (50, 50), (0, 255, 0))
        assert out.size == rgb_image.size

    def test_outline_drawn(self, rgb_image: Image.Image) -> None:
        """輪郭線の色が正しく描画されること。"""
        out = lcv.draw_rectangle(
            rgb_image, (10, 10), (50, 50), (0, 255, 0), thickness=1
        )
        assert out.getpixel((10, 10)) == (0, 255, 0)

    def test_fill_with_minus1(self, rgb_image: Image.Image) -> None:
        """thickness=-1 で塗りつぶされること。"""
        out = lcv.draw_rectangle(
            rgb_image, (10, 10), (50, 50), (0, 255, 0), thickness=-1
        )
        assert out.getpixel((30, 30)) == (0, 255, 0)


class TestDrawCircle:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_circle(rgb_image, (128, 128), 20, (255, 0, 0))
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_circle(rgb_image, (128, 128), 20, (255, 0, 0))
        assert out.size == rgb_image.size

    def test_fill_with_minus1(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_circle(rgb_image, (128, 128), 20, (0, 0, 255), thickness=-1)
        assert out.getpixel((128, 128)) == (0, 0, 255)

    def test_invalid_radius(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.draw_circle(rgb_image, (128, 128), 0, (255, 0, 0))


class TestDrawLine:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_line(rgb_image, (0, 0), (100, 100), (255, 255, 0))
        assert out is not rgb_image

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.draw_line(rgb_image, (0, 0), (100, 100), (255, 255, 0))
        assert out.size == rgb_image.size

    def test_color_on_line(self, rgb_image: Image.Image) -> None:
        """水平線の色が正しく描画されること。"""
        blank = Image.new("RGB", (100, 100), (0, 0, 0))
        out = lcv.draw_line(blank, (0, 50), (99, 50), (255, 255, 255), thickness=1)
        assert out.getpixel((50, 50)) == (255, 255, 255)


class TestBlend:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.blend(rgb_image, rgb_image, 0.5)
        assert out is not rgb_image

    def test_alpha_zero_equals_img1(self, rgb_image: Image.Image) -> None:
        img2 = Image.new("RGB", rgb_image.size, (0, 0, 0))
        out = lcv.blend(rgb_image, img2, 0.0)
        assert out.tobytes() == rgb_image.tobytes()

    def test_alpha_one_equals_img2(self, rgb_image: Image.Image) -> None:
        img2 = Image.new("RGB", rgb_image.size, (0, 0, 0))
        out = lcv.blend(rgb_image, img2, 1.0)
        assert out.tobytes() == img2.tobytes()

    def test_invalid_alpha_high(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.blend(rgb_image, rgb_image, 1.5)

    def test_invalid_alpha_low(self, rgb_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.blend(rgb_image, rgb_image, -0.1)


class TestComposite:
    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        mask = Image.new("L", rgb_image.size, 128)
        out = lcv.composite(rgb_image, rgb_image, mask)
        assert out is not rgb_image

    def test_mask_zero_returns_img1(self, rgb_image: Image.Image) -> None:
        img2 = Image.new("RGB", rgb_image.size, (0, 0, 0))
        mask = Image.new("L", rgb_image.size, 0)
        out = lcv.composite(rgb_image, img2, mask)
        assert out.tobytes() == rgb_image.tobytes()

    def test_mask_full_returns_img2(self, rgb_image: Image.Image) -> None:
        img2 = Image.new("RGB", rgb_image.size, (0, 0, 0))
        mask = Image.new("L", rgb_image.size, 255)
        out = lcv.composite(rgb_image, img2, mask)
        assert out.tobytes() == img2.tobytes()


class TestAlphaComposite:
    def test_returns_rgba(self, rgba_image: Image.Image) -> None:
        out = lcv.alpha_composite(rgba_image, rgba_image)
        assert out.mode == "RGBA"

    def test_returns_new_image(self, rgba_image: Image.Image) -> None:
        out = lcv.alpha_composite(rgba_image, rgba_image)
        assert out is not rgba_image

    def test_invalid_dst_mode(
        self, rgb_image: Image.Image, rgba_image: Image.Image
    ) -> None:
        with pytest.raises(ValueError):
            lcv.alpha_composite(rgb_image, rgba_image)

    def test_invalid_src_mode(
        self, rgb_image: Image.Image, rgba_image: Image.Image
    ) -> None:
        with pytest.raises(ValueError):
            lcv.alpha_composite(rgba_image, rgb_image)


class TestBgr2Rgb:
    def test_rb_channels_swapped(self, rgb_image: Image.Image) -> None:
        """左上ピクセルが赤 (255,0,0) → bgr2rgb 後は青チャンネルに 255 が入る。"""
        out = lcv.bgr2rgb(rgb_image)
        r_orig, g_orig, b_orig = rgb_image.split()
        r_out, g_out, b_out = out.split()
        assert b_out.tobytes() == r_orig.tobytes()
        assert g_out.tobytes() == g_orig.tobytes()
        assert r_out.tobytes() == b_orig.tobytes()

    def test_returns_new_image(self, rgb_image: Image.Image) -> None:
        out = lcv.bgr2rgb(rgb_image)
        assert out is not rgb_image

    def test_mode_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.bgr2rgb(rgb_image)
        assert out.mode == "RGB"

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        out = lcv.bgr2rgb(rgb_image)
        assert out.size == rgb_image.size

    def test_double_swap_is_identity(self, rgb_image: Image.Image) -> None:
        out = lcv.bgr2rgb(lcv.bgr2rgb(rgb_image))
        assert out.tobytes() == rgb_image.tobytes()

    def test_invalid_mode(self, gray_image: Image.Image) -> None:
        with pytest.raises(ValueError):
            lcv.bgr2rgb(gray_image)

    def test_rgb2bgr_is_alias(self, rgb_image: Image.Image) -> None:
        assert lcv.rgb2bgr(rgb_image).tobytes() == lcv.bgr2rgb(rgb_image).tobytes()


class TestSplit:
    def test_rgb_returns_3_channels(self, rgb_image: Image.Image) -> None:
        channels = lcv.split(rgb_image)
        assert len(channels) == 3

    def test_each_channel_mode_is_L(self, rgb_image: Image.Image) -> None:
        for ch in lcv.split(rgb_image):
            assert ch.mode == "L"

    def test_rgba_returns_4_channels(self, rgba_image: Image.Image) -> None:
        channels = lcv.split(rgba_image)
        assert len(channels) == 4

    def test_gray_returns_1_channel(self, gray_image: Image.Image) -> None:
        channels = lcv.split(gray_image)
        assert len(channels) == 1

    def test_size_preserved(self, rgb_image: Image.Image) -> None:
        for ch in lcv.split(rgb_image):
            assert ch.size == rgb_image.size


class TestMerge:
    def test_roundtrip(self, rgb_image: Image.Image) -> None:
        """split → merge で元の画像に戻る。"""
        channels = lcv.split(rgb_image)
        out = lcv.merge(channels)
        assert out.tobytes() == rgb_image.tobytes()

    def test_mode_is_rgb(self, rgb_image: Image.Image) -> None:
        out = lcv.merge(lcv.split(rgb_image))
        assert out.mode == "RGB"

    def test_wrong_channel_count_raises(self, rgb_image: Image.Image) -> None:
        r, g, _ = lcv.split(rgb_image)
        with pytest.raises(ValueError):
            lcv.merge([r, g], mode="RGB")

    def test_rgba_roundtrip(self, rgba_image: Image.Image) -> None:
        channels = lcv.split(rgba_image)
        out = lcv.merge(channels, mode="RGBA")
        assert out.mode == "RGBA"
        assert out.tobytes() == rgba_image.tobytes()
