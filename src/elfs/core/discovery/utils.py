from pandas import DataFrame

from elfs.data.access.utils import LogAttributes


def determine_log_case_count(
        log: DataFrame
) -> int:
    """
    Returns the number of cases in a log.

    :param log: Event log
    :return: Case count
    """

    return len(log[LogAttributes.CASE_ATTRIBUTE_KEY].drop_duplicates())


def determine_log_variant_count(
        log: DataFrame
) -> int:
    """
    Returns the number of variants in a log.

    :param log: Event log
    :return: Variant count
    """

    # identify variants
    cases = log[LogAttributes.CASE_ATTRIBUTE_KEY].drop_duplicates()
    variant_map = {}
    for case in cases:
        activities = log[log[LogAttributes.CASE_ATTRIBUTE_KEY] == case][LogAttributes.ACTIVITY_ATTRIBUTE_KEY]
        variant_map.setdefault(tuple(activities), []).append(case)

    return len(variant_map)
