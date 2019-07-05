"""
Python interface to the libxmp-lite library (part of https://github.com/cmatsuoka/libxmp)
plays Protracker (MOD), Scream Tracker 3 (S3M), Fast Tracker II (XM), and Impulse Tracker (IT).

This module uses CFFI to create the glue code but also to actually compile everything else too!

Author: Irmen de Jong (irmen@razorvine.net)
Software license: "MIT software license". See http://opensource.org/licenses/MIT
"""


import os
import glob
from cffi import FFI

root_include_dir = os.getcwd()


ffibuilder = FFI()
ffibuilder.cdef("""
    
#define XMP_NAME_SIZE		64	/* Size of module name and type */
#define XMP_MAX_KEYS		121	/* Number of valid keys */
#define XMP_MAX_ENV_POINTS	32	/* Max number of envelope points */
#define XMP_MAX_MOD_LENGTH	256	/* Max number of patterns in module */
#define XMP_MAX_CHANNELS	64	/* Max number of channels in module */
#define XMP_MAX_SRATE		49170	/* max sampling rate (Hz) */
#define XMP_MIN_SRATE		4000	/* min sampling rate (Hz) */
#define XMP_MIN_BPM		20	/* min BPM */

#define XMP_FORMAT_8BIT		  1  /* Mix to 8-bit instead of 16 */
#define XMP_FORMAT_UNSIGNED	  2  /* Mix to unsigned samples */
#define XMP_FORMAT_MONO		  4  /* Mix to mono instead of stereo */

/* error codes */
#define XMP_END			1
#define XMP_ERROR_INTERNAL	2	/* Internal error */
#define XMP_ERROR_FORMAT	3	/* Unsupported module format */
#define XMP_ERROR_LOAD		4	/* Error loading file */
#define XMP_ERROR_DEPACK	5	/* Error depacking file */
#define XMP_ERROR_SYSTEM	6	/* System error */
#define XMP_ERROR_INVALID	7	/* Invalid parameter */
#define XMP_ERROR_STATE		8	/* Invalid player state */

typedef char *xmp_context;
   
struct xmp_event {
	unsigned char note;		/* Note number (0 means no note) */
	unsigned char ins;		/* Patch number */
	unsigned char vol;		/* Volume (0 to basevol) */
	unsigned char fxt;		/* Effect type */
	unsigned char fxp;		/* Effect parameter */
	unsigned char f2t;		/* Secondary effect type */
	unsigned char f2p;		/* Secondary effect parameter */
	unsigned char _flag;		/* Internal (reserved) flags */
};

struct xmp_module {
	char name[XMP_NAME_SIZE];	/* Module title */
	char type[XMP_NAME_SIZE];	/* Module format */
	int pat;			/* Number of patterns */
	int trk;			/* Number of tracks */
	int chn;			/* Tracks per pattern */
	int ins;			/* Number of instruments */
	int smp;			/* Number of samples */
	int spd;			/* Initial speed */
	int bpm;			/* Initial BPM */
	int len;			/* Module length in patterns */
	int rst;			/* Restart position */
	int gvl;			/* Global volume */

	// struct xmp_pattern **xxp;	/* Patterns */
	// struct xmp_track **xxt;		/* Tracks */
	// struct xmp_instrument *xxi;	/* Instruments */
	// struct xmp_sample *xxs;		/* Samples */
	// struct xmp_channel xxc[XMP_MAX_CHANNELS]; /* Channel info */
	// unsigned char xxo[XMP_MAX_MOD_LENGTH];	/* Orders */
	
	...;
	
};


struct xmp_module_info {
	unsigned char md5[16];		/* MD5 message digest */
	int vol_base;			/* Volume scale */
	struct xmp_module *mod;		/* Pointer to module data */
	char *comment;			/* Comment text, if any */
	int num_sequences;		/* Number of valid sequences */
	struct xmp_sequence *seq_data;	/* Pointer to sequence data */
};

struct xmp_frame_info {			/* Current frame information */
	int pos;			/* Current position */
	int pattern;			/* Current pattern */
	int row;			/* Current row in pattern */
	int num_rows;			/* Number of rows in current pattern */
	int frame;			/* Current frame */
	int speed;			/* Current replay speed */
	int bpm;			/* Current bpm */
	int time;			/* Current module time in ms */
	int total_time;			/* Estimated replay time in ms*/
	int frame_time;			/* Frame replay time in us */
	void *buffer;			/* Pointer to sound buffer */
	int buffer_size;		/* Used buffer size */
	int total_size;			/* Total buffer size */
	int volume;			/* Current master volume */
	int loop_count;			/* Loop counter */
	int virt_channels;		/* Number of virtual channels */
	int virt_used;			/* Used virtual channels */
	int sequence;			/* Current sequence */

	struct xmp_channel_info {	/* Current channel information */
		unsigned int period;	/* Sample period (* 4096) */
		unsigned int position;	/* Sample position */
		short pitchbend;	/* Linear bend from base note*/
		unsigned char note;	/* Current base note number */
		unsigned char instrument; /* Current instrument number */
		unsigned char sample;	/* Current sample number */
		unsigned char volume;	/* Current volume */
		unsigned char pan;	/* Current stereo pan */
		struct xmp_event event;	/* Current track event */
		
		...;
		
	} channel_info[XMP_MAX_CHANNELS];
};

struct xmp_test_info {
	char name[XMP_NAME_SIZE];	/* Module title */
	char type[XMP_NAME_SIZE];	/* Module format */
};


extern const char *xmp_version;
extern const unsigned int xmp_vercode;

xmp_context xmp_create_context  (void);
void        xmp_free_context    (xmp_context);
int         xmp_test_module     (char *, struct xmp_test_info *);
int         xmp_load_module     (xmp_context, char *);
void        xmp_scan_module     (xmp_context);
void        xmp_release_module  (xmp_context);
int         xmp_start_player    (xmp_context, int, int);
int         xmp_play_frame      (xmp_context);
int         xmp_play_buffer     (xmp_context, void *, int, int);
void        xmp_get_frame_info  (xmp_context, struct xmp_frame_info *);
void        xmp_end_player      (xmp_context);
void        xmp_inject_event    (xmp_context, int, struct xmp_event *);
void        xmp_get_module_info (xmp_context, struct xmp_module_info *);
char      **xmp_get_format_list (void);
int         xmp_next_position   (xmp_context);
int         xmp_prev_position   (xmp_context);
int         xmp_set_position    (xmp_context, int);
int         xmp_set_row         (xmp_context, int);
int         xmp_set_tempo_factor(xmp_context, double);
void        xmp_stop_module     (xmp_context);
void        xmp_restart_module  (xmp_context);
int         xmp_seek_time       (xmp_context, int);
int         xmp_channel_mute    (xmp_context, int, int);
int         xmp_channel_vol     (xmp_context, int, int);
int         xmp_set_player      (xmp_context, int, int);
int         xmp_get_player      (xmp_context, int);
int         xmp_set_instrument_path (xmp_context, char *);
int         xmp_load_module_from_memory (xmp_context, void *, long);
int         xmp_load_module_from_file (xmp_context, void *, long);

/* External sample mixer API */
int         xmp_start_smix       (xmp_context, int, int);
void        xmp_end_smix         (xmp_context);
int         xmp_smix_play_instrument(xmp_context, int, int, int, int);
int         xmp_smix_play_sample (xmp_context, int, int, int, int);
int         xmp_smix_channel_pan (xmp_context, int, int);
int         xmp_smix_load_sample (xmp_context, int, char *);
int         xmp_smix_release_sample (xmp_context, int);
""")


libraries = []
compiler_args = []
macros =  [
            ("BUILDING_STATIC", None),
            ("PACKAGE_NAME", "\"\""),
            ("PACKAGE_TARNAME", "\"\""),
            ("PACKAGE_VERSION", "\"\""),
            ("PACKAGE_STRING", "\"\""),
            ("PACKAGE_BUGREPORT", "\"\""),
            ("PACKAGE_URL", "\"\""),
            ("STDC_HEADERS", "1"),
            ("HAVE_SYS_TYPES_H", "1"),
            ("HAVE_SYS_STAT_H", "1"),
            ("HAVE_STDLIB_H", "1"),
            ("HAVE_STRING_H", "1"),
            ("HAVE_MEMORY_H", "1"),
            ("HAVE_STRINGS_H", "1"),
            ("HAVE_INTTYPES_H", "1"),
            ("HAVE_STDINT_H", "1"),
            ("HAVE_LOCALTIME_R", "1"),
            ("HAVE_ROUND", "1"),
            ("HAVE_POWF", "1"),
            ("_REENTRANT", None),
            ("LIBXMP_CORE_PLAYER", None),
            # ("XMP_SYM_VISIBILITY", None),
            # ("HAVE_SYMVER", "0"),
            # ("HAVE_SYMVER_GNU_ASM", "0"),
            # ("HAVE_SYMVER_ASM_LABEL", "0")
            ]

if os.name == "posix":
    libraries = []  # ["m", "pthread", "dl"]
    compiler_args = ["-g1", "-O3" ]
    macros.extend([
            ("HAVE_LIBM", "1"),
            ("HAVE_UNISTD_H", "1"),
    	])


ffibuilder.set_source("_libxmplite", """
  
    #include <xmp.h>
  

""",
                      sources=[] +
                                glob.glob("libxmp-lite/src/*.c") +
                                glob.glob("libxmp-lite/src/loaders/*.c"),
                      include_dirs=["./libxmp-lite/include/libxmp-lite",
                                    "./libxmp-lite/src",
                                    "./libxmp-lite/src/loaders"
                                    ],
                      libraries=libraries,
                      define_macros = macros,
                      extra_compile_args=compiler_args)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
