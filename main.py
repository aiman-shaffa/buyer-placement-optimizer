import argparse
from pathlib import Path

from solver import PlacementSolver


def main():
    parser = argparse.ArgumentParser(description='Balance buyers across ranked neighborhoods')
    parser.add_argument('input', nargs='?', default=str(Path(__file__).with_name('input.txt')))
    parser.add_argument('output', nargs='?', default='generated_output.txt')
    args = parser.parse_args()
    try:
        solver = PlacementSolver.from_file(args.input)
        solver.optimize_placements()
        solver.generate_output(args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
