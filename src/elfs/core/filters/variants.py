from pandas import DataFrame

from enum import StrEnum

from typing import Union


class SelectionVariants(StrEnum):
    """
    Selection variants for variants filter
    """

    INClUDE = 'include'
    EXCLUDE = 'exclude'


class IntervalTypes(StrEnum):
    """
    Interval types for variants filter
    """

    ABSOLUTE = 'absolute'
    RELATIVE = 'relative'


def filter_log_by_variants(
        log: DataFrame,
        frequency_intervals: set[tuple[Union[int, float], Union[int, float]]],
        activity_attribute_key: str,
        case_attribute_key: str,
        interval_type: IntervalTypes,
        selection_variant: SelectionVariants
) -> DataFrame:
    """
    Filters case variants for their frequency.

    A case is included (or excluded) in the results if the case variants frequency lies in the given frequency
    interval(s). The frequency intervals can be given in absolute or relative values.

    :param log: Event log to filter
    :param frequency_intervals: Frequency interval(s) to filter for
    :param activity_attribute_key: Attribute key for activity from event log
    :param case_attribute_key: Attribute key for case from event log
    :param interval_type: Type of interval
    :param selection_variant: Variant for result selection
    :return: Event log
    """

    # identify variants
    cases = log[case_attribute_key].drop_duplicates()
    variant_map = {}
    for case in cases:
        activities = log[log[case_attribute_key] == case][activity_attribute_key]
        variant_map.setdefault(tuple(activities), []).append(case)

    # sort variants by frequency
    sorted(variant_map.items(), key=lambda item: len(item[1]))

    # identify variant cases within interval
    cases_filtered = []

    for interval in frequency_intervals:

        # define lower and upper bounds
        lower_bound = interval[0]
        upper_bound = interval[1]

        if interval_type == IntervalTypes.ABSOLUTE:

            # validate bounds for absolute values
            # TODO: check whether necessary or not
            if len(variant_map) >= lower_bound:
                if len(variant_map) < upper_bound:
                    upper_bound = len(variant_map)
        else:

            # calculate bounds for relative values
            lower_bound = int(lower_bound * len(variant_map))
            upper_bound = int(upper_bound * len(variant_map))

        for i in range(lower_bound - 1, upper_bound - 1):
            variant_cases = list(variant_map.values())[i]
            for case in variant_cases:
                cases_filtered.append(case)

    # filter log by variants
    if selection_variant == SelectionVariants.INClUDE:
        log_filtered = log[log[case_attribute_key].isin(cases_filtered)]
    else:
        log_filtered = log[~log[case_attribute_key].isin(cases_filtered)]

    return log_filtered
