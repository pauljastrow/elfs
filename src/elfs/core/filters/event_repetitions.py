from pandas import DataFrame

from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for event repetitions filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


# TODO: allow single values and list of values
def filter_log_by_event_repetitions(
        log: DataFrame,
        repetition_intervals: set[tuple[int, int]],
        activity_attribute_key: str,
        case_attribute_key: str,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters cases for their activities' repetitions.

    A case is included (or excluded) in the results if all activities' repetition count lies in the given interval(s).

    :param log: Event log to filter
    :param repetition_intervals: Repetition count interval(s) to filter for
    :param activity_attribute_key: Attribute key for activity from event log
    :param case_attribute_key: Attribute key for case from event log
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # identify cases
    cases = log[case_attribute_key].drop_duplicates()

    # identify cases whose event repetitions lie in the user-specified intervals
    cases_event_repetitions = []
    for case in cases:
        event_counts = log[log[case_attribute_key] == case][activity_attribute_key].value_counts()
        for interval in repetition_intervals:
            lower_bound = interval[0]
            upper_bound = interval[1]
            if event_counts.between(lower_bound, upper_bound).all():
                cases_event_repetitions.append(case)

    # filter log by cases with event repetitions
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(cases_event_repetitions)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases_event_repetitions)]

    return log_filtered
