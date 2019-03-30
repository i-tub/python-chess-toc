#!/usr/bin/env python3
"""
Take a PGN file and generate an HTML file with a table of contents for the PGN
file. Each entry in the table is a board with the final position for a game,
superimposed with the plot of the engine evaluation function.
"""

import argparse
import os
import sys

import chess.engine
import chess.pgn
import jinja2

import chesstoc


def parse_args():
    """
    Parse the command-line arguments.

    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(prog='annotator', description=__doc__)
    parser.add_argument(
        "pgn_file", help="input PGN file", metavar="<filename>")
    parser.add_argument(
        "--engine",
        "-e",
        metavar='<engine>',
        help="analysis engine (default: %(default)s)",
        default="stockfish")
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--time_per_move",
        "-t",
        help="how long to spend on each move "
        "(default: %(default)s)",
        default=1.0,
        type=float,
        metavar="<seconds>")
    parser.add_argument(
        "--threads",
        help="threads for use by the engine "
        "(default: %(default)s)",
        metavar='<int>',
        type=int,
        default=4)
    parser.add_argument(
        "--maxgames",
        "-m",
        help="max number of games to evaluate. ",
        metavar='<int>',
        type=int)
    parser.add_argument(
        "--columns",
        help="number of games per row (default: %(default)s)",
        metavar='<int>',
        default=4,
        type=int)
    parser.add_argument(
        "--html", help="HTML output file with table of contents")
    parser.add_argument(
        "--template", metavar='<filename>', help="template file to use")
    parser.add_argument(
        "--css", metavar='<filename>', help="stylesheet to use")
    parser.add_argument(
        "-T",
        dest='templatepath',
        metavar='<directory>',
        action='append',
        help="directory to search for templates (may be used multiple times)")
    parser.add_argument(
        "--dryrun",
        action='store_true',
        help="skip the game analysis and plotting")

    return parser.parse_args()


def checkgame(game):
    """
    Check for PGN parsing errors and raise a ValueError if any were found.

    :param game: game to check
    :type game: chess.pgn.Game
    """
    if game.errors:
        msg = "There were errors parsing the PGN game:\n"
        for error in game.errors:
            msg += error + '\n'
        raise RuntimeError(msg)

    # Try to verify that the PGN file was readable
    if game.end().parent is None:
        raise RuntimeError(
            "Could not render the board. Is the file legal PGN?")


def pgn_reader(pgn_file):
    """
    A generator that yields the games from a PGN file as well as a dict with
    basic metadata. The dict contains the PGN headers, plus "WhiteResult" and
    "BlackResult" for convenience, as well as an "index" which is the position
    of the game in the file, counting from 1.

    :param pgn_file: input filename
    :type pgn_file: str

    :return: generator of games and metadata
    :rtype: generator of tuples (chess.pgn.Game, dict)
    """
    with open(pgn_file) as pgn:
        for index, game in enumerate(
                iter(lambda: chess.pgn.read_game(pgn), None), 1):
            try:
                checkgame(game)
            except ValueError as e:
                sys.exit(e)
            metadata = {'index': index}
            metadata.update(game.headers)
            try:
                results = metadata['Result'].split('-')
                # Fake PGN headers with each color result for convenience
                metadata['WhiteResult'], metadata['BlackResult'] = results
            except:
                pass
            yield game, metadata


def get_css():
    """
    Return the body of the default css file.

    :rtype: str
    """
    css = os.path.join(os.path.dirname(__file__), 'templates', 'chesstoc.css')
    with open(css) as fh:
        return fh.read()


def write_html(games, args):
    """
    Write an HTML file with a table of contents for a collection of games.

    :param games: game metadata, where each game is a dict with PGN headers
                  as well as the `svg_combined` filename.
    :type games: iterable of dict

    :param args: command-line arguments
    :type args: argparse.Namespace
    """
    if args.template:
        loader = jinja2.FileSystemLoader(args.templatepath or '.')
    else:
        loader = jinja2.PackageLoader('chesstoc')
    env = jinja2.Environment(loader=loader)
    template = env.get_template(args.template or 'template.html')
    with open(args.html, 'w') as fh:
        fh.write(
            template.render({
                'games': games,
                'args': args,
                'get_css': get_css
            }))


def main():
    args = parse_args()

    games = []
    for game, g in pgn_reader(args.pgn_file):
        print("Game %d: %s: %s - %s" % (g['index'], g.get('Event'),
                                        g.get('White'), g.get('Black')))
        basename = "%03d" % g['index']
        svg_plot = f'{basename}-plot.svg'
        svg_board = f'{basename}-board.svg'
        svg_combined = f'{basename}.svg'

        g['ECO'], g['Opening'] = chesstoc.classify_opening(game)
        g['svg_plot'] = svg_plot
        g['svg_board'] = svg_board
        g['svg_combined'] = svg_combined
        games.append(g)

        chesstoc.write_board(game, svg_board)

        if not args.dryrun:
            with chess.engine.SimpleEngine.popen_uci(args.engine) as engine:
                engine.configure({"Threads": args.threads})
                scores = chesstoc.analyze_game(game, engine,
                                               args.time_per_move)

            chesstoc.write_plot(scores, svg_plot)
            chesstoc.compose_svg(svg_board, svg_plot, svg_combined)

        if args.maxgames is not None and g['index'] == args.maxgames:
            break

    if args.html:
        write_html(games, args)


if __name__ == "__main__":
    main()
