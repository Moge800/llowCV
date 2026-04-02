from __future__ import annotations

import ctypes
import fcntl
import io
import mmap
import os
import select

from PIL import Image

from llowcv.camera.base import Camera

# ---------------------------------------------------------------------------
# v4l2 定数
# ---------------------------------------------------------------------------
V4L2_BUF_TYPE_VIDEO_CAPTURE = 1
V4L2_MEMORY_MMAP = 1
V4L2_FIELD_NONE = 1
V4L2_PIX_FMT_MJPEG = 0x47504A4D  # b'MJPG'
V4L2_PIX_FMT_YUYV = 0x56595559  # b'YUYV'

# ---------------------------------------------------------------------------
# v4l2 ctypes 構造体
# ---------------------------------------------------------------------------


class _timeval(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_usec", ctypes.c_long)]


class _v4l2_timecode(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("frames", ctypes.c_uint8),
        ("seconds", ctypes.c_uint8),
        ("minutes", ctypes.c_uint8),
        ("hours", ctypes.c_uint8),
        ("userbits", ctypes.c_uint8 * 4),
    ]


class _v4l2_buffer_m(ctypes.Union):
    _fields_ = [
        ("offset", ctypes.c_uint32),
        ("userptr", ctypes.c_ulong),
        ("planes", ctypes.c_void_p),
        ("fd", ctypes.c_int32),
    ]


class _v4l2_buffer(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("bytesused", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("field", ctypes.c_uint32),
        ("timestamp", _timeval),
        ("timecode", _v4l2_timecode),
        ("sequence", ctypes.c_uint32),
        ("memory", ctypes.c_uint32),
        ("m", _v4l2_buffer_m),
        ("length", ctypes.c_uint32),
        ("reserved2", ctypes.c_uint32),
        ("request_fd", ctypes.c_int32),
    ]


class _v4l2_pix_format(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("pixelformat", ctypes.c_uint32),
        ("field", ctypes.c_uint32),
        ("bytesperline", ctypes.c_uint32),
        ("sizeimage", ctypes.c_uint32),
        ("colorspace", ctypes.c_uint32),
        ("priv", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("ycbcr_enc", ctypes.c_uint32),
        ("quantization", ctypes.c_uint32),
        ("xfer_func", ctypes.c_uint32),
    ]


class _v4l2_format_union(ctypes.Union):
    _fields_ = [
        ("pix", _v4l2_pix_format),
        ("raw_data", ctypes.c_byte * 200),
    ]


class _v4l2_format(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32),
        ("fmt", _v4l2_format_union),
    ]


class _v4l2_requestbuffers(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("memory", ctypes.c_uint32),
        ("capabilities", ctypes.c_uint32),
        ("flags", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
    ]


# ---------------------------------------------------------------------------
# ioctl 番号をプラットフォームの sizeof から動的計算
# ---------------------------------------------------------------------------
def _ioc(direction: int, type_: str, nr: int, size: int) -> int:
    return (direction << 30) | (ord(type_) << 8) | nr | (size << 16)


_IOC_READ = 2
_IOC_WRITE = 1
_IOC_RW = _IOC_READ | _IOC_WRITE

VIDIOC_S_FMT = _ioc(_IOC_RW, "V", 5, ctypes.sizeof(_v4l2_format))
VIDIOC_REQBUFS = _ioc(_IOC_RW, "V", 8, ctypes.sizeof(_v4l2_requestbuffers))
VIDIOC_QUERYBUF = _ioc(_IOC_RW, "V", 9, ctypes.sizeof(_v4l2_buffer))
VIDIOC_QBUF = _ioc(_IOC_RW, "V", 15, ctypes.sizeof(_v4l2_buffer))
VIDIOC_DQBUF = _ioc(_IOC_RW, "V", 17, ctypes.sizeof(_v4l2_buffer))
VIDIOC_STREAMON = _ioc(_IOC_WRITE, "V", 18, ctypes.sizeof(ctypes.c_int))
VIDIOC_STREAMOFF = _ioc(_IOC_WRITE, "V", 19, ctypes.sizeof(ctypes.c_int))

_NUM_BUFS = 2


# ---------------------------------------------------------------------------
# LinuxCamera
# ---------------------------------------------------------------------------


class LinuxCamera(Camera):
    """Linux v4l2 バックエンドのカメラ実装。"""

    def __init__(
        self,
        index: int = 0,
        size: tuple[int, int] | None = None,
        fps: int | None = None,
    ) -> None:
        devpath = f"/dev/video{index}"
        try:
            self._fd = os.open(devpath, os.O_RDWR | os.O_NONBLOCK)  # type: ignore
        except OSError as e:
            raise OSError(f"Camera {index} not available: {devpath}") from e
        self._mmaps: list[tuple[mmap.mmap, int]] = []
        self._size = size or (640, 480)
        self._pixfmt = V4L2_PIX_FMT_MJPEG
        self._actual_size = self._size
        try:
            self._init_device()
        except Exception:
            os.close(self._fd)
            self._fd = -1
            raise

    def _ioctl(self, req: int, arg: ctypes._CData) -> None:
        import errno

        while True:
            try:
                fcntl.ioctl(self._fd, req, arg)  # type: ignore
                return
            except OSError as e:
                if e.errno == errno.EINTR:
                    continue
                raise

    def _init_device(self) -> None:
        w, h = self._size

        # フォーマット設定（MJPEG 優先、失敗時 YUYV へフォールバック）
        fmt = _v4l2_format()
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        fmt.fmt.pix.width = w
        fmt.fmt.pix.height = h
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG
        fmt.fmt.pix.field = V4L2_FIELD_NONE
        try:
            self._ioctl(VIDIOC_S_FMT, fmt)
        except OSError:
            fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV
            self._ioctl(VIDIOC_S_FMT, fmt)
        self._pixfmt = fmt.fmt.pix.pixelformat
        self._actual_size = (fmt.fmt.pix.width, fmt.fmt.pix.height)

        # バッファリクエスト
        req_bufs = _v4l2_requestbuffers()
        req_bufs.count = _NUM_BUFS
        req_bufs.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        req_bufs.memory = V4L2_MEMORY_MMAP
        self._ioctl(VIDIOC_REQBUFS, req_bufs)

        # バッファを mmap してキューに積む
        for i in range(req_bufs.count):
            buf = _v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP
            buf.index = i
            self._ioctl(VIDIOC_QUERYBUF, buf)
            mm = mmap.mmap(
                self._fd,
                buf.length,
                mmap.MAP_SHARED,  # type: ignore
                mmap.PROT_READ | mmap.PROT_WRITE,  # type: ignore
                offset=buf.m.offset,
            )
            self._mmaps.append((mm, buf.length))
            self._ioctl(VIDIOC_QBUF, buf)

        # ストリーム開始
        buf_type = ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE)
        self._ioctl(VIDIOC_STREAMON, buf_type)

    def capture(self, timeout: float | None = None) -> Image.Image:
        """1フレームをキャプチャする。

        Args:
            timeout: タイムアウト秒数。None で無制限に待機。

        Returns:
            キャプチャされた PIL.Image（mode='RGB'）。

        Raises:
            OSError: キャプチャに失敗した場合。
        """
        rlist, _, _ = select.select([self._fd], [], [], timeout)
        if not rlist:
            raise OSError("Camera capture timed out")

        buf = _v4l2_buffer()
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = V4L2_MEMORY_MMAP
        self._ioctl(VIDIOC_DQBUF, buf)

        mm, _ = self._mmaps[buf.index]
        mm.seek(0)
        data = mm.read(buf.bytesused)

        self._ioctl(VIDIOC_QBUF, buf)

        return self._decode(data)

    def _decode(self, data: bytes) -> Image.Image:
        if self._pixfmt == V4L2_PIX_FMT_MJPEG:
            return Image.open(io.BytesIO(data)).convert("RGB")
        w, h = self._actual_size
        return _yuyv_to_rgb(data, w, h)

    def set_control(self, name: str, value: int) -> None:
        raise NotImplementedError(f"set_control not yet implemented: {name!r}")

    def close(self) -> None:
        """カメラを閉じる。"""
        if not hasattr(self, "_fd") or self._fd < 0:
            return
        try:
            buf_type = ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE)
            self._ioctl(VIDIOC_STREAMOFF, buf_type)
        except OSError:
            pass
        for mm, _ in self._mmaps:
            mm.close()
        self._mmaps.clear()
        os.close(self._fd)
        self._fd = -1


def _yuyv_to_rgb(data: bytes, width: int, height: int) -> Image.Image:
    """YUYV（YUY2）バイト列を RGB PIL.Image に変換する。"""
    import array

    out = array.array("B", bytes(width * height * 3))
    src = memoryview(data)
    dst = 0
    for i in range(0, width * height * 2, 4):
        y0, u, y1, v = src[i], src[i + 1], src[i + 2], src[i + 3]
        for y in (y0, y1):
            out[dst] = max(0, min(255, int(y + 1.402 * (v - 128))))
            out[dst + 1] = max(
                0, min(255, int(y - 0.344 * (u - 128) - 0.714 * (v - 128)))
            )
            out[dst + 2] = max(0, min(255, int(y + 1.772 * (u - 128))))
            dst += 3
    return Image.frombytes("RGB", (width, height), bytes(out))
