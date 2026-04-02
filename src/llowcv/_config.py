import os


def _parse_bool_env(key: str, default: bool) -> bool:
    """環境変数をboolとして読む。0 / false / no / off → False、それ以外 → True。"""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() not in {"0", "false", "no", "off"}


class _Config:
    """llowcv グローバル設定。

    環境変数で初期値を制御できる。

    Attributes:
        warn_noop: True の場合、操作に効果がない（no-op）時に UserWarning を出す。
            False に設定すると、すべての no-op 警告を一括抑制する。
            環境変数 LLOWCV_WARN_NOOP で初期値を指定可能（0 / false / no / off で無効化）。
    """

    warn_noop: bool = _parse_bool_env("LLOWCV_WARN_NOOP", default=True)


config = _Config()
