from pathlib import Path

from pandas import (DataFrame, read_csv)

from pm4py.objects.conversion.log.converter import apply as convert_xes_to_Data_Frame, Variants as ConversionVariants

from elfs.data.access.reader import read_log_from_xes_file


def import_xes(
        file_path: Path
) -> DataFrame:
    """
    Imports event log from external .xes file.

    :param file_path: File path to external .xes file
    :return: Event log as pm4py DataFrame
    """

    # read .xes file
    log_xes = read_log_from_xes_file(file_path=str(file_path))

    # convert .xes file to pandas DataFrame via pm4py
    log_df = convert_xes_to_Data_Frame(log=log_xes, variant=ConversionVariants.TO_DATA_FRAME)

    return log_df


def import_csv(
        file_path: Path
) -> DataFrame:
    """
    Imports event log from external .csv file.

    :param file_path: File path to external .csv file
    :return: Event log as pm4py DataFrame
    """

    # read .csv file
    log_df = read_csv(file_path)

    return log_df
