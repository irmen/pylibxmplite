"""

Example program that loads the given mod file in the Xmp player,
and uses it in a miniaudio playback generator function to stream the music.

(miniaudio: https://pypi.org/project/miniaudio/ )

"""

import sys
import miniaudio
import libxmplite


def stream_module(xmp: libxmplite.Xmp):
    required_frames = yield b""  # generator initialization
    while True:
        buffer = xmp.play_buffer(required_frames * 2 * 2)
        info = xmp.frame_info()
        print("\r #", info.time, "pos:", info.pos, "pat:", info.pattern, "row:", info.row, end="     ", flush=True)
        required_frames = yield buffer


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("must give mod filename to play as argument")

    device = miniaudio.PlaybackDevice(output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=48000)

    xmp = libxmplite.Xmp()
    xmp.load(sys.argv[1])
    xmp.start(device.sample_rate)

    stream = stream_module(xmp)
    next(stream)  # start the generator
    device.start(stream)

    info = xmp.module_info()
    print("~~~~~~~~~~", info["name"], "~~~~~~~~~")
    print(info["type"], " file playing in the background. Press enter to stop playback!\n")
    input()

    xmp.stop()
    xmp.release()
    device.close()
