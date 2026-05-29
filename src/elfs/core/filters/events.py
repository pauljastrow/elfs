from pandas import DataFrame

from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for event filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


def filter_log_by_events(
        log: DataFrame,
        activities: list[str],
        activity_attribute_key: str,
        case_attribute_key: str,
        selection_variant: str
) -> DataFrame:
    """
    Filters cases for activities.

    A case is included (or excluded) in the results if in a case specific activities are present.

    :param log: Event log to filter
    :param activities: Activities to filter for
    :param activity_attribute_key: Attribute key for activity from event log
    :param case_attribute_key: Attribute key for case from event log
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # search for activities
    search_df = log[log[activity_attribute_key].isin(activities)][case_attribute_key]

    # filter log by activities
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(search_df)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(search_df)]

    return log_filtered
