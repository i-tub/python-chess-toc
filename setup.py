import setuptools
import chesstoc


with open('README.md') as fh:
    long_description = fh.read()


setuptools.setup(
    name="python-chess-toc",
    version=chesstoc.__version__,
    author=chesstoc.__author__,
    author_email=chesstoc.__email__,
    description="Create a graphical table of contents for chess games with engine analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL-3.0+",
    keywords="chess pgn svg html",
    url="https://github.com/i-tub/python-chess-toc",
    packages=["chesstoc"],
    include_package_data=True,
    python_requires=">=3.4",
    install_requires=['python-chess', 'svgutils', 'matplotlib', 'jinja2'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Board Games",
    ],
)
