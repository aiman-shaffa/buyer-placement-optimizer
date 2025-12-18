import argparse
import sys
from pathlib import Path

from helpers import format_placements, parse_input, read_input_data
from solver import PlacementSolver

BUNDLED_INPUT = Path(__file__).with_name('input.txt')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Balance buyers across ranked neighborhoods')
    parser.add_argument('input', nargs='?', default=str(BUNDLED_INPUT),
                        help='input file, or - for stdin (default: the bundled input.txt)')
    parser.add_argument('output', nargs='?', default='-',
                        help='file to write placements to (default: stdout)')
    args = parser.parse_args(argv)
    try:
        records = parse_input(sys.stdin) if args.input == '-' else read_input_data(args.input)
        solver = PlacementSolver(*records)
        solver.optimize_placements()
        if args.output == '-':
            sys.stdout.write(format_placements(solver.final_selections))
        else:
            solver.generate_output(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
