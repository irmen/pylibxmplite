[![saythanks](https://img.shields.io/badge/say-thanks-ff69b4.svg)](https://saythanks.io/to/irmen)
[![Latest Version](https://img.shields.io/pypi/v/libxmplite.svg)](https://pypi.python.org/pypi/libxmplite/)


# Python libxmp-lite  modplayer

This module (pun intented) provides a Python interface to the
libxmp-lite (a cut-down version of [libxmp](https://github.com/cmatsuoka/libxmp) library.
The libxmp-lite library is linked into the extenson module, no additional
fiddling and installation is required. 

*Requires Python 3.5 or newer.  Also works on pypy3 (because it uses cffi).* 

The library is primarily distributed in source form so you need a C compiler to build and install this
(note: the setup script takes care of the actual compilation process, no need to worry about compiling things yourself).
For Linux and Mac this shouldn't be a problem. For Windows users, if the correct binary install
is not available on pypi, you'll have to get it to compile as well which may be a bit of a hassle 
on this platform. You have to make sure that the required tools that allow you to compile Python extension modules
are installed (Visual Studio or the VC++ build tools).
 
Software license for these Python bindings: MIT

Software license for the libxmp library: LGPL


## Example

### Most basic mod decoding

```python
import libxmplite

print("Supported module formats: ", libxmplite.get_formats())

xmp = libxmplite.Xmp()
xmp.load("amiga.mod")
xmp.start(44100)

info = xmp.module_info()    # grab name, comment, number of patterns, ....

frame_info = xmp.play_frame()

# ... process the frame buffer bytes ...
# ... repeat until satisfied

xmp.release()
```

There's also a ``xmp.play_buffer()`` method that is more suited to be integrated
into an async pull API.

There's also extensive documentation for the underlying [libxmp API](https://github.com/cmatsuoka/libxmp/blob/master/docs/libxmp.rst).
