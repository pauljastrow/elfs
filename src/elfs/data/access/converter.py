from typing import Union

from pandas import DataFrame
from pm4py.objects.conversion.log.converter import apply as convert, Variants
from pm4py.objects.log.obj import EventLog


def convert_log(
        log: Union[DataFrame, EventLog]
) -> Union[EventLog, DataFrame]:
    """
    Returns converted event log.

    Converts an event log of type DataFrame (or pm4py EventLog) to a pm4py EventLog (or DataFrame).

    :param log: Event log to convert
    :return: Converted event log
    """

    # Check data type of provided event log and convert it respectively
    if isinstance(log, EventLog):
        return convert(log, variant=Variants.TO_DATA_FRAME)
    else:
        return convert(log, variant=Variants.TO_EVENT_LOG)
