import pandas as pd
from pandas import DataFrame
from tabulate import tabulate
from string import ascii_uppercase
from itertools import combinations
from collections import defaultdict


def put_states_in_array(table=DataFrame()):
    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            nonterminal_transition = table.iloc[lin, col]
            if nonterminal_transition == 'eps':
                table.iloc[lin, col] = [nonterminal_transition]
            elif nonterminal_transition is None:
                continue
            else:
                table.iloc[lin, col] = list(nonterminal_transition)

    return table


def define_nonterminals_transitions_count(table=DataFrame()):
    nonterminals_transitions = {
        terminal: 0
        for terminal in table.iloc[:, 0]
        if terminal != table.iloc[0, 0]
    }

    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            states = table.iloc[lin, col]
            if states is None:
                continue
            else:
                for state in states:
                    if (state in ascii_uppercase) and (state != table.iloc[lin, 0]):
                        nonterminals_transitions.setdefault(state, 0)
                        nonterminals_transitions[state] += 1

    return nonterminals_transitions


def define_useless_terminals(table=DataFrame()):
    useless_nonterminals = []
    for lin in range(1, table.shape[0]):
        to_delete = True
        has_single_terminal = False
        line_non_terminals = []
        for col in range(1, table.shape[1]):
            if table.iloc[lin, col] is not None:
                states = table.iloc[lin, col]
                for state in states:
                    if state not in ascii_uppercase:
                        if len(states) == 1:
                            to_delete = False
                            has_single_terminal = True
                    else:
                        line_non_terminals.append(state)

        if has_single_terminal is False:
            for non_terminal in line_non_terminals:
                if non_terminal is table.iloc[lin, 0]:
                    to_delete = True
                else:
                    to_delete = False

        if to_delete is True:
            useless_nonterminals.append(table.iloc[lin, 0])

    return useless_nonterminals


def delete_unavailable_useless_terminals(table=DataFrame()):
    while True:
        nonterminals_transitions = define_nonterminals_transitions_count(table)
        useless_nonterminals = define_useless_terminals(table)
        unavailable_nonterminals = []

        for key in nonterminals_transitions.keys():
            if nonterminals_transitions[key] == 0:
                unavailable_nonterminals.append(key)

        for lin in range(1, table.shape[0]):
            if table.iloc[lin, 0] in unavailable_nonterminals:
                table = table.drop(index=lin)

        for lin in range(1, table.shape[0]):
            if table.iloc[lin, 0] in useless_nonterminals:
                table = table.drop(index=lin)

        for lin in range(1, table.shape[0]):
            for col in range(1, table.shape[1]):
                states = table.iloc[lin, col]
                if states is not None:
                    for state in states:
                        if state in useless_nonterminals:
                            table.iloc[lin, col] = states.remove(state)

        table = resolve_left_empty_cells(table)

        is_edited = False

        if len(useless_nonterminals) > 0:
            print(
                "Обнаружены и удалены бесполезные нетерминалы:",
                "\n",
                "❌ ",
                "".join(useless_nonterminals)
                if len(useless_nonterminals) > 1
                else ", ".join(useless_nonterminals),
                sep=""
            )
            is_edited = True
        if len(unavailable_nonterminals) > 0:
            print(
                "Обнаружены и удалены недоступные нетерминалы:",
                "\n",
                "❌ ",
                "".join(unavailable_nonterminals)
                if len(unavailable_nonterminals) > 1
                else ", ".join(unavailable_nonterminals),
                sep=""
            )
            is_edited = True

        if (not useless_nonterminals) and (0 not in nonterminals_transitions.values()):
            if is_edited:
                print("Проблемы устранены:")
            else:
                print("Проблемы не обнаружены:")
            break

    return table


def resolve_epsilon_rules(table=DataFrame()):
    is_epsilon_resolved = False

    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            states = table.iloc[lin, col]

            if states is not None:
                if len(states) > 1:

                    for i in range(len(states)):
                        if (states[i] in ascii_uppercase) and (states[i] is not table.iloc[lin, 0]):

                            matching_row = table[table.iloc[:, 0] == states[i]]
                            if not matching_row.empty:

                                line_to_check = matching_row.iloc[0]
                                is_eps = any(
                                    'eps' in value
                                    for value in line_to_check
                                    if value is not None
                                )

                                if is_eps:
                                    is_epsilon_resolved = True
                                    new_alternatives = list(
                                        combinations(
                                            [
                                                state
                                                for state in states
                                                if state != table.iloc[lin, 0]
                                            ],
                                            2
                                        )
                                    )
                                    single_elements = [
                                        (state,)
                                        for state in states
                                        if state not in ascii_uppercase
                                    ]
                                    new_alternatives = new_alternatives + single_elements

                                    add_alternatives_to_table(
                                        table,
                                        lin,
                                        new_alternatives
                                    )

                                    print(
                                        "Устраним eps-правило: ",
                                        "\n",
                                        "✏️ Нетерминал: ", table.iloc[lin, 0],
                                        "\n",
                                        "➕ Новые элементы: ", ' | '.join(''.join(na) for na in new_alternatives)
                                    )

            if table.iloc[lin, col] is not None:
                if 'eps' in table.iloc[lin, col]:
                    table.iloc[lin, col] = None

    if is_epsilon_resolved is False:
        print('Эпсилон-правила не обнаружены.')

    table = resolve_nan(table)
    table = resolve_left_empty_cells(table)

    return table


def resolve_chained_rules(table=DataFrame()):
    chained_lines = []
    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            states = table.iloc[lin, col]
            if states and len(states) == 1 and states[0] in ascii_uppercase:
                chained_lines.append(table.iloc[lin, 0])

    if chained_lines:
        print("Обнаружены цепные правила для данных нетерминалов: ")
        for chained_line in chained_lines:
            print(
                "✔️ ",
                chained_line,
                sep=""
            )
        print("Устраним их:")
        while chained_lines:
            chained_line_name = chained_lines.pop()
            target_line = get_target_line(table, chained_line_name)
            target_name = target_line[0]
            target_values = target_line[1]

            chained_line_row_index = table[
                table["Нетерминал"] == chained_line_name
                ].index[0]
            for col in table.columns[1:]:
                if table.at[chained_line_row_index, col] == target_name:
                    table.at[chained_line_row_index, col] = None

            for i in range(len(target_values)):
                add_alternatives_to_table(
                    table,
                    table.loc[
                        table["Нетерминал"] == chained_line_name
                        ]
                    .index[0],
                    target_values[i]
                )

            table = table_without_arrays(table)
            table = resolve_left_empty_cells(table)
    else:
        print("Цепные правила не обнаружены")

    return table


def get_target_line(table=DataFrame(), chained_line_name=str):
    chained_line = table[
        table["Нетерминал"] == chained_line_name
        ]

    target_line = []
    if not chained_line.empty:
        chained_line_length = chained_line.shape[1]
        for col in range(1, chained_line_length):
            chained_line_states = chained_line.iloc[0, col]
            if (chained_line_states is not None) and (len(chained_line_states) == 1) and (
                    chained_line_states[0] in ascii_uppercase):
                chain = chained_line_states[0]
                target_values = [
                    [
                        value
                        for value in row[1:]
                        if value is not None
                    ]
                    for row in table[
                        table["Нетерминал"] == chain
                        ]
                    .values
                ]
                target_line = [chain, target_values]

    return target_line


def resolve_left_factoring_rules(table=DataFrame()):
    while True:
        rating = get_left_factoring_ratings(table)
        if not rating:
            print("Левая факторизация устранена.")
            break
        else:
            nonterminals = list(rating.keys())

            for lin in range(table.shape[0]):
                elements = defaultdict(list)

                flag_nonterminals = []
                for key, value in rating.items():
                    for flag_terminal, rate in value.items():
                        flag_nonterminals.append(flag_terminal)

                for col in range(1, table.shape[1]):
                    if table.iloc[lin, 0] in nonterminals:
                        states = table.iloc[lin, col]
                        if (states is not None) and (states[0] in flag_nonterminals):
                            initial_state = states[1:]
                            states = [
                                states[0],
                                "F́_" +
                                table.iloc[lin, 0] +
                                states[0]
                            ]
                            table.iloc[lin, col] = states

                            elements[
                                "F́_" +
                                table.iloc[lin, 0] +
                                states[0]
                                ].append(initial_state)

                new_row = []
                for new_nonterminal, new_elements in elements.items():
                    new_row.append(new_nonterminal)
                    for new_element in new_elements:
                        new_row.append(new_element)
                    table.loc[len(table)] = new_row + [None] * (len(table.columns) - len(new_row))
                    new_row = []
            break

    table = remove_duplicates_from_rows(table)
    table = resolve_nan(table)
    table = resolve_left_empty_cells(table)
    table = table_without_arrays(table)
    return table


def get_left_factoring_ratings(table=DataFrame()):
    non_singular_states = {
        table.iloc[lin, 0]: [
            "".join(table.iloc[lin, col])
            for col in range(1, table.shape[1])
            if table.iloc[lin, col] is not None and len(table.iloc[lin, col]) > 1
        ]
        for lin in range(table.shape[0])
    }

    first_values_rating = {
        key: {
            state[0]: sum(1 for s in value if s[0] == state[0])
            for state in value
        }
        for key, value in non_singular_states.items()
    }

    final_filtered_rating = {
        key: {k: v for k, v in inner_dict.items() if v >= 2}
        for key, inner_dict in first_values_rating.items()
    }

    final_filtered_rating = {key: value for key, value in final_filtered_rating.items() if value}

    print("Будем итерироваться по следующему рейтингу перехода:")
    for nonterminal, rates in first_values_rating.items():
        print("Нетерминал перехода:", nonterminal)
        for element, rate in rates.items():
            if rate > 1:
                print("✔️ Элемент, рейтинг: ", element, ", ", rate, sep="")
            else:
                print("❌ Элемент, рейтинг: ", element, ", ", rate, sep="")

    return final_filtered_rating


def resolve_direct_left_recursion(table):
    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            states = table.iloc[lin, col]
            if states is not None:
                nonterminal = states[0]
                if table.iloc[lin, 0] == nonterminal:
                    elements = states[1:]
                    table.iloc[lin, col] = None
                    new_nonterminal = "Ŕ_" + nonterminal
                    table.loc[len(table)] = (
                            [
                                new_nonterminal,
                                elements + new_nonterminal,
                                elements
                            ]
                            + [None] * (len(table.columns) - 3)
                    )

    with pd.option_context('mode.chained_assignment', None):
        table = resolve_left_empty_cells(table)
        for lin in range(table.shape[0]):
            for col in range(1, table.shape[1]):
                states = table.iloc[lin, col]
                if states is not None:
                    nonterminal = table.iloc[lin, 0]
                    if ("Ŕ_" + nonterminal) in table.iloc[:, 0].values:
                        table.iloc[lin, col] = states + "Ŕ_" + nonterminal

    return table


def format_dict(dictionary):
    if dictionary is None:
        dictionary = dict()
    formatted_output = []
    for key, values in dictionary.items():
        formatted_output.append(f"{key}: {values}")

    return "\n".join(formatted_output)


def format_table(table=DataFrame()):
    return tabulate(table,
                    headers="keys",
                    tablefmt="grid",
                    showindex=False
                    )


def table_without_arrays(table=DataFrame()):
    for lin in range(table.shape[0]):
        for col in range(1, table.shape[1]):
            value = table.iloc[lin, col]
            if value is not None:
                table.iloc[lin, col] = "".join(value)

    return table


def resolve_nan(table=DataFrame()):
    table = table.applymap(lambda x: None if isinstance(x, (float, int)) and pd.isna(x) else x)
    return table


def resolve_left_empty_cells(table=DataFrame()):
    changes_made = True
    while changes_made:
        changes_made = False

        for lin in range(table.shape[0]):
            for col in range(1, table.shape[1]):
                if table.iloc[lin, col] is not None:
                    if table.iloc[lin, col - 1] is None:
                        table.iloc[lin, col - 1] = table.iloc[lin, col]
                        table.iloc[lin, col] = None
                        changes_made = True

    table = table.dropna(axis=1, how='all')

    return table


def remove_duplicates_from_rows(table):
    for lin in range(table.shape[0]):
        unique_values = set()
        for col in range(1, table.shape[1]):
            if str(table.iloc[lin, col]) in unique_values:
                table.iloc[lin, col] = None
            else:
                unique_values.add(str(table.iloc[lin, col]))

    table = table.dropna(axis=1, how='all')

    return table


def add_alternatives_to_table(table, lin, new_alternatives):
    for new_alternative in new_alternatives:
        num_old_alternatives = table.shape[1] - 1
        new_column_name = "Альт." + str(num_old_alternatives + 1)

        if new_column_name not in table.columns:
            table[new_column_name] = None

        table.at[lin, new_column_name] = list(new_alternative)

