from __future__ import annotations

import ctypes
import ctypes.wintypes
import io
from typing import Any

from PIL import Image

from llowcv.camera.base import Camera

# ---------------------------------------------------------------------------
# Windows DLL
# ---------------------------------------------------------------------------
_ole32 = ctypes.windll.ole32  # type: ignore[attr-defined]
_mfplat = ctypes.windll.mfplat  # type: ignore[attr-defined]
_mf = ctypes.windll.mf  # type: ignore[attr-defined]
_mfreadwrite = ctypes.windll.mfreadwrite  # type: ignore[attr-defined]

COINIT_MULTITHREADED = 0x0
MF_VERSION = 0x00020070
MFSTARTUP_FULL = 0x3
MF_SOURCE_READER_FIRST_VIDEO_STREAM = ctypes.c_uint32(0xFFFFFFFC).value

# ---------------------------------------------------------------------------
# GUID ヘルパー
# ---------------------------------------------------------------------------


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_uint32),
        ("Data2", ctypes.c_uint16),
        ("Data3", ctypes.c_uint16),
        ("Data4", ctypes.c_uint8 * 8),
    ]


def _guid(s: str) -> _GUID:
    """'{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}' 形式から GUID を生成する。"""
    s = s.strip("{}")
    p = s.split("-")
    d4 = bytes.fromhex(p[3] + p[4])
    return _GUID(int(p[0], 16), int(p[1], 16), int(p[2], 16), (ctypes.c_uint8 * 8)(*d4))


_ATTR_SOURCE_TYPE = _guid("{C60AC5FE-252A-478F-A0EF-BC8FA5F7CAD3}")
_ATTR_VIDCAP_GUID = _guid("{8AC3587A-4AE7-42D8-99E0-0A6013EEF90F}")
_IID_IMFMediaSource = _guid("{279A808D-AEC7-40C8-9C6B-A6B492C78A66}")


# ---------------------------------------------------------------------------
# vtable ヘルパー
# ---------------------------------------------------------------------------


def _vtfn(ptr: ctypes.c_void_p, index: int, restype: type, *argtypes: type) -> Any:
    """COM vtable の index 番目の関数ポインタを返す。"""
    addr = ptr.value if hasattr(ptr, "value") else int(ptr)
    if not addr:
        raise OSError("NULL COM interface pointer")
    vptr = ctypes.cast(addr, ctypes.POINTER(ctypes.c_void_p))
    vtable_addr = vptr[0]
    if not vtable_addr:
        raise OSError("NULL vtable pointer")
    table = ctypes.cast(vtable_addr, ctypes.POINTER(ctypes.c_void_p))
    return ctypes.cast(table[index], ctypes.CFUNCTYPE(restype, *argtypes))  # type: ignore


def _hr(result: int, msg: str) -> None:
    if result < 0:
        raise OSError(f"{msg} failed (HRESULT=0x{result & 0xFFFFFFFF:08X})")


# ---------------------------------------------------------------------------
# WindowsCamera
# ---------------------------------------------------------------------------


class WindowsCamera(Camera):
    """Windows Media Foundation バックエンドのカメラ実装。"""

    def __init__(
        self,
        index: int = 0,
        size: tuple[int, int] | None = None,
        fps: int | None = None,
    ) -> None:
        self._reader: ctypes.c_void_p | None = None
        self._mf_started = False

        _hr(_ole32.CoInitializeEx(None, COINIT_MULTITHREADED), "CoInitializeEx")
        _hr(_mfplat.MFStartup(MF_VERSION, MFSTARTUP_FULL), "MFStartup")
        self._mf_started = True

        try:
            self._reader = self._create_reader(index)
        except Exception:
            self.close()
            raise

    # ------------------------------------------------------------------
    def _create_reader(self, index: int) -> ctypes.c_void_p:
        # 1. 属性オブジェクトを作成して VIDEO_CAPTURE を指定
        pp_attr = ctypes.c_void_p()
        _hr(_mfplat.MFCreateAttributes(ctypes.byref(pp_attr), 1), "MFCreateAttributes")
        if not pp_attr.value:
            raise OSError("MFCreateAttributes returned NULL interface pointer")

        # IMFAttributes::SetGUID (vtable index 21)
        # IUnknown(0-2) + IMFAttributes::GetItem(3)..SetDouble(20)..SetGUID(21)
        SetGUID = _vtfn(
            pp_attr,
            21,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.POINTER(_GUID),
            ctypes.POINTER(_GUID),
        )
        _hr(
            SetGUID(
                pp_attr,
                ctypes.byref(_ATTR_SOURCE_TYPE),
                ctypes.byref(_ATTR_VIDCAP_GUID),
            ),
            "IMFAttributes::SetGUID",
        )

        # 2. デバイスを列挙
        pp_devices = ctypes.c_void_p()
        count = ctypes.c_uint32(0)
        _hr(
            _mf.MFEnumDeviceSources(
                pp_attr, ctypes.byref(pp_devices), ctypes.byref(count)
            ),
            "MFEnumDeviceSources",
        )
        if index >= count.value:
            raise OSError(
                f"Camera {index} not found ({count.value} device(s) available)"
            )

        # 3. IMFActivate::ActivateObject → IMFMediaSource
        devices = ctypes.cast(pp_devices, ctypes.POINTER(ctypes.c_void_p))
        activate = devices[index]

        # IMFActivate::ActivateObject (vtable index 30)
        # IMFActivate inherits IMFAttributes (0-29), ActivateObject is first at 30
        ActivateObject = _vtfn(
            activate,
            30,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.POINTER(_GUID),
            ctypes.POINTER(ctypes.c_void_p),
        )
        pp_source = ctypes.c_void_p()
        _hr(
            ActivateObject(
                activate, ctypes.byref(_IID_IMFMediaSource), ctypes.byref(pp_source)
            ),
            "IMFActivate::ActivateObject",
        )

        # 4. SourceReader を作成
        pp_reader = ctypes.c_void_p()
        _hr(
            _mfreadwrite.MFCreateSourceReaderFromMediaSource(
                pp_source, None, ctypes.byref(pp_reader)
            ),
            "MFCreateSourceReaderFromMediaSource",
        )
        return pp_reader

    # ------------------------------------------------------------------
    def capture(self, timeout: float | None = None) -> Image.Image:
        """1フレームをキャプチャする。

        Args:
            timeout: タイムアウト秒数（現実装では未使用）。

        Returns:
            キャプチャされた PIL.Image（mode='RGB'）。

        Raises:
            OSError: キャプチャに失敗した場合。
        """
        if self._reader is None:
            raise OSError("Camera is not open")

        # IMFSourceReader::ReadSample (vtable index 9)
        # IUnknown(0-2), GetStreamSelection(3)..SetCurrentPosition(8), ReadSample(9)
        ReadSample = _vtfn(
            self._reader,
            9,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_void_p),
        )
        flags = ctypes.c_uint32(0)
        ts = ctypes.c_int64(0)
        pp_sample = ctypes.c_void_p()
        _hr(
            ReadSample(
                self._reader,
                MF_SOURCE_READER_FIRST_VIDEO_STREAM,
                0,
                None,
                ctypes.byref(flags),
                ctypes.byref(ts),
                ctypes.byref(pp_sample),
            ),
            "IMFSourceReader::ReadSample",
        )

        return self._sample_to_image(pp_sample)

    def _sample_to_image(self, pp_sample: ctypes.c_void_p) -> Image.Image:
        # IMFSample::ConvertToContiguousBuffer (vtable index 38)
        # IMFSample inherits IMFAttributes (0-29), then GetSampleFlags(30)..
        # GetBufferByIndex(37), ConvertToContiguousBuffer(38)
        ConvertToContiguousBuffer = _vtfn(
            pp_sample,
            38,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        )
        pp_buf = ctypes.c_void_p()
        _hr(
            ConvertToContiguousBuffer(pp_sample, ctypes.byref(pp_buf)),
            "ConvertToContiguousBuffer",
        )

        # IMFMediaBuffer::GetCurrentLength (vtable index 5)
        GetCurrentLength = _vtfn(
            pp_buf, 5, ctypes.c_int32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)
        )
        length = ctypes.c_uint32(0)
        _hr(GetCurrentLength(pp_buf, ctypes.byref(length)), "GetCurrentLength")

        # IMFMediaBuffer::Lock (vtable index 3)
        Lock = _vtfn(
            pp_buf,
            3,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        )
        # IMFMediaBuffer::Unlock (vtable index 4)
        Unlock = _vtfn(pp_buf, 4, ctypes.c_int32, ctypes.c_void_p)

        p_data = ctypes.c_void_p()
        _hr(Lock(pp_buf, ctypes.byref(p_data), None, None), "IMFMediaBuffer::Lock")
        try:
            raw = bytes(ctypes.string_at(p_data, length.value))
        finally:
            Unlock(pp_buf)

        # MJPEG の場合は Pillow で直接デコード
        if raw[:2] == b"\xff\xd8":
            return Image.open(io.BytesIO(raw)).convert("RGB")
        raise OSError("Unsupported pixel format from Media Foundation")

    # ------------------------------------------------------------------
    def set_control(self, name: str, value: int) -> None:
        raise NotImplementedError(f"set_control not yet implemented: {name!r}")

    def close(self) -> None:
        """カメラを閉じてリソースを解放する。"""
        if self._reader is not None:
            Release = _vtfn(self._reader, 2, ctypes.c_uint32, ctypes.c_void_p)
            Release(self._reader)
            self._reader = None
        if self._mf_started:
            _mfplat.MFShutdown()
            self._mf_started = False
        _ole32.CoUninitialize()
