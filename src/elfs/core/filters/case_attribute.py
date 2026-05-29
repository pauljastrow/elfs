from typing import Union

from pandas import DataFrame, Series, concat

from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for case attribute filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


def filter_log_by_case_attribute(
        log: DataFrame,
        attribute_key: str,
        attribute_values: Union[str, int, bool, list[str], list[int], set[tuple[int, int]]],
        case_attribute_key: str,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters cases for a specific attribute value.

    A case is included (or excluded) in the results if the case attribute has the given value or at least one of the
    case's activities has this value as one of its activity attribute values.

    :param log: Event log to filter
    :param attribute_key: Attribute key to filter by from event log
    :param attribute_values: Attribute value(s) to filter for
    :param case_attribute_key: Attribute key for cases from event log
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # filter for single values or lists of values
    if isinstance(attribute_values, Union[str, int, list]):

        # transform single value to list to make isin() functional
        if isinstance(attribute_values, Union[str, int]):
            attribute_values = [attribute_values]

        # search for cases with attribute value
        if isinstance(attribute_values[0], bool):
            cases = log[log[attribute_key].eq(attribute_values[0])][case_attribute_key]
        else:
            cases = log[log[attribute_key].isin(attribute_values)][case_attribute_key]

    # filter for numeric intervals
    else:
        cases = Series()

        # search for cases with attribute values for every interval
        for interval in attribute_values:

            lower_bound = interval[0]
            upper_bound = interval[1]

            # search for cases with attribute value in interval
            temp_cases = log[log[attribute_key].between(lower_bound, upper_bound)][case_attribute_key]
            cases = concat([cases, temp_cases])

    # filter initial log by identified cases and include or exclude them from the final results
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(cases)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases)]

    return log_filtered
