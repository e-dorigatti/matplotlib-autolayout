"""
setup file
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="matplotlib-autolayout",
    version="0.0.1",
    author="e-dorigatti",
    author_email="emilio.dorigatti@gmail.com",
    description="ASCII-art-based layout generator for matplotlib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e-dorigatti/matplotlib-autolayout/",
    packages=setuptools.find_packages(),
    install_requires=["click>=7.0.0", "matplotlib>=3.0.0",],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
