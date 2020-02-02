"""

Example program that loads the given mod file in the Xmp player,
and uses it in a miniaudio playback generator function to stream the music.
All that in a tkinter GUI

(miniaudio: https://pypi.org/project/miniaudio/ )

"""

import tkinter
import tkinter.ttk
from tkinter.filedialog import askopenfilename
from tkinter.font import nametofont
import miniaudio
import libxmplite


class Gui(tkinter.Tk):
    def __init__(self):
        super().__init__()
        default_font = nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.wm_title("Python ModPlayer -- libxmplite v{} -- xmp v{}".format(libxmplite.__version__, libxmplite.xmp_version))
        self.load_button = tkinter.Button(self, text="Load module", command=self.load_module, bg="teal")
        self.load_button.pack(anchor=tkinter.W)
        # self.load_button = tkinter.Button(self, text="Pause/Unpause", command=self.pause)
        # self.load_button.pack()
        info_frame = tkinter.Frame(self, width=10)
        info_frame.title_label = tkinter.Label(info_frame, text="title")
        info_frame.title_label.grid(row=0, column=0, padx=10, sticky=tkinter.E)
        info_frame.type_label = tkinter.Label(info_frame, text="type")
        info_frame.type_label.grid(row=1, column=0, padx=10, sticky=tkinter.E)
        info_frame.channels_label = tkinter.Label(info_frame, text="channels")
        info_frame.channels_label.grid(row=2, column=0, padx=10, sticky=tkinter.E)
        info_frame.bpm_label = tkinter.Label(info_frame, text="bpm")
        info_frame.bpm_label.grid(row=3, column=0, padx=10, sticky=tkinter.E)
        info_frame.time_label = tkinter.Label(info_frame, text="time")
        info_frame.time_label.grid(row=5, column=0, padx=10, sticky=tkinter.E)
        info_frame.pos_label = tkinter.Label(info_frame, text="pos")
        info_frame.pos_label.grid(row=6, column=0, padx=10, sticky=tkinter.E)
        info_frame.pat_label = tkinter.Label(info_frame, text="pat")
        info_frame.pat_label.grid(row=7, column=0, padx=10, sticky=tkinter.E)
        info_frame.row_label = tkinter.Label(info_frame, text="row")
        info_frame.row_label.grid(row=8, column=0, padx=10, sticky=tkinter.E)
        info_frame.title_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.title_e.grid(row=0, column=1, sticky=tkinter.W)
        info_frame.type_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.type_e.grid(row=1, column=1, sticky=tkinter.W)
        info_frame.channels_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.channels_e.grid(row=2, column=1, sticky=tkinter.W)
        info_frame.bpm_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.bpm_e.grid(row=3, column=1, sticky=tkinter.W)
        info_frame.time_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.time_e.grid(row=5, column=1, sticky=tkinter.W)
        info_frame.pos_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.pos_e.grid(row=6, column=1, sticky=tkinter.W)
        info_frame.pat_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.pat_e.grid(row=7, column=1, sticky=tkinter.W)
        info_frame.row_e = tkinter.Label(info_frame, relief=tkinter.SUNKEN)
        info_frame.row_e.grid(row=8, column=1, sticky=tkinter.W)
        self.info_frame = info_frame
        self.info_frame.columnconfigure(1, minsize=200)
        self.info_frame.rowconfigure(4, minsize=20)
        self.info_frame.pack(side=tkinter.LEFT, padx=10, fill=tkinter.X, expand=tkinter.YES)
        tracks_holder = tkinter.Frame(relief=tkinter.RIDGE, height=256, width=200)
        self.tracks_holder = tracks_holder
        self.tracks_holder.pack(fill=tkinter.X, expand=tkinter.YES, padx=16, pady=16)
        # pbstyle = tkinter.ttk.Style()
        # pbstyle.theme_use("classic")
        self.audiodevice = miniaudio.PlaybackDevice(output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=44100)
        self.xmp = libxmplite.Xmp()
        self.tracks = []
        self.playing = False
        self.previous_update_time = 0

    def start(self):
        self.mainloop()

    def close(self):
        self.xmp.stop()
        self.xmp.release()
        self.audiodevice.close()

    def pause(self):
        if self.playing:
            self.audiodevice.stop()
        else:
            self.audiodevice.start(self.module_stream)
        self.playing = not self.playing

    def load_module(self):
        filename = askopenfilename(title="Select module file to play", filetypes=(
            ("Supported mod types", "*.xm *.s3m *.it *.mod"), ("Screamtracker", "*.s3m"),
            ("Protracker", "*.mod"), ("Impulsetracker", "*.it"), ("Fasttracker", "*.xm")))
        if filename:
            if self.playing:
                self.audiodevice.stop()
                self.playing = False
            self.xmp.stop()
            self.xmp.load(filename)
            self.xmp.start(self.audiodevice.sample_rate)
            modinfo = self.xmp.module_info()
            self.info_frame.title_e["text"] = modinfo.name
            self.info_frame.type_e["text"] = modinfo.type
            self.info_frame.channels_e["text"] = modinfo.chn
            self.info_frame.bpm_e["text"] = modinfo.bpm
            self.mod_global_volume = modinfo.gvl
            self.mod_vol_base = modinfo.vol_base
            self.create_tracks(modinfo.chn, modinfo.vol_base)
            self.module_stream = self.stream_module()
            next(self.module_stream)  # start the generator
            self.audiodevice.start(self.module_stream)
            self.playing = True
            self.previous_update_time = 0

    def create_tracks(self, count, max_volume):
        w = min(32, 800 // count)
        pbstyle = tkinter.ttk.Style()
        pbstyle.configure("bar.Vertical.TProgressbar", thickness=w)
        for t in self.tracks:
            t.pack_forget()
        self.tracks.clear()
        for i in range(count):
            track = tkinter.Frame(self.tracks_holder)
            track.progressbar = tkinter.ttk.Progressbar(track, orient=tkinter.VERTICAL, length=256,
                                                        maximum=max_volume, mode='determinate', style="bar.Vertical.TProgressbar")
            track.progressbar.pack(side=tkinter.TOP, padx=0, pady=0)
            track.event = tkinter.Label(track, text="★")
            track.event.pack()
            track.pack(side=tkinter.LEFT, padx=0, pady=0)
            self.tracks.append(track)

    def update_display(self, info: libxmplite.FrameInfo):
        if info.time - self.previous_update_time < 50:
            return
        self.previous_update_time = info.time
        self.info_frame.time_e["text"] = "{} / {}".format(info.time, info.total_time)
        self.info_frame.pos_e["text"] = info.pos
        self.info_frame.pat_e["text"] = info.pattern
        self.info_frame.row_e["text"] = info.row
        for track, ch in zip(self.tracks, info.channel_info[:len(self.tracks)]):
            volume = (ch.volume / self.mod_global_volume) * self.mod_vol_base
            track.progressbar["value"] = volume
            if ch.event:
                track.event["fg"] = "maroon"
            else:
                track.event["fg"] = "gray70"

    def stream_module(self):
        required_frames = yield b""  # generator initialization
        try:
            while True:
                buffer = self.xmp.play_buffer(required_frames * 2 * 2)
                self.update_display(self.xmp.frame_info())
                required_frames = yield buffer
        except libxmplite.XmpError as x:
            print("XMP Playback error!!", x)


if __name__ == "__main__":
    gui = Gui()
    gui.start()
