"""

Example program that loads the given mod file in the Xmp player,
and uses it in a miniaudio playback generator function to stream the music.

Windows version that is displaying far less information on screen because
the windows console is.... well.

(miniaudio: https://pypi.org/project/miniaudio/ )

"""

import sys
import miniaudio
import libxmplite


class Display:
    def __init__(self, mod_info: libxmplite.ModuleInfo) -> None:
        self.mod_info = mod_info
        print("PLAYING MODULE: ", self.mod_info.name)
        print("  (", self.mod_info.type, " ", self.mod_info.chn, "channels ", self.mod_info.bpm, "bpm )")

    def update(self, info: libxmplite.FrameInfo) -> None:
        print("\r #", info.time, "/", info.total_time, "  pos", info.pos, " pat", info.pattern, " row", info.row, end="       ", flush=True)


def stream_module(xmp: libxmplite.Xmp, display: Display):
    required_frames = yield b""  # generator initialization
    try:
        while True:
            buffer = xmp.play_buffer(required_frames * 2 * 2)
            display.update(xmp.frame_info())
            required_frames = yield buffer
    except libxmplite.XmpError as x:
        print("XMP Playback error!!", x)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("must give mod filename to play as argument")

    device = miniaudio.PlaybackDevice(output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=44100, buffersize_msec=100)

    xmp = libxmplite.Xmp()
    xmp.load(sys.argv[1])
    xmp.start(device.sample_rate)

    mod_info = xmp.module_info()
    display = Display(mod_info)
    stream = stream_module(xmp, display)
    next(stream)  # start the generator
    device.start(stream)

    print("\nFile playing in the background. Press enter to stop playback!\n")
    input()

    xmp.stop()
    xmp.release()
    device.close()
