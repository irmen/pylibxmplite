"""

Example program that loads the given mod file in the Xmp player,
and decodes a few frames from it.

"""

import sys
import libxmplite


if len(sys.argv) != 2:
    raise SystemExit("must give mod filename to play as argument")

print("Supported module formats: ", libxmplite.get_formats())

xmp = libxmplite.Xmp()
xmp.load(sys.argv[1])
xmp.start(44100)

info = xmp.module_info()
print("~~~~~~", info["name"], "~~~~~")
print("module type:", info["type"])

frame_info = xmp.play_frame()
print("got", len(frame_info.buffer), "sample bytes...")
frame_info = xmp.play_frame()
print("got", len(frame_info.buffer), "sample bytes...")
frame_info = xmp.play_frame()
print("got", len(frame_info.buffer), "sample bytes...")
# ... process the frame_info data, and play the buffer...
# (see the modplayer example for actual sound playback)

print("closing down.")
xmp.release()
