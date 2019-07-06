"""

Example program that loads the given mod file in the Xmp player,
and decodes a few frames from it.

"""

import sys
import libxmplite


if len(sys.argv) != 2:
    raise SystemExit("must give mod filename to play as argument")

print("Library version:", libxmplite.__version__, "   libxmp-lite version:", libxmplite.xmp_version)
print("Supported module formats: ", libxmplite.get_formats())

xmp = libxmplite.Xmp()
xmp.load(sys.argv[1])
xmp.start(44100)

info = xmp.module_info()
print("\n~~~~", info.name, "~~~~")
print("Module format:", info.type)
print("Channels:", info.chn)
print("Number of patterns:", info.pat)
print("Number of tracks:", info.trk)
print("Number of instruments:", info.ins)
print("Number of samples:", info.smp)
print("Initial speed:", info.spd)
print("Initial BPM:", info.bpm)
print("Module length in patterns:", info.length)
print("Restart position:", info.rst)
print("Global volume:", info.gvl)
print()

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
