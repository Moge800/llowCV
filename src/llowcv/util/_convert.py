from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    import numpy


def as_cv2(img: Image.Image) -> numpy.ndarray:
    """PIL.Image を OpenCV 互換の ndarray（BGR）に変換する。

    Args:
        img: 変換する PIL.Image（mode='RGB'）。

    Returns:
        BGR 順の uint8 ndarray。shape は (height, width, 3)。

    Raises:
        ImportError: numpy がインストールされていない場合。
    """
    import numpy as np

    return np.array(img.convert("RGB"))[:, :, ::-1].copy()


def from_cv2(arr: numpy.ndarray) -> Image.Image:
    """OpenCV 互換の ndarray（BGR）を PIL.Image に変換する。

    Args:
        arr: BGR 順の uint8 ndarray。shape は (height, width, 3)。

    Returns:
        変換された PIL.Image（mode='RGB'）。

    Raises:
        ImportError: numpy がインストールされていない場合。
    """
    import numpy as np

    return Image.fromarray(arr[:, :, ::-1].astype(np.uint8))


def as_numpy(img: Image.Image) -> numpy.ndarray:
    """PIL.Image を RGB ndarray に変換する。

    Args:
        img: 変換する PIL.Image。

    Returns:
        RGB 順の ndarray。

    Raises:
        ImportError: numpy がインストールされていない場合。
    """
    import numpy as np

    return np.array(img)


def to_bgr(arr: numpy.ndarray) -> numpy.ndarray:
    """RGB ndarray を BGR ndarray に変換する。

    Args:
        arr: RGB 順の ndarray。shape は (height, width, 3)。

    Returns:
        BGR 順の ndarray。

    Raises:
        ImportError: numpy がインストールされていない場合。
    """
    import numpy as np  # noqa: F401

    return arr[:, :, ::-1].copy()
