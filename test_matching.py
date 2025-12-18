import random
from pathlib import Path

import pytest

from assessment import Pearl

HERE = Path(__file__).parent

REGRESSION = [
    'N N0 E:7 W:7 R:10', 'N N1 E:2 W:1 R:1', 'N N2 E:7 W:6 R:4',
    'H H0 E:5 W:4 R:2 N2>N1>N0', 'H H1 E:0 W:3 R:6 N2>N1>N0', 'H H2 E:8 W:5 R:10 N2>N1>N0',
    'H H3 E:8 W:0 R:2 N2>N1>N0', 'H H4 E:5 W:8 R:1 N0>N2>N1', 'H H5 E:6 W:1 R:8 N2>N0>N1',
]


@pytest.fixture
def solve(tmp_path):
    def run(lines):
        path = tmp_path / 'input.txt'
        path.write_text('\n'.join(lines))
        solver = Pearl(path)
        solver.optimize_placements()
        return solver
    return run


def assert_invariants(solver):
    """Every buyer placed once, occupancy balanced, and no buyer can claim a preferred seat."""
    placement = {buyer: name for name, entries in solver.final_selections.items() for buyer, _ in entries}
    all_buyers = [buyer for entries in solver.final_selections.values() for buyer, _ in entries]
    assert len(all_buyers) == len(set(all_buyers))
    assert set(placement) == {b['H'] for b in solver.home_buyers}
    sizes = [len(entries) for entries in solver.final_selections.values()]
    assert max(sizes) - min(sizes) <= 1
    for buyer in solver.home_buyers:
        name = buyer['H']
        for preferred in buyer['prefs'][:buyer['prefs'].index(placement[name])]:
            residents = solver.final_selections[preferred]
            assert len(residents) == solver.capacities[preferred]
            score = next(item['score'] for item in solver.buyers_scores[name][:-1] if item['neighborhood'] == preferred)
            assert all(score <= resident_score for _, resident_score in residents)


def test_duplicate_assignment_regression(solve):
    assert_invariants(solve(REGRESSION))


@pytest.mark.parametrize('buyer_count', range(16))
def test_balanced_complete_stable_results(solve, buyer_count):
    rng = random.Random(17 + buyer_count)
    lines = ['N N0 E:7 W:7 R:10', 'N N1 E:2 W:1 R:1', 'N N2 E:7 W:6 R:4']
    for index in range(buyer_count):
        preferences = '>'.join(rng.sample(['N0', 'N1', 'N2'], 3))
        lines.append(f'H H{index} E:{rng.randrange(11)} W:{rng.randrange(11)} R:{rng.randrange(11)} {preferences}')
    solver = solve(lines)
    assert_invariants(solver)
    first = {key: list(value) for key, value in solver.final_selections.items()}
    solver.optimize_placements()
    assert first == solver.final_selections


@pytest.mark.parametrize('lines', [
    [],
    ['N N0 E:1 W:1 R:1'] * 2,
    ['N N0 E:1 W:1 R:1', 'H H0 E:1 W:1 R:1 N9'],
    ['bad'],
    ['N N0 E:1 E:2 R:1'],
])
def test_invalid_inputs_are_rejected(solve, lines):
    with pytest.raises(ValueError):
        solve(lines)


def test_equal_scores_favor_earlier_buyer(solve):
    solver = solve(['N N0 E:1 W:1 R:1', 'N N1 E:1 W:1 R:1',
                    'H B E:1 W:1 R:1 N0>N1', 'H A E:1 W:1 R:1 N0>N1'])
    assert solver.final_selections == {'N0': [('B', 3)], 'N1': [('A', 3)]}


def test_bundled_fixture_reproduces_generated_output(tmp_path):
    solver = Pearl(HERE / 'input.txt')
    solver.optimize_placements()
    assert_invariants(solver)
    result = tmp_path / 'output.txt'
    solver.generate_output(result)
    assert result.read_text() == (HERE / 'generated_output.txt').read_text()
