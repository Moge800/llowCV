"""カメラ API のテスト。

USB カメラが接続されていない環境では @camera_available でスキップする。
カメラ未接続でも動くテストは常に実行する。
"""

import pytest
from PIL import Image

import llowcv as lcv


def _is_camera_available() -> bool:
    """USB カメラ（index=0）が利用可能か確認する。"""
    try:
        with lcv.Camera(index=0) as cam:
            frame = cam.capture(timeout=2.0)
            return frame is not None
    except Exception:
        # OSError / NotImplementedError の他、COM 初期化エラーも含めて吸収する
        return False


camera_available = pytest.mark.skipif(
    not _is_camera_available(),
    reason="USB camera not connected",
)


class TestCameraNotFound:
    def test_invalid_index_raises_oserror(self) -> None:
        with pytest.raises(OSError):
            lcv.Camera(index=99).capture()

    def test_context_manager_protocol(self) -> None:
        """__enter__ / __exit__ が定義されていることを確認。"""
        assert hasattr(lcv.Camera, "__enter__")
        assert hasattr(lcv.Camera, "__exit__")


@camera_available
class TestCameraCapture:
    def test_returns_pil_image(self) -> None:
        with lcv.Camera(index=0) as cam:
            frame = cam.capture()
        assert isinstance(frame, Image.Image)

    def test_mode_is_rgb(self) -> None:
        with lcv.Camera(index=0) as cam:
            frame = cam.capture()
        assert frame.mode == "RGB"

    def test_size_is_nonzero(self) -> None:
        with lcv.Camera(index=0) as cam:
            frame = cam.capture()
        w, h = frame.size
        assert w > 0 and h > 0

    def test_context_manager_closes(self) -> None:
        """with ブロック終了後に close() が呼ばれること。"""
        with lcv.Camera(index=0) as cam:
            _ = cam.capture()
        # close() 後に再キャプチャすると OSError になるはず
        with pytest.raises((OSError, NotImplementedError)):
            cam.capture()
