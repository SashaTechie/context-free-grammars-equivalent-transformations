#Table
from pandas import DataFrame

def example_table():
    columns = \
        ['Нетерминал', 'Альт. 1', 'Альт. 2', 'Альт. 3', 'Альт. 4']
    data = [
        ['E', 'T', 'E+T', 'E-T', 'eps'],
        ['T', 'F', 'F*T', 'F/T', 'eps'],
        ['F', 'G', 'Fn', 'n'],
        ['G', 'Gm'],
        ['H', 'Hh', 'h']
    ]
    table = DataFrame(data, columns=columns)
    return table
