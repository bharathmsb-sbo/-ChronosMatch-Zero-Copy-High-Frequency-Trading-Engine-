from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [
    Extension(
        "chronosmatch.orderbook",
        ["cython_engine/orderbook.pyx"],
        extra_compile_args=["-O3", "-march=native"],
    )
]

setup(
    packages=["chronosmatch"],
    ext_modules=cythonize(extensions, compiler_directives={"language_level": 3, "boundscheck": False, "wraparound": False, "cdivision": True}),
)
