from typing import Union, Any

from pandas import DataFrame

from numpy import timedelta64

from datetime import datetime

from elfs.core.filters.case_duration import DurationUnits
from elfs.core.filters.variants import IntervalTypes


def validate_log_columns(
        log: DataFrame,
        required_columns: list[str]
) -> DataFrame:
    """
    Returns log if required attributes (i.e. columns) are present in log.

    :param log: Event log
    :param required_columns: Attributes (i.e. columns) to validate
    :return: Event log
    """

    # check presence of given attributes
    for column in required_columns:
        if column not in log.columns:
            raise ValueError(f'Column {column} not found; must be in {log.columns}')
    return log


# TODO: check whether necessary
def clean_log_columns(
        log: DataFrame,
        required_columns: list[str]
) -> DataFrame:
    """
    Returns log after cleaning values of given attribute(s) (i.e. columns).

    :param log: Event log
    :param required_columns: Attributes (i.e. columns) to clean
    :return: Cleaned event log
    """

    # drop non-existing values
    log.dropna(subset=required_columns, inplace=True)
    return log


def validate_variants(
        variant_input: str,
        variants: Any
) -> Any:
    """
    Returns validated variant.

    Checks whether provided user input matches variant options.

    :param variant_input: User input
    :param variants: Variant class
    :return: Variant
    """

    if variant_input not in variants:
        raise ValueError(f'Variant must be in: {set(variants)}')
    else:
        variant_input = variants(variant_input)

    return variant_input


def validate_duration_intervals(
        case_duration_intervals: set[tuple[int, int]],
        case_duration_unit: str
) -> set[tuple[timedelta64, timedelta64]]:
    """
    Returns validated duration interval(s).

    Verifies that bounds are non-negative, lower bounds are less or equal than upper bounds, and converts duration
    interval(s) from int to time delta.

    :param case_duration_intervals: Duration interval(s)
    :param case_duration_unit: Duration unit
    :return: Validated duration interval(s)
    """

    case_duration_intervals_validated: set[tuple[timedelta64, timedelta64]] = set()

    # validate every interval
    for interval in case_duration_intervals:

        lower_bound = interval[0]
        upper_bound = interval[1]

        # verify that no bound is negative
        if lower_bound < 0 or upper_bound < 0:
            raise ValueError(f'case duration interval must be positive but is [{lower_bound}, {upper_bound}]')

        # convert duration from int to timedelta
        lower_bound = timedelta64(lower_bound, case_duration_unit)
        upper_bound = timedelta64(upper_bound, case_duration_unit)

        # verify that lower bound is not bigger than upper bound
        correct_interval(lower_bound, upper_bound)

        case_duration_intervals_validated.add((lower_bound, upper_bound))

    return case_duration_intervals_validated


def validate_timeframe_intervals(
        timeframe_intervals: set[tuple[str, str]]
) -> set[tuple[datetime, datetime]]:
    """
    Returns validated duration interval(s).

    Verifies that lower bounds are less or equal than upper bounds, and converts time frame interval(s) from str to
    datetime.

    :param timeframe_intervals: Time frame interval(s)
    :return: Validated time frame interval(s)
    """

    timeframe_intervals_validated: set[tuple[datetime, datetime]] = set()

    # validate every interval
    for interval in timeframe_intervals:

        lower_bound = interval[0]
        upper_bound = interval[1]

        # convert duration from str to datetime
        lower_bound = transform_to_datetime(lower_bound)
        upper_bound = transform_to_datetime(upper_bound)

        # verify that lower bound is not bigger than upper bound
        correct_interval(lower_bound, upper_bound)

        timeframe_intervals_validated.add((lower_bound, upper_bound))

    return timeframe_intervals_validated


def validate_frequency_intervals(
        frequency_intervals: set[tuple[Union[int, float], Union[int, float]]],
        interval_type: IntervalTypes
) -> set[tuple[Union[int, float], Union[int, float]]]:
    """
    Returns validated frequency interval(s).

    Verifies that in an absolute frequency interval the bounds are of type int and the bounds in a relative frequency
    interval are of type float. Moreover, it checks whether the lower bounds are less or equal than upper bounds.

    :param frequency_intervals: Frequency interval(s)
    :param interval_type: Type of interval (absolute, relative)
    :return: Validated time frame interval(s)
    """

    frequency_intervals_validated: set[tuple[Union[int, float], Union[int, float]]] = set()

    # validate every interval
    for interval in frequency_intervals:

        lower_bound = interval[0]
        upper_bound = interval[1]

        # verify that the bounds of an absolute frequency interval are positive and of type int
        if interval_type == IntervalTypes.ABSOLUTE:

            if type(lower_bound) is not type(upper_bound):
                raise ValueError('lower_bound and upper_bound must be of same type')

            if isinstance(lower_bound, float) or isinstance(upper_bound, float):
                try:
                    lower_bound = int(lower_bound)
                    upper_bound = int(upper_bound)
                except ValueError:
                    raise ValueError('For variant "absolute", lower_bound and upper_bound must be of type int')

            if lower_bound < 0 or upper_bound < 0:
                raise ValueError('Lower_bound and upper_bound must be positive')

        # verify that the bounds of an absolute frequency interval are positive and of type float
        elif interval_type == IntervalTypes.RELATIVE and (
                lower_bound > 1 or upper_bound > 1 or lower_bound < 0 or upper_bound < 0
        ):
            raise ValueError('For variant "relative", lower_bound and upper_bound must be in the interval [0;1]')

        # verify that lower bound is not bigger than upper bound
        correct_interval(lower_bound, upper_bound)

        frequency_intervals_validated.add((lower_bound, upper_bound))

    return frequency_intervals_validated


def correct_interval(
        lower_bound: Union[int, float, timedelta64, datetime],
        upper_bound: Union[int, float, timedelta64, datetime]
) -> [Union[int, float, timedelta64, datetime], Union[int, float, timedelta64, datetime]]:
    """
    Returns validated bounds of an interval.

    Verifies that the lower bound of an interval is less or equal than the upper bound. If this is not the case, the
    lower bound and upper bound are switched.

    :param lower_bound: Lower bound of interval
    :param upper_bound: Upper bound of interval
    :return: Validated lower bound and validated upper bound
    """

    # verify whether lower bound is less or equal upper bound
    if lower_bound > upper_bound:
        temp = upper_bound
        upper_bound = lower_bound
        lower_bound = temp

    return lower_bound, upper_bound


def validate_duration_unit(
        unit: str
) -> str:
    """
    Returns validated duration unit.

    :param unit: Duration unit provided by user
    :return: Validated duration unit
    """

    # verify whether input resembles one of the supported duration units
    if unit not in DurationUnits:
        raise ValueError(f'Invalid duration unit: {unit}')

    return unit


def transform_to_datetime(
        input_datetime: str
) -> datetime:
    """
    Returns a user provided date in str form converted to datetime.

    :param input_datetime: Date provided by the user to convert
    :return: Converted date
    """

    # Define supported date formats
    formats = ['%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M', '%d.%m.%Y']

    # Check which date format provided date has and transform it to datetime
    for fmt in formats:
        try:
            return datetime.strptime(input_datetime, fmt)
        except ValueError:
            pass

    raise ValueError(f'Invalid datetime format: {input_datetime}')
