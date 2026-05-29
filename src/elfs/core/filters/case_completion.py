from pandas import DataFrame
from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for case completion filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


def filter_log_by_case_completion(
        log: DataFrame,
        case_attribute_key: str,
        case_completion_attribute_key: str,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters cases for their completion.

    A case is included (or excluded) in the results if its completion attribute is true.

    :param log: Event log to filter
    :param case_attribute_key: Attribute key for cases from event log
    :param case_completion_attribute_key: Attribute key for case completion from event log
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # data pre-processing
    # TODO: check if additional mapping options are necessary
    log[case_completion_attribute_key] = log[case_completion_attribute_key].map(
        {'TRUE': True, 'true': True, 'FALSE': False, 'false': False}
    )

    # search for completed cases
    cases_completed = log[log[case_completion_attribute_key]][case_attribute_key]

    # filter log by case completion and include or exclude them from the final results
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(cases_completed)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases_completed)]

    return log_filtered
