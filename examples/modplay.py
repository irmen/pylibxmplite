"""

Example program that loads the given mod file in the Xmp player,
and uses it in a miniaudio playback generator function to stream the music.

(miniaudio: https://pypi.org/project/miniaudio/ )

"""

import sys
import miniaudio
import libxmplite


class Display:
    def __init__(self, mod_info: libxmplite.ModuleInfo) -> None:
        self.mod_info = mod_info

    def update(self, info: libxmplite.FrameInfo) -> None:
        self.cls()
        print("PLAYING MODULE: ", self.mod_info.name)
        print("  (", self.mod_info.type, " ", self.mod_info.chn, "channels ", self.mod_info.bpm, "bpm )")
        print("\n#", info.time, "/", info.total_time, "  pos", info.pos, " pat", info.pattern, " row", info.row, "\n")
        for ch in info.channel_info[:mod_info.chn]:
            print("*" if ch.event else " ", "I{:03d} #{:03d}".format(ch.instrument, ch.note), end="")
            volume = "#" * int((ch.volume / mod_info.gvl) * 64)
            print(" |", volume.ljust(64, " "), "|")
        print("\nPress enter to quit.", flush=True)

    def cls(self) -> None:
        print("\033[2J\033[H", end="")

    def close(self) -> None:
        pass


def stream_module(xmp: libxmplite.Xmp, display: Display):
    required_frames = yield b""  # generator initialization
    while True:
        buffer = xmp.play_buffer(required_frames * 2 * 2)
        display.update(xmp.frame_info())
        required_frames = yield buffer


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("must give mod filename to play as argument")

    device = miniaudio.PlaybackDevice(output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)

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
    display.close()
