"""Setup script for Long March game."""
from setuptools import setup, find_packages

setup(
    name="long_march",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "long-march = long_march.main:main",
        ],
    },
    author="Your Name",
    description="Long March: Red Star Over China — historical survival narrative",
    license="MIT",
)

