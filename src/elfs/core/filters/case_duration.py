from pandas import DataFrame, Series, concat

from numpy import timedelta64

from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for case duration filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


class DurationUnits(StrEnum):
    WEEK = 'W'
    DAY = 'D'
    HOUR = 'h'
    MINUTE = 'm'
    SECOND = 's'


# TODO: allow also single values and list of values
def filter_log_by_case_duration(
        log: DataFrame,
        case_duration_intervals: set[tuple[timedelta64, timedelta64]],
        case_attribute_key: str,
        case_start_date_attribute_key: str,
        case_end_date_attribute_key: str,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters cases for their duration.

    A case is included (or excluded) in the results if the case duration lies in the given value interval(s).

    :param log: Event log to filter
    :param case_duration_intervals: Duration interval(s) to filter for
    :param case_attribute_key: Attribute key for case from event log
    :param case_start_date_attribute_key: Attribute key for case start date from event log
    :param case_end_date_attribute_key: Attribute key for case end date from event log
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    case_duration_attribute_key = 'case:duration'

    # calculate case duration
    log[case_duration_attribute_key] = (log[case_end_date_attribute_key] - log[case_start_date_attribute_key])

    # filter log by case duration
    cases = Series()

    for interval in case_duration_intervals:

        lower_bound = interval[0]
        upper_bound = interval[1]

        # search for cases with attribute value in interval
        temp_cases = log[log[case_duration_attribute_key].between(lower_bound, upper_bound)][case_attribute_key]
        cases = concat([cases, temp_cases])

    # filter initial log by identified cases and include or exclude them from the final results
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(cases)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases)]

    return log_filtered
