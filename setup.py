import os
import glob
import sys
import enum
import re
import textwrap
import unittest
from setuptools import setup, Extension

if sys.version_info < (3, 5):
    raise SystemExit("requires Python 3.5 or newer")

# miniaudio_path = os.path.abspath(".")  # to make sure the compiler can find the required include files
PKG_VERSION = "0.1.dev0"  # re.search(r'^__version__\s*=\s*"(.+)"', open("miniaudio.py", "rt").read(), re.MULTILINE).groups()[0]


clibxmp = Extension('libxmp',
                    include_dirs = ["libxmp-lite/include/libxmp-lite", "libxmp-lite/src"],
                    sources = glob.glob("libxmp-lite/src/*.c"),
                    define_macros = [
                        ("BUILDING_STATIC", None),
                        # ("XMP_SYM_VISIBILITY", None),
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
                        ("HAVE_UNISTD_H", "1"),
                        ("HAVE_LIBM", "1"),
                        ("HAVE_LOCALTIME_R", "1"),
                        ("HAVE_ROUND", "1"),
                        ("HAVE_POWF", "1"),
                        ("_REENTRANT", None), 
                        ("LIBXMP_CORE_PLAYER", None),
                        # ("HAVE_SYMVER", "0"),
                        # ("HAVE_SYMVER_GNU_ASM", "0"),
                        # ("HAVE_SYMVER_ASM_LABEL", "0")
                        ],
                    extra_compile_args = []
                    )
                    

if __name__ == "__main__":
    setup(
        name="libxmplite",
        version=PKG_VERSION,
        # cffi_modules=["build_ffi_module.py:ffibuilder"],
        # include_dirs=[miniaudio_path],
        zip_safe=False,
        include_package_data=False,
        # py_modules=["miniaudio"],
        install_requires=["cffi>=1.3.0"],
        setup_requires=["cffi>=1.3.0"],
        tests_require=[],
        ext_modules=[clibxmp]
    )
