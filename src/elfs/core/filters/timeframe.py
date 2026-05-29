import datetime

from enum import StrEnum

from pandas import DataFrame, Series, concat


class SelectionVariants(StrEnum):
    """
    Selection variants for timeframe filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


class IntervalVariants(StrEnum):
    """
    Interval variants for timeframe filter
    """

    START_DATE = 'start_date'
    END_DATE = 'end_date'
    BOTH = 'both'


def filter_log_by_timeframe(
        log: DataFrame,
        timeframe_intervals: set[tuple[datetime, datetime]],
        case_attribute_key: str,
        start_date_attribute_key: str,
        end_date_attribute_key: str,
        interval_variant: IntervalVariants,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters cases for their timeframe.

    A case is included (or excluded) in the results if the case starts, ends, or starts and ends within given timeframe
    interval(s). The interval variant is used to determine whether the timeframe refers to the start date, end date, or
    both dates.

    :param log: Event log to filter
    :param timeframe_intervals: Time intervals to filter for
    :param case_attribute_key: Attribute key for case from event log
    :param start_date_attribute_key: Attribute key for case start date from event log
    :param end_date_attribute_key: Attribute key for case end date from event log
    :param interval_variant: Variant for determination of timeframe reference
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # data pre-processing
    log[start_date_attribute_key] = log[start_date_attribute_key].dt.tz_convert(None)
    log[end_date_attribute_key] = log[end_date_attribute_key].dt.tz_convert(None)

    # filter log for timeframe
    cases = Series()

    for interval in timeframe_intervals:

        begin_timeframe = interval[0]
        end_timeframe = interval[1]

        # search for cases whose timeframe lies in intervals
        if interval_variant == IntervalVariants.START_DATE:
            temp_cases = log[
                (log[start_date_attribute_key] >= begin_timeframe) & (log[start_date_attribute_key] <= end_timeframe)
                ][case_attribute_key]
        elif interval_variant == IntervalVariants.END_DATE:
            temp_cases = log[
                (log[end_date_attribute_key] >= begin_timeframe) &(log[end_date_attribute_key] <= end_timeframe)
                ][case_attribute_key]
        else:
            temp_cases = log[
                (log[start_date_attribute_key] >= begin_timeframe) & (log[start_date_attribute_key] <= end_timeframe) &
                (log[end_date_attribute_key] >= begin_timeframe) & (log[end_date_attribute_key] <= end_timeframe)
                ][case_attribute_key]

        cases = concat([cases, temp_cases])

    # filter initial log by identified cases and include or exclude them from the final results
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(cases)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases)]

    return log_filtered
