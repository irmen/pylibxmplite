"""
Python interface to the libxmp-lite library (part of https://github.com/cmatsuoka/libxmp)
plays Protracker (MOD), Scream Tracker 3 (S3M), Fast Tracker II (XM), and Impulse Tracker (IT).

Author: Irmen de Jong (irmen@razorvine.net)
Software license: "MIT software license". See http://opensource.org/licenses/MIT
"""

import os
import sys
import inspect
from typing import Tuple, List, Dict, Union
from collections import namedtuple
from _libxmplite import lib, ffi
from _libxmplite.lib import XMP_FORMAT_8BIT, XMP_FORMAT_UNSIGNED, XMP_FORMAT_MONO


__version__ = "1.0"
xmp_version = ffi.string(lib.xmp_version).decode()


XEvent = namedtuple("Event", ["note", "ins", "vol", "fxt", "fxp", "f2t", "f2p"])


class XmpError(Exception):
    def __init__(self, msg: str, errorcode: int) -> None:
        super().__init__(msg)
        self.errorcode = errorcode


class ChannelInfo:
    period = 0
    position = 0
    pitchbend = 0
    note = 0
    instrument = 0
    sample = 0
    volume = 0
    pan = 0
    event = XEvent(0, 0, 0, 0, 0, 0, 0)


class FrameInfo:
    pos = 0
    pattern = 0
    row = 0
    num_rows = 0
    frame = 0
    speed = 0
    bpm = 0
    time = 0
    total_time = 0
    frame_time = 0
    buffer = memoryview(b"")
    buffer_size = 0         # you can use len(buffer) as well
    total_size = 0
    volume = 0
    loop_count = 0
    virt_channels = 0
    virt_used = 0
    sequence = 0
    channel_info = []       # type: List[ChannelInfo]


def _get_filename_bytes(filename: str) -> bytes:
    filename2 = os.path.expanduser(filename)
    if not os.path.isfile(filename2):
        raise FileNotFoundError(filename)
    return filename2.encode(sys.getfilesystemencoding())


def test_module(filename: str) -> Tuple[str, str]:
    """investigate a module file and return its name and type"""
    testinfo = ffi.new("struct xmp_test_info *")
    fbytes = _get_filename_bytes(filename)
    result = lib.xmp_test_module(fbytes, testinfo)
    if result != 0:
        raise XmpError("cannot successfully check module", result)
    name = ffi.string(testinfo.name).decode()
    mtype = ffi.string(testinfo.type).decode()
    return name, mtype


def get_formats() -> List[str]:
    """return the supported module formats"""
    fmts = lib.xmp_get_format_list()
    result = []
    for i in range(9999):
        fmt = fmts[i]
        if fmt == ffi.NULL:
            break
        result.append(ffi.string(fmt).decode())
    return result


class Xmp:
    def __init__(self):
        self._context = lib.xmp_create_context()
        self._buffer = bytearray(128 * 1024)

    def load(self, filename: str) -> None:
        result = lib.xmp_load_module(self._context, _get_filename_bytes(filename))
        if result != 0:
            raise XmpError("cannot load module", result)

    def load_mem(self, data: bytes) -> None:
        result = lib.xmp_load_module_from_memory(self._context, data, len(data))
        if result != 0:
            raise XmpError("cannot load module", result)

    def release(self) -> None:
        lib.xmp_release_module(self._context)

    def scan(self) -> None:
        lib.xmp_scan_module(self._context)

    def module_info(self) -> Dict[str, Union[str, int]]:
        info = ffi.new("struct xmp_module_info *")
        lib.xmp_get_module_info(self._context, info)
        return {
            "name": ffi.string(info.mod.name).decode(),
            "comment": "" if info.comment == ffi.NULL else ffi.string(info.comment).decode(),
            "type": ffi.string(info.mod.type).decode(),
            "pat": info.mod.pat,
            "trk": info.mod.trk,
            "chn": info.mod.chn,
            "ins": info.mod.ins,
            "smp": info.mod.smp,
            "spd": info.mod.spd,
            "bpm": info.mod.bpm,
            "rst": info.mod.rst,
            "gvl": info.mod.gvl,
        }

    def start(self, sample_rate: int = 44100, format: int = 0) -> None:
        result = lib.xmp_start_player(self._context, sample_rate, format)
        if result != 0:
            raise XmpError("cannot start player", result)

    def stop(self) -> None:
        lib.xmp_end_player(self._context)

    def pause(self) -> None:
        lib.xmp_stop_module(self._context)

    def restart(self) -> None:
        lib.xmp_restart_module(self._context)

    def play_frame(self) -> FrameInfo:
        """play a single frame of the module. Returns result of frame_info() immediately."""
        result = lib.xmp_play_frame(self._context)
        if result != 0:
            raise XmpError("cannot play", result)
        return self.frame_info()

    def play_buffer(self, size: int = 4096, loop: int = 0) -> memoryview:
        """Fill internal buffer with sound data. Returns view to that data in the internal buffer."""
        if size > len(self._buffer) or size <= 0:
            raise ValueError("requested size too large or invalid")
        result = lib.xmp_play_buffer(self._context, ffi.from_buffer(self._buffer), size, loop)
        if result != 0:
            raise XmpError("cannot play", result)
        return memoryview(self._buffer)[0:size]

    def frame_info(self) -> FrameInfo:
        xinfo = ffi.new("struct xmp_frame_info *")
        lib.xmp_get_frame_info(self._context, xinfo)
        info = FrameInfo()
        for name, value in inspect.getmembers(xinfo):
            setattr(info, name, value)
        info.buffer = memoryview(ffi.buffer(xinfo.buffer, xinfo.buffer_size))
        info.channel_info = [self._make_channelinfo(cinfo) for cinfo in xinfo.channel_info]
        return info

    def inject_event(self, channel: int, event: XEvent) -> None:
        xevent = ffi.new("struct xmp_event*")
        xevent.note = event.note
        xevent.ins = event.ins
        xevent.vol = event.vol
        xevent.fxt = event.fxt
        xevent.fxp = event.fxp
        xevent.f2t = event.f2t
        xevent.f2p = event.f2p
        lib.xmp_inject_event(self._context, channel, xevent)

    def __del__(self):
        self.stop()
        lib.xmp_free_context(self._context)

    def _make_channelinfo(self, cinfo: ffi.CData) -> ChannelInfo:
        info = ChannelInfo()
        for name, value in inspect.getmembers(cinfo):
            setattr(info, name, value)
        info.event = XEvent(cinfo.event.note, cinfo.event.ins, cinfo.event.vol,
                            cinfo.event.fxt, cinfo.event.fxp, cinfo.event.f2t, cinfo.event.f2p)
        return info


# TODO: implement the song control functions
# TODO: implement the external sample mixer functions?
"""
int         xmp_next_position   (xmp_context);
int         xmp_prev_position   (xmp_context);
int         xmp_set_position    (xmp_context, int);
int         xmp_set_row         (xmp_context, int);
int         xmp_set_tempo_factor(xmp_context, double);
int         xmp_seek_time       (xmp_context, int);
int         xmp_channel_mute    (xmp_context, int, int);
int         xmp_channel_vol     (xmp_context, int, int);
int         xmp_set_player      (xmp_context, int, int);
int         xmp_get_player      (xmp_context, int);
int         xmp_set_instrument_path (xmp_context, char *);

int         xmp_start_smix       (xmp_context, int, int);
void        xmp_end_smix         (xmp_context);
int         xmp_smix_play_instrument(xmp_context, int, int, int, int);
int         xmp_smix_play_sample (xmp_context, int, int, int, int);
int         xmp_smix_channel_pan (xmp_context, int, int);
int         xmp_smix_load_sample (xmp_context, int, char *);
int         xmp_smix_release_sample (xmp_context, int);
"""
