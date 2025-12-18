from bisect import insort
from collections import deque

from helpers import calculate_buyer_scores, read_input_data, write_output_data


class PlacementSolver:
    def __init__(self, neighborhoods, home_buyers):
        names = [n['N'] for n in neighborhoods]
        buyers = [b['H'] for b in home_buyers]
        if not names:
            raise ValueError('Input defines no neighborhoods')
        if len(set(names)) != len(names):
            raise ValueError('Neighborhood names must be unique')
        if len(set(buyers)) != len(buyers):
            raise ValueError('Buyer names must be unique')
        for buyer in home_buyers:
            if len(buyer['prefs']) != len(names) or set(buyer['prefs']) != set(names):
                raise ValueError('Each buyer must rank every neighborhood exactly once')
        self.neighborhoods, self.home_buyers = neighborhoods, home_buyers
        base, remainder = divmod(len(buyers), len(names))
        self.capacities = {name: base + (index < remainder) for index, name in enumerate(names)}
        self.scores = calculate_buyer_scores(neighborhoods, home_buyers)
        self.final_selections = {name: [] for name in names}

    @classmethod
    def from_file(cls, filename):
        return cls(*read_input_data(filename))

    def optimize_placements(self):
        """Buyer-proposing deferred acceptance; ties follow buyer input order.

        Total capacity equals the buyer count and every buyer ranks every
        neighborhood, so nobody runs out of preferences before being placed.
        """
        order = {buyer['H']: index for index, buyer in enumerate(self.home_buyers)}
        prefs = {buyer['H']: buyer['prefs'] for buyer in self.home_buyers}
        self.final_selections = {name: [] for name in self.capacities}
        pending = deque(order)
        next_preference = dict.fromkeys(order, 0)
        while pending:
            buyer = pending.popleft()
            neighborhood = prefs[buyer][next_preference[buyer]]
            next_preference[buyer] += 1
            accepted = self.final_selections[neighborhood]
            insort(accepted, (buyer, self.scores[buyer][neighborhood]), key=lambda item: (-item[1], order[item[0]]))
            if len(accepted) > self.capacities[neighborhood]:
                rejected, _ = accepted.pop()
                pending.append(rejected)
        return self.final_selections

    def generate_output(self, filename):
        write_output_data(filename, self.final_selections)
