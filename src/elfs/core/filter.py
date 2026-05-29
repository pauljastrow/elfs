from typing import Union

from pm4py.objects.log.obj import EventLog

from elfs.data.access.utils import LogAttributes
from elfs.core.filters.utils import (
    validate_log_columns,
    clean_log_columns,
    validate_variants,
    validate_duration_unit,
    validate_duration_intervals,
    validate_timeframe_intervals,
    validate_frequency_intervals
)
from elfs.data.access.converter import convert_log
from elfs.core.filters.case_duration import (
    SelectionVariants as CaseDurationSelectionVariants,
    filter_log_by_case_duration
)
from elfs.core.filters.timeframe import (
    IntervalVariants as TimeframeIntervalVariants,
    SelectionVariants as TimeframeSelectionVariants,
    filter_log_by_timeframe
)
from elfs.core.filters.events import (SelectionVariants as EventSelectionVariants, filter_log_by_events)
from elfs.core.filters.start_and_end_events import (
    SelectionVariants as StartEndEventSelectionVariants,
    SetVariants as StartEndEventSetVariants,
    filter_log_by_start_and_end_events
)
from elfs.core.filters.case_attribute import (
    SelectionVariants as CaseAttributeSelectionVariants,
    filter_log_by_case_attribute
)
from elfs.core.filters.variants import (
    IntervalTypes as VariantIntervalTypes,
    SelectionVariants as VariantSelectionVariants,
    filter_log_by_variants, IntervalTypes
)
from elfs.core.filters.event_repetitions import (
    SelectionVariants as EventRepetitionSelectionVariants,
    filter_log_by_event_repetitions
)
from elfs.core.filters.case_completion import (
    SelectionVariants as CaseCompletionSelectionVariants,
    filter_log_by_case_completion
)


def filter_case_duration(
        log: EventLog,
        case_duration_intervals: set[tuple[int, int]],
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        case_start_date_attribute_key: str = LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
        case_end_date_attribute_key: str = LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
        case_duration_unit: str = 'D',
        selection_variant: str = CaseDurationSelectionVariants.INCLUDE
) -> EventLog:
    """
    Filters cases by duration from start and end date

    :param log: EventLog
    :param case_duration_intervals: Case duration intervals in specified unit
    :param case_attribute_key: Case attribute key from log
    :param case_start_date_attribute_key: Start date attribute from log
    :param case_end_date_attribute_key: End date attribute from log
    :param case_duration_unit: Case duration unit
    :param selection_variant: Variants (
                    include: filters for cases whose duration lies in interval
                    exclude: filters for cases whose duration does not lay in interval
                    )
    :return: filtered EventLog
    """

    # input data pre-processing and validation
    case_duration_unit = validate_duration_unit(case_duration_unit)
    case_duration_intervals = validate_duration_intervals(case_duration_intervals, case_duration_unit)
    selection_variant = validate_variants(variant_input=selection_variant, variants=CaseDurationSelectionVariants)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(
        log=log_df,
        required_columns=[case_start_date_attribute_key, case_end_date_attribute_key]
    )
    log_df = clean_log_columns(
        log=log_df,
        required_columns=[case_start_date_attribute_key, case_end_date_attribute_key]
    )

    # filter log by case duration
    log_filtered_df = filter_log_by_case_duration(
        log=log_df,
        case_duration_intervals=case_duration_intervals,
        case_attribute_key=case_attribute_key,
        case_start_date_attribute_key=case_start_date_attribute_key,
        case_end_date_attribute_key=case_end_date_attribute_key,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


def filter_timeframe(
        log: EventLog,
        timeframe_intervals: set[tuple[str, str]],
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        start_date_attribute_key: str = LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
        end_date_attribute_key: str = LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
        interval_variant: str = TimeframeIntervalVariants.BOTH,
        selection_variant: str = TimeframeSelectionVariants
) -> EventLog:
    """
    Filters cases by timeframe. The Filter allows to filter only for start date, end date, or both.

    :param log: EventLog
    :param timeframe_intervals: Intervals of timeframe
    :param case_attribute_key: Case attribute key from log
    :param start_date_attribute_key: Start date attribute from log
    :param end_date_attribute_key: End date attribute from log
    :param interval_variant: Variants (
                    Variants.START_DATE: filters cases by start date
                    Variants.END_DATE: filters cases by end date
                    Variants.BOTH: filters cases by both the start and end date
                    )
    :param selection_variant: Variants (
                    include: filters for cases which include activities
                    exclude: filters for cases which do not include activities
                    )
    :return: filtered EventLog
    """

    # input data pre-processing and validation
    interval_variant = validate_variants(variant_input=interval_variant, variants=TimeframeIntervalVariants)
    selection_variant = validate_variants(variant_input=selection_variant, variants=TimeframeSelectionVariants)
    timeframe_intervals = validate_timeframe_intervals(timeframe_intervals=timeframe_intervals)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[start_date_attribute_key, end_date_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[start_date_attribute_key, end_date_attribute_key])

    # filter
    log_filtered_df = filter_log_by_timeframe(
        log=log_df,
        timeframe_intervals=timeframe_intervals,
        case_attribute_key=case_attribute_key,
        start_date_attribute_key=start_date_attribute_key,
        end_date_attribute_key=end_date_attribute_key,
        interval_variant=interval_variant,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


# TODO: check if presence of activities is checked
def filter_events(
        log: EventLog,
        activities: list[str],
        activity_attribute_key: str = LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        selection_variant: str = EventSelectionVariants.INCLUDE
) -> EventLog:
    """
    Filters cases by events

    :param log: EventLog
    :param activities: Name of event that the log should be filtered for
    :param activity_attribute_key: Activity attribute from log
    :param case_attribute_key: Case attribute from log
    :param selection_variant: Variants (
                    include: filters for cases which include activities
                    exclude: filters for cases which do not include activities
                    )
    :return: filtered EventLog
    """

    # input data pre-processing and validation
    selection_variant = validate_variants(variant_input=selection_variant, variants=EventSelectionVariants)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])

    # filter
    log_filtered_df = filter_log_by_events(
        log=log_df,
        activities=activities,
        activity_attribute_key=activity_attribute_key,
        case_attribute_key=case_attribute_key,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


def filter_start_and_end_events(
        log: EventLog,
        start_activities: list[str],
        end_activities: list[str],
        activity_attribute_key: str = LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        activity_timestamp_attribute_key: str = LogAttributes.TIMESTAMP_ATTRIBUTE_KEY,  # START_TIMESTAMP_ATTRIBUTE_KEY
        set_variant: str = StartEndEventSetVariants.INTERSECTION,
        selection_variant: str = StartEndEventSelectionVariants.INCLUDE
) -> EventLog:
    """
    Filters cases by start and end event
    :param log: EventLog
    :param start_activities: List of activities cases are allowed to start with
    :param end_activities: List of activities cases are allowed to end with
    :param activity_attribute_key: Activity attribute from log
    :param case_attribute_key: Case attribute from log
    :param activity_timestamp_attribute_key: Activity timestamp attribute from log
    :param set_variant: Variants (
                        intersection: cases must have both a start and end activity from the list to be considered
                        union: cases must have a start or end activity from the list to be considered
                        )
    :param selection_variant: Variants (
                                include: filters for cases which start or end with spedified activities
                                exclude: filters for cases which do not start or end with spedified activities
                                )
    :return: filtered EventLog
    """

    # input data pre-processing and validation
    if len(start_activities) == 0 and len(end_activities) == 0:
        raise ValueError('At least one activity expected')

    set_variant = validate_variants(variant_input=set_variant, variants=StartEndEventSetVariants)
    selection_variant = validate_variants(variant_input=selection_variant, variants=StartEndEventSelectionVariants)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])

    # filter
    log_filtered_df = filter_log_by_start_and_end_events(
        log=log_df,
        start_activities=start_activities,
        end_activities=end_activities,
        activity_attribute_key=activity_attribute_key,
        case_attribute_key=case_attribute_key,
        activity_timestamp_attribute_key=activity_timestamp_attribute_key,
        set_variant=set_variant,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


def filter_case_attribute(
        log: EventLog,
        attribute_key: str,
        attribute_values: Union[str, int, bool, list[str], list[int], set[tuple[int, int]]],
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        selection_variant: str = CaseAttributeSelectionVariants.INCLUDE
) -> EventLog:
    """
    filters cases by case attribute
    :param log: EventLog
    :param attribute_key: Attribute from log
    :param attribute_values: Values for attribute from log
    :param case_attribute_key: Case attribute from log
    :param selection_variant: Variants (
                    include: filters for cases which include attribute value
                    exclude: filters for cases which do not include attribute value
                    )
    :return: filtered EventLog
    """

    # data pre-processing and validation
    selection_variant = validate_variants(variant_input=selection_variant, variants=CaseAttributeSelectionVariants)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[attribute_key, case_attribute_key])
    # log_df = clean_log_columns(log=log_df, required_columns=[case_attribute_key])

    # filter
    log_filtered_df = filter_log_by_case_attribute(
        log=log_df,
        attribute_key=attribute_key,
        attribute_values=attribute_values,
        case_attribute_key=case_attribute_key,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


# check if relative values should apply to cases or variants: as in multi-range filter paper
def filter_variants(
        log: EventLog,
        frequency_intervals: set[tuple[Union[int, float], Union[int, float]]],
        activity_attribute_key: str = LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        interval_type: str = VariantIntervalTypes.ABSOLUTE,
        selection_variant: str = VariantSelectionVariants.INClUDE
) -> EventLog:
    """
    filters cases for their most frequent or infrequent variants
    :param log: EventLog
    :param frequency_intervals: Absolute (or relative) frequency intervals
    :param activity_attribute_key: Activity attribute from log
    :param case_attribute_key: Case attribute from log
    :param interval_type: Variants (
                    absolute: frequency interval is integer based
                    relative: frequency interval is probability based
                    )
    :param selection_variant: Variants (
                    include: filters for variants whose frequency lies in interval
                    exclude: filters for variants whose frequency lies not in interval
                    )
    :return: filtered EventLog
    """

    # data pre-processing and validation
    interval_type = validate_variants(variant_input=interval_type, variants=VariantIntervalTypes)
    selection_variant = validate_variants(variant_input=selection_variant, variants=VariantSelectionVariants)
    frequency_intervals = validate_frequency_intervals(
        frequency_intervals=frequency_intervals,
        interval_type=interval_type
    )

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])

    # filter
    log_filtered_df = filter_log_by_variants(
        log=log_df,
        frequency_intervals=frequency_intervals,
        activity_attribute_key=activity_attribute_key,
        case_attribute_key=case_attribute_key,
        interval_type=interval_type,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


def filter_event_repetitions(
        log: EventLog,
        repetition_intervals: set[tuple[int, int]],
        activity_attribute_key: str = LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        selection_variant: str = EventRepetitionSelectionVariants.INCLUDE
) -> EventLog:
    """
    filters cases by the existence of event repetitions
    :param log: EventLog
    :param repetition_intervals: Amount of event repetitions
    :param activity_attribute_key: Activity attribute from log
    :param case_attribute_key: Case attribute from log
    :param selection_variant: Variants (
                    include: filters for cases which include event repetitions
                    exclude: filters for cases which do not include event repetitions
                    )
    :return: filtered EventLog
    """

    # input data pre-processing and validation
    selection_variant = validate_variants(variant_input=selection_variant, variants=EventRepetitionSelectionVariants)
    repetition_intervals = validate_frequency_intervals(repetition_intervals, interval_type=IntervalTypes.ABSOLUTE)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[activity_attribute_key, case_attribute_key])

    # filter
    log_filtered_df = filter_log_by_event_repetitions(
        log=log_df,
        repetition_intervals=repetition_intervals,
        activity_attribute_key=activity_attribute_key,
        case_attribute_key=case_attribute_key,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered = convert_log(log=log_filtered_df)

    return log_filtered


def filter_case_completion(
        log: EventLog,
        case_attribute_key: str = LogAttributes.CASE_ATTRIBUTE_KEY,
        case_completion_attribute_key: str = LogAttributes.CASE_COMPLETION_ATTRIBUTE_KEY,
        selection_variant: str = CaseCompletionSelectionVariants.INCLUDE
) -> EventLog:
    """
    filters cases for their completion status
    :param log: EventLog
    :param case_attribute_key: Case attribute from log
    :param case_completion_attribute_key: Case completion attribute from log
    :param selection_variant: Variants (
                    include: filters for cases which are completed
                    exclude: filters for cases which are not completed
                    )
    :return:
    """

    # input data pre-processing and validation
    selection_variant = validate_variants(variant_input=selection_variant, variants=CaseCompletionSelectionVariants)

    # log pre-processing
    log_df = convert_log(log=log)
    log_df = validate_log_columns(log=log_df, required_columns=[case_attribute_key, case_completion_attribute_key])
    log_df = clean_log_columns(log=log_df, required_columns=[case_attribute_key, case_completion_attribute_key])

    # filter
    log_filtered_df = filter_log_by_case_completion(
        log=log_df,
        case_attribute_key=case_attribute_key,
        case_completion_attribute_key=case_completion_attribute_key,
        selection_variant=selection_variant
    )

    # log post-processing
    log_filtered_df = convert_log(log_filtered_df)

    return log_filtered_df
