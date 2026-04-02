import warnings

from PIL import Image, UnidentifiedImageError


def imread(path: str, mode: str = "RGB") -> Image.Image:
    """画像ファイルを読み込む。

    Args:
        path: 読み込むファイルのパス。
        mode: PIL の画像モード。デフォルトは 'RGB'。

    Returns:
        読み込んだ PIL.Image オブジェクト。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
        ValueError: 未対応のフォーマットの場合。
    """
    try:
        img = Image.open(path)
        return img.convert(mode)
    except UnidentifiedImageError as e:
        raise ValueError(str(e)) from e


def imwrite(path: str, img: Image.Image) -> None:
    """画像をファイルに書き出す。

    Args:
        path: 書き出すファイルのパス。フォーマットは拡張子から自動判定。
        img: 書き出す PIL.Image オブジェクト。

    Raises:
        ValueError: 未対応のフォーマットの場合。
    """
    try:
        img.save(path)
    except (KeyError, ValueError) as e:
        raise ValueError(str(e)) from e


def imshow(
    img: Image.Image,
    backend: str | None = None,
    block: bool = True,
    silent: bool = False,
) -> None:
    """画像をデスクトップに表示する。

    デバッグ・確認用途。waitKey 不要。呼び出しのたびに新規ウィンドウが開く。
    リアルタイムプレビューが必要な場合は cv2 を使うこと。

    Args:
        img: 表示する PIL.Image オブジェクト。
        backend: 表示バックエンド。None または 'pillow' でデフォルト（OS のビューア）、
            'mpl' で matplotlib を使用。
        block: True の場合、ウィンドウが閉じられるまで処理をブロックする。
            'mpl' バックエンドにのみ有効。'pillow' バックエンドでは無視され警告が出る。
        silent: True の場合、no-op 警告を抑制する。

    Raises:
        ValueError: 不明な backend が指定された場合。
    """
    if backend is None or backend == "pillow":
        if not block and not silent:
            warnings.warn(
                "'block' has no effect on the 'pillow' backend. "
                "The OS viewer is always opened asynchronously.",
                UserWarning,
                stacklevel=2,
            )
        img.show()
    elif backend == "mpl":
        import matplotlib.pyplot as plt

        plt.imshow(img)
        plt.axis("off")
        plt.show(block=block)
    else:
        raise ValueError(f"Unknown backend: {backend!r}")
