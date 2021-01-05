import re
import os
import sys
from setuptools import setup

modules_path = os.path.abspath(".")  # to make sure the compiler can find the required include files
PKG_VERSION = re.search(r'^__version__\s*=\s*"(.+)"', open("libxmplite.py", "rt").read(), re.MULTILINE).groups()[0]


if __name__ == "__main__":
    setup(
        name="libxmplite",
        version=PKG_VERSION,
        cffi_modules=["build_ffi_module.py:ffibuilder"],
        include_dirs=[modules_path],
        zip_safe=False,
        include_package_data=False,
        py_modules=["libxmplite"],
        install_requires=["cffi>=1.3.0"],
        setup_requires=["cffi>=1.3.0"],
        tests_require=[]
    )
