from pandas import DataFrame, concat, to_datetime

from enum import StrEnum


class SelectionVariants(StrEnum):
    """
    Selection variants for start and end event filter
    """

    INCLUDE = 'include'
    EXCLUDE = 'exclude'


class SetVariants(StrEnum):
    """
    Set variants for start and end event filter
    """

    UNION = 'union'
    INTERSECTION = 'intersection'


def filter_log_by_start_and_end_events(
        log: DataFrame,
        start_activities: list[str],
        end_activities: list[str],
        activity_attribute_key: str,
        case_attribute_key: str,
        activity_timestamp_attribute_key: str,
        set_variant: SetVariants,
        selection_variant: SelectionVariants,
) -> DataFrame:
    """
    Filters cases for their duration.

    A case is included (or excluded) in the results if the case duration lies in the given value interval(s).

    :param log: Event log to filter
    :param start_activities: Start activities to filter for
    :param end_activities: End activities to filter for
    :param activity_attribute_key: Attribute key for activity from event log
    :param case_attribute_key: Attribute key for case from event log
    :param activity_timestamp_attribute_key: Attribute key for activity start timestamp from event log
    :param set_variant: Variant for result inclusion
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # data pre-processing
    log[activity_timestamp_attribute_key] = to_datetime(log[activity_timestamp_attribute_key])
    start_search_df = DataFrame()
    end_search_df = DataFrame()

    # identify and filter start activities
    if start_activities:
        start_search_df = log.loc[log.groupby(case_attribute_key)[activity_timestamp_attribute_key].idxmin()]
        start_search_df = start_search_df[start_search_df[activity_attribute_key].isin(start_activities)][
            case_attribute_key]

    # identify and filter end activities
    if end_activities:
        end_search_df = log.loc[log.groupby(case_attribute_key)[activity_timestamp_attribute_key].idxmax()]
        end_search_df = end_search_df[end_search_df[activity_attribute_key].isin(end_activities)][case_attribute_key]

    # process search results
    if not start_search_df.empty and not end_search_df.empty:
        if set_variant == SetVariants.INTERSECTION:
            search_results = start_search_df[start_search_df.isin(end_search_df)]
        else:
            search_results = concat([start_search_df, end_search_df]).drop_duplicates()
    elif not start_search_df.empty:
        search_results = start_search_df
    else:
        search_results = end_search_df

    # filter log by start and end activities
    if selection_variant == SelectionVariants.INCLUDE:
        log_filtered = log[log[case_attribute_key].isin(search_results)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(search_results)]

    return log_filtered
