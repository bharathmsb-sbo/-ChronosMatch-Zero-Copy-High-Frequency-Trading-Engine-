from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        [
            "engine/matching_engine.pyx",
            "engine/order_book.pyx",
            "engine/ring_buffer.pyx",
            "engine/c_order.pyx",
            "engine/c_matcher.pyx"
        ],
        compiler_directives={
            "language_level": "3"
        }
    )
)