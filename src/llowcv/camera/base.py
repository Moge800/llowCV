from __future__ import annotations

import sys

from PIL import Image


class Camera:
    """USB UVC カメラからフレームを取得するクラス。

    プラットフォームに応じて適切な実装を返すファクトリクラス。
    Windows は Media Foundation、Linux は v4l2 バックエンドを使用する。

    Examples:
        >>> with Camera(index=0) as cam:
        ...     frame = cam.capture()
    """

    def __new__(
        cls,
        index: int = 0,
        size: tuple[int, int] | None = None,
        fps: int | None = None,
    ) -> Camera:
        if cls is Camera:
            if sys.platform == "win32":
                from llowcv.camera.windows import WindowsCamera

                return object.__new__(WindowsCamera)
            else:
                from llowcv.camera.linux import LinuxCamera

                return object.__new__(LinuxCamera)
        return object.__new__(cls)

    def __init__(
        self,
        index: int = 0,
        size: tuple[int, int] | None = None,
        fps: int | None = None,
    ) -> None:
        """カメラを初期化する。

        Args:
            index: カメラのデバイスインデックス。
            size: キャプチャサイズ (width, height)。None でデバイスデフォルト。
            fps: フレームレート。None でデバイスデフォルト。

        Raises:
            OSError: カメラが見つからない、または初期化に失敗した場合。
        """

    def capture(self, timeout: float | None = None) -> Image.Image:
        """1フレームをキャプチャする。

        Args:
            timeout: タイムアウト秒数。None で無制限に待機。

        Returns:
            キャプチャされた PIL.Image（mode='RGB'）。

        Raises:
            OSError: キャプチャに失敗した場合。
        """
        raise NotImplementedError

    def set_control(self, name: str, value: int) -> None:
        """カメラコントロールを設定する。

        Args:
            name: コントロール名（例: 'brightness', 'contrast'）。
            value: 設定値。

        Raises:
            OSError: コントロールの設定に失敗した場合。
            ValueError: 未対応のコントロール名の場合。
        """
        raise NotImplementedError

    def close(self) -> None:
        """カメラを閉じる。"""
        raise NotImplementedError

    def __enter__(self) -> Camera:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
