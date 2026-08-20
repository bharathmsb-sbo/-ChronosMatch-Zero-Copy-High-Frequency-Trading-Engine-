from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension(
        "order_book",
        ["order_book.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
    )
]

setup(
    name="chronosmatch",
    ext_modules=cythonize(extensions, language_level="3"),
)
