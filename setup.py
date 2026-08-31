from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        "engine/matching_engine.pyx",
        compiler_directives={
            "language_level": "3"
        }
    )
)