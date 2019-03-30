# python-chess-toc
Create a graphical table of contents for chess games with engine analysis

The `chesstoc` package takes a PGN file and generates an HTML file with a graphical table of contents for the PGN
file. Each table entry is a board with the final position for a game,
superimposed with the plot of the engine evaluation function.

For example,

    python3 -m chesstoc --time 1.0 --html candidates.html candidates.pgn --col 2

analyzes the games from candidates.pgn, spending one second per move, and produces an HTML file with a two-column table that looks like this:

![TOC for candidates.pgn](https://raw.githubusercontent.com/i-tub/python-chess-toc/master/examples/screenshot.png)

## Installation

    pip install python-chess-toc

## Dependencies
* python 3
* python-chess
* jinja2
* matplotlib
* svgutils
* a UCI chess engine (only tested with Stockfish)

## Acknowledgements

Many thanks to the authors of all the packages above. The present package is merely a thin layer of glue that gets `python-chess` to do the parsing, talking to the engine, and board rendering, and then feeds the numbers into `matplotlib` and `svgutils` to produce the figures, and finally uses `jinja2` to generate the HTML. Also, I borrowed the opening database from https://github.com/niklasf/eco and borrowed some ideas from https://github.com/rpdelaney/python-chess-annotator.

## License
python-chess-toc is licensed under the GPL 3 (or any later version at your option). Check out LICENSE.txt for the full text.
