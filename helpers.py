ATTRIBUTES = ('E', 'W', 'R')


def parse_input(lines):
    """Split N (neighborhood) and H (buyer) records into two lists of dicts."""
    neighborhoods, home_buyers = [], []
    for line_number, line in enumerate(lines, 1):
        parts = line.split()
        if not parts:
            continue
        if parts[0] not in ('N', 'H') or len(parts) != (5 if parts[0] == 'N' else 6):
            raise ValueError(f'Invalid record on line {line_number}')
        record = {parts[0]: parts[1], **parse_attributes(parts[2:5], line_number)}
        if parts[0] == 'N':
            neighborhoods.append(record)
        else:
            record['prefs'] = parts[5].split('>')
            home_buyers.append(record)
    return neighborhoods, home_buyers


def read_input_data(filename):
    with open(filename, encoding='utf-8') as file:
        return parse_input(file)


def parse_attributes(tokens, line_number):
    values = {}
    for token in tokens:
        key, separator, value = token.partition(':')
        if not separator or key not in ATTRIBUTES or key in values:
            raise ValueError(f'Expected one each of E, W, R on line {line_number}, got {token!r}')
        try:
            values[key] = int(value)
        except ValueError:
            raise ValueError(f'{key} must be an integer on line {line_number}, got {value!r}') from None
    return values


def format_placements(selections):
    """One line per neighborhood, buyers listed by descending score."""
    lines = []
    for neighborhood, assigned_buyers in selections.items():
        ranked = sorted(assigned_buyers, key=lambda x: x[1], reverse=True)
        lines.append(' '.join([f'{neighborhood}:', *(f'{h}({s})' for h, s in ranked)]))
    return ''.join(line + '\n' for line in lines)


def write_output_data(filename, selections):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(format_placements(selections))


def calculate_buyer_scores(neighborhoods, home_buyers):
    """Compatibility of every buyer with every neighborhood: the dot product of their E, W and R."""
    return {
        buyer['H']: {hood['N']: sum(buyer[key] * hood[key] for key in ATTRIBUTES) for hood in neighborhoods}
        for buyer in home_buyers
    }
