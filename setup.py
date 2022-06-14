#!/usr/bin/python3

import setuptools
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

__version__ = "1.1.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_extensions():
    sources = ["csrc/coco_eval/cocoeval.cpp", "csrc/vision.cpp"]
    print(f"Sources: {sources}")

    ext_modules = [
        Pybind11Extension(
            name="fast_coco_eval._C",
            sources=sources,
            define_macros=[('VERSION_INFO', __version__)],
        )
    ]
    return ext_modules

setup(
    name="faster-coco-eval",
    version=__version__,
    author="MiXaiLL76",
    python_requires=">=3.6",
    ext_modules=get_extensions(),
    packages=setuptools.find_packages(),
    cmdclass={"build_ext": build_ext},
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'numpy',
        "pybind11",
        "pycocotools"
    ],
)