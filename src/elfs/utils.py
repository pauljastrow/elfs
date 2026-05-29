from argparse import Namespace

from typing import Union

from pathlib import Path

from tabulate import tabulate

from elfs.data.access.utils import ensure_storage_dir


def validate_input(
        input_arg: Namespace,
        arg_name: str,
        number: bool = False,
        multiple: bool = False,
        interval: bool = False,
        boolean: bool = False,
) -> Union[str, int, list[str], list[int], set[tuple[int, int]], set[tuple[str, str]]]:
    """
    Validate user input arguments from cli

    :param input_arg: User input argument from cli
    :param arg_name: Name of input variable
    :param number: Indication whether input is numeric
    :param multiple: Indication whether input is a list of values
    :param interval: Indication whether input is an interval
    :param boolean: Indication whether input is an boolean
    :return: Validated user input argument
    """

    # define input variable
    temp = input_arg

    # demand user input
    if not temp:
        temp = input(f' {f'{arg_name}: ':<45}')

    # data pre-processing
    temp = temp.replace('; ', ';')

    # validate intervals
    if interval:

        temp_set = set()

        # split string into intervals
        tuples = temp.split('];[')
        for t in tuples:
            temp_min, temp_max = t.strip('[]').split(',')
            if number:
                try:
                    temp_min = int(temp_min)
                except ValueError:
                    temp_min = float(temp_min)

                try:
                    temp_max = int(temp_max)
                except ValueError:
                    temp_max = float(temp_max)

            temp_set.add((temp_min, temp_max))

        temp = temp_set

    # validate lists
    elif multiple:
        temp = temp.split(';')
        if number:
            new_temp = list()
            for t in temp:
                try:
                    new_temp.append(int(t))
                except ValueError:
                    new_temp.append(float(t))
            temp = new_temp

    # validate numbers
    elif number:
        try:
            temp = int(temp)
        except ValueError:
            temp = float(temp)

    # validate boolean
    elif boolean:
        temp = temp.lower() == 'true'

    return temp


def validate_log_name(log_name: str) -> str:
    """
    Validate whether log name exists.

    :param log_name: Name of (stored) event log
    :return: Log name
    """

    # ensure presence of storage directory
    dir_path = Path('logs')
    ensure_storage_dir(dir_path)

    # format log name
    log_name = log_name.removesuffix('.xes')
    file_path = Path(f'logs/{log_name}.xes')

    # check if file path leads to a file
    if not file_path.is_file():
        raise IsADirectoryError(f'Event log with name {log_name} not found.')

    return log_name


def validate_reference_model(model_name: str) -> str:
    """
    Validate whether model name exists.

    :param model_name: Name of (stored) reference model
    :return: Model name
    """

    # check whether model directory exists
    dir_path = Path(f'models/{model_name.removesuffix('_n')}')
    if not dir_path.exists():
        raise IsADirectoryError(f'Model with name {model_name} not found.')

    # format model name
    model_name = model_name.removesuffix('.pnml')
    file_path = Path(f'models/{model_name.removesuffix('_n')}/{model_name}.pnml')

    # check if file path leads to a file
    if not file_path.is_file():
        raise IsADirectoryError(f'Model with name {model_name} not found.')

    return model_name


def print_pairwise_similarity_analysis_output(
        model_names: list[str],
        similarity_scores: dict[str, float],
        log_complexity_kpis: dict[str, dict[str, float]],
        model_complexity_kpis: dict[str, dict[str, float]],
        n_model: str,
) -> None:
    """
    Prints pairwise similarity analysis output, which includes the base model, the comparison model, and optionally its
    negative model with both log and model complexity measures.

    :param model_names: Names of models to print
    :param similarity_scores: Similarity scores of models to print
    :param log_complexity_kpis: Log complexity kpi values
    :param model_complexity_kpis: Model complexity kpi values
    :param n_model: Indication of inclusion of negative model
    :return: None
    """

    # provide log complexity kpis

    if n_model == 'true':
        print(
            ' Log Complexity Analysis\n'
            f' {f'Model: ':<40}{f'{model_names[0]}':<20} {f'{model_names[1]}':<20} {f'{model_names[2]}':<20}'
        )
        for kpi, values in log_complexity_kpis.items():
            print(
                f' {f'{kpi}: ':<40}{f'{values[model_names[0]]}':<20} {f'{values[model_names[1]]}':<20} '
                f'{f'{values[model_names[2]]}':<20}'
            )
    else:
        print(
            ' Log Complexity Analysis\n'
            f' {f'Model: ':<40}{f'{model_names[0]}':<20} {f'{model_names[1]}':<20}'
        )
        for kpi, values in log_complexity_kpis.items():
            print(
                f' {f'{kpi}: ':<40}{f'{values[model_names[0]]}':<20} {f'{values[model_names[1]]}':<20}'
            )
    print(
        '----------------------------------------------------------------------------------------------------'
    )

    # provide model complexity kpis

    if n_model == 'true':
        print(
            ' Model Complexity Analysis\n'
            f' {f'Model: ':<40}{f'{model_names[0]}':<20} {f'{model_names[1]}':<20} {f'{model_names[2]}':<20}'
        )
        for kpi, values in model_complexity_kpis.items():
            print(
                f' {f'{kpi}: ':<40}{f'{values[model_names[0]]}':<20} {f'{values[model_names[1]]}':<20} '
                f'{f'{values[model_names[2]]}':<20}'
            )
    else:
        print(
            ' Model Complexity Analysis\n'
            f' {f'Model: ':<40}{f'{model_names[0]}':<20} {f'{model_names[1]}':<20}'
        )
        for kpi, values in model_complexity_kpis.items():
            print(
                f' {f'{kpi}: ':<40}{f'{values[model_names[0]]}':<20} {f'{values[model_names[1]]}':<20}'
            )
    print(
        '----------------------------------------------------------------------------------------------------\n'
        f' {f'Similarity Scores: ':<45}'
    )
    for name, score in similarity_scores.items():
        print(f' {name:<40}: {round(score, 4)}')
    print('\n')


def print_matrixwise_similarity_analysis_output(
        model_names: list[str],
        similarity_scores: dict[str, float],
        cnc_values: dict[str, float]
) -> None:
    """
    Prints similarity matrix of a list of models and their coefficients of network complexity.

    :param model_names: Names of models to print
    :param similarity_scores: Similarity scores of models to print
    :param cnc_values: Coefficients of network complexity of models to print
    :return: None
    """

    header: list[str] = ['Model\ncnc']
    for n in range(len(model_names)):
        col_model = model_names[n]
        cnc_value = cnc_values[col_model]
        header.append(f'{col_model}\n{cnc_value}')

    similarity_map = {}
    for pair, score in similarity_scores.items():
        model_1, model_2 = pair.split(' - ')
        similarity_map[(model_1, model_2)] = score
        similarity_map[(model_2, model_1)] = score

    table = []
    for n in range(len(model_names)):
        row_model = model_names[n]
        cnc_value = cnc_values[row_model]
        row: list[str] = [f'{row_model}\n{cnc_value}']
        for col_model in model_names:
            similarity_score = round(similarity_map.get((row_model, col_model), 1), 4)
            row.append(str(similarity_score))
        table.append(row)

    print(' Model Complexity Analysis')
    print(tabulate(table, headers=header, tablefmt='simple') + '\n')
