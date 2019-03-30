"""
Functions to analyze a game an plot the resulting evaluation on top of a
diagram of the final position of the game.
"""

__author__ = "Ivan Tubert-Brohman"
__email__ = "ivan.tubert@gmail.com"
__version__ = "0.1.1"

import itertools
import json
import os

import chess
import chess.engine
import chess.pgn
import chess.svg

import matplotlib.pyplot as plt

from svgutils import compose

# Used to convert mating positions to centipawns
MAX_SCORE = 10000

# Figure size in points
SIZE = 360

# Margins as fraction of the figure area which will be covered by the axes
LEFT_BOTTOM_MARGIN = 0.05
TOP_RIGHT_MARGIN = 0.98


def analyze_game(game, engine, time_per_move=1.0, verbose=False):
    """
    Analyze a game using an engine and return the numerical evaluation of
    each position.

    :param game: game to analyze
    :type game: chess.pgn.Game

    :param game: engine to use for analysis
    :type game: chess.engine.SimpleEngine

    :param time_per_move: time to spend on each full move (2 plies), in seconds
    :type time_per_move: float

    :return: the evaluation for every position in the game's mainline,
        in full points from White's point of view.
    :rtype: list of float
    """
    limit = chess.engine.Limit(time=time_per_move / 2)

    scores = []
    for ply, node in enumerate(itertools.chain([game], game.mainline())):
        board = node.board()
        result = engine.play(board, limit, info=chess.engine.INFO_SCORE)
        score = result.info['score']
        besteval = score.white().score(mate_score=MAX_SCORE) / 100
        if verbose:
            print(ply, besteval, (ply + 1) // 2, node.san() if ply else '')
        scores.append(besteval)
    return scores


def classify_opening(game):
    """
    :param game: game to analyze
    :type game: chess.pgn.Game

    :return: ECO code and opening name
    :rtype: tuple (str, str)
    """
    ecofile = os.path.join(os.path.dirname(__file__), 'eco/eco.json')
    ecodata = json.load(open(ecofile, 'r'))
    openings = {o['f']: o for o in ecodata}

    for node in reversed(game.mainline()):
        eco_fen = ' '.join(node.board().fen().split()[:3])
        opening = openings.get(eco_fen)
        if opening:
            return opening['c'], opening['n']
    return None, None


def write_plot(scores, filename, scale=8.0):
    """
    Write a plot of the scores to `filename`. The Y axis ranges from -scale to
    +scale, and the X axis is the full move number from 0 to the end of the
    game.

    :param scores: evaluation for every position in the game's mainline,
            in full points from White's point of view.
    :type scores: list of float

    :param filename: file to write
    :type filename: str

    :param scale: limit of Y axis
    :type scale: float
    """
    # shift margin a bit to make sure line is still visible when capped
    cap = scale - 0.05
    y = [min(max(s, -cap), cap) for s in scores]
    x = [0.5 * i for i in range(len(y))]

    size_in_inches = SIZE / 72.0
    fig, ax = plt.subplots(figsize=(size_in_inches, size_in_inches))

    ax.set_ylim(-scale, scale)
    ax.set_xlim(0, max(x))
    ax.plot(x, y, color='black')

    # Leave only a minimal amount of padding (e.g. for the axis labels).
    fig.subplots_adjust(LEFT_BOTTOM_MARGIN, LEFT_BOTTOM_MARGIN,
                        TOP_RIGHT_MARGIN, TOP_RIGHT_MARGIN)

    fig.savefig(filename, transparent=True)
    plt.close(fig)


def write_board(game, filename, size=SIZE):
    """
    Write a diagram of the final position of the game to an SVG file.

    :param game: game to create the figure for
    :type game: chess.pgn.Game

    :param filename: file to write
    :type filename: str

    :param size: size of the figure, passed to chess.svg.board().
    :type size: int
    """
    with open(filename, mode='w') as fh:
        fh.write(
            chess.svg.board(game.end().board(), size=size, coordinates=False))


def compose_svg(svg_board, svg_plot, svg_combined):
    """
    Create a combined SVG in which the board image is put in the background of
    the axes area of the plot image.

    :param svg_board: filename of existing board image.
    :type svg_board: str

    :param svg_plot: filename of existing plot image.
    :type svg_plot: str

    :param svg_combined: filename of combined image, to be written.
    :type svg_combined: str
    """
    scale = TOP_RIGHT_MARGIN - LEFT_BOTTOM_MARGIN
    xdel = LEFT_BOTTOM_MARGIN * SIZE
    ydel = (1.0 - TOP_RIGHT_MARGIN) * SIZE
    compose.Figure(
        SIZE, SIZE,
        compose.Panel(compose.SVG(svg_board).scale(scale).move(xdel, ydel)),
        compose.Panel(compose.SVG(svg_plot))).save(svg_combined)
