def read_input_data(filename):
  neighborhoods, home_buyers = [], []

  with open(filename, encoding='utf-8') as file:
    for line_number, line in enumerate(file, 1):
      parts = line.split()
      if not parts:
        continue
      if parts[0] not in ('N', 'H') or len(parts) != (5 if parts[0] == 'N' else 6):
        raise ValueError(f'Invalid record on line {line_number}')
      data_dict = {parts[0]: parts[1]}
      data_dict.update(parse_attributes(parts[2:5], line_number))

      if parts[0] == 'N':
        neighborhoods.append(data_dict)
      elif parts[0] == 'H':
        # Since home buyer have an additional attribute of preferences, we save that as well
        data_dict['prefs'] = parts[5].split('>')
        home_buyers.append(data_dict)

  return neighborhoods, home_buyers

def parse_attributes(tokens, line_number):
  values = {}
  for token in tokens:
    key, separator, value = token.partition(':')
    if not separator or key not in ('E', 'W', 'R') or key in values:
      raise ValueError(f'Expected one each of E, W, R on line {line_number}, got {token!r}')
    try:
      values[key] = int(value)
    except ValueError:
      raise ValueError(f'{key} must be an integer on line {line_number}, got {value!r}') from None
  return values

def write_output_data(filename, selections):
  with open(filename, 'w', encoding='utf-8') as file:
    for neighborhood, assigned_buyers in selections.items():
      ranked = sorted(assigned_buyers, key=lambda x: x[1], reverse=True)
      file.write(' '.join([f'{neighborhood}:', *(f'{h}({s})' for h, s in ranked)]) + '\n')

def calculate_buyer_scores(neighborhoods, home_buyers):
  """
  Calculate compatibility scores between home buyers and neighborhoods by using the
  dot product of the home buyer's goals and the neighborhood scores.
  """
  buyers_scores = {}

  for buyer in home_buyers:
    current_scores = []

    for neighborhood in neighborhoods:
      current_scores.append({
        'neighborhood': neighborhood['N'],
        'score': buyer['E'] * neighborhood['E'] + buyer['W'] * neighborhood['W'] + buyer['R'] * neighborhood['R'],
      })

    # Sort buyers by their scores in each neighborhood in descending order
    buyers_scores[buyer['H']] = sorted(current_scores, key=lambda item: item['score'], reverse=True)
    buyers_scores[buyer['H']].append(buyer['prefs'])

  return buyers_scores
