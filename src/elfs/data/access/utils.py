from pathlib import Path

from enum import StrEnum

from pandas import DataFrame

from xml.etree import ElementTree as ET

from pm4py.utils import format_dataframe


class LogAttributes(StrEnum):
    """
    Standard naming convention for event log attributes used in elfs
    """

    CASE_ATTRIBUTE_KEY = 'case:concept:name'
    CASE_START_DATE_ATTRIBUTE_KEY = 'case:startDate'
    CASE_END_DATE_ATTRIBUTE_KEY = 'case:endDate'
    CASE_COMPLETION_ATTRIBUTE_KEY = 'case:requestComplete'
    ACTIVITY_ATTRIBUTE_KEY = 'concept:name'
    TIMESTAMP_ATTRIBUTE_KEY = 'time:timestamp'
    START_TIMESTAMP_ATTRIBUTE_KEY = 'start_timestamp'


class LogFormats(StrEnum):
    """
    Supported import file formats for event log files
    """
    XES = '.xes'
    CSV = '.csv'


def validate_file_log(
        file_path: Path
) -> Path:
    """
    Returns validated event log file path.

    Checks whether file path exists, leads to a file, and leads to a .xes or .csv file.

    :param file_path: File path to event log
    :return: Validated file path as Path
    """

    # check if file path exists
    if not file_path.exists():
        raise FileNotFoundError(f'File path not found: {file_path}')

    # check if file path leads to a file
    if not file_path.is_file():
        raise IsADirectoryError(f'File path leads to no file: {file_path}')

    # check if file is of type .xes
    if not file_path.suffix.lower() in set(LogFormats):
        raise ValueError(f'Invalid file type: {file_path.suffix} found by file path: {file_path}')

    return file_path


def format_log(
        log: DataFrame,
        case_attribute: str,
        case_start_date_attribute: str,
        case_end_date_attribute: str,
        case_completion_attribute: str,
        activity_attribute: str,
        time_stamp_attribute: str,
        start_timestamp_attribute: str
) -> DataFrame:
    """
    Returns formatted event log.

    Sets empty attribute keys provided by the user to standard attribute keys. The main attributes are formatted via
    pm4py. Additional attributes, necessary for filtering, are formatted separately. In case, additional attributes are
    not present in event log, they are calculated. In case, the case completion attribute is not present all cases are
    considered completed.

    :param log: Event log to format
    :param case_attribute: Attribute key for cases from event log
    :param case_start_date_attribute: Attribute key for case start date from event log
    :param case_end_date_attribute: Attribute key for case end date from event log
    :param case_completion_attribute: Attribute key for case completion from event log
    :param activity_attribute: Attribute key for activities from event log
    :param time_stamp_attribute: Attribute key for timestamp from event log
    :param start_timestamp_attribute: Attribute key for activity start timestamp from event log
    :return: Formatted event log as pm4py EventLog
    """

    empty_options = ['', ' ', '.']

    # format main attributes (use standard attribute keys for empty inputs)
    if case_attribute in empty_options:
        case_attribute = LogAttributes.CASE_ATTRIBUTE_KEY
    if activity_attribute in empty_options:
        activity_attribute = LogAttributes.ACTIVITY_ATTRIBUTE_KEY
    if time_stamp_attribute in empty_options:
        time_stamp_attribute = LogAttributes.TIMESTAMP_ATTRIBUTE_KEY
    if start_timestamp_attribute in empty_options:
        start_timestamp_attribute = LogAttributes.START_TIMESTAMP_ATTRIBUTE_KEY

    # use formating function from pm4py for formating of main attributes
    log = format_dataframe(
        df=log,
        case_id=case_attribute,
        activity_key=activity_attribute,
        timestamp_key=time_stamp_attribute,
        start_timestamp_key=start_timestamp_attribute,
    )

    # format additional attributes (use standard attribute keys for empty inputs)
    if case_start_date_attribute in empty_options:
        case_start_date_attribute = LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY
        if case_start_date_attribute not in log.columns:
            # identify start date for every trace
            log[case_start_date_attribute] = (log.groupby(LogAttributes.CASE_ATTRIBUTE_KEY)[time_stamp_attribute].
                                              transform('min'))

    if case_end_date_attribute in empty_options:
        case_end_date_attribute = LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY
        if case_end_date_attribute not in log.columns:
            # identify end date for every trace
            log[case_end_date_attribute] = (log.groupby(LogAttributes.CASE_ATTRIBUTE_KEY)[time_stamp_attribute].
                                            transform('max'))

    if case_completion_attribute in empty_options:
        case_completion_attribute = LogAttributes.CASE_COMPLETION_ATTRIBUTE_KEY
        if case_completion_attribute not in log.columns:
            # consider all traces as completed
            log[case_completion_attribute] = 'true'

    if case_start_date_attribute in log.columns:
        log = log.rename(columns={case_start_date_attribute: LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY.value})
        # TODO: check if reformating to date format is needed
    else:
        raise ValueError(f'Case start date attribute {case_start_date_attribute} not found in log')
    if case_end_date_attribute in log.columns:
        log = log.rename(columns={case_end_date_attribute: LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY.value})
        # TODO: check if reformating to date format is needed
    else:
        raise ValueError(f'Case end date attribute {case_end_date_attribute} not found in log')
    if case_completion_attribute in log.columns:
        log = log.rename(columns={case_completion_attribute: LogAttributes.CASE_COMPLETION_ATTRIBUTE_KEY.value})
        # TODO: check if mapping to true and false needed
    else:
        raise ValueError(f'Case completion attribute {case_completion_attribute} not found in log')

    return log


def ensure_storage_dir(path: Path) -> None:
    """
    Ensures the storage directory exists.

    :return: None
    """

    path.mkdir(exist_ok=True)


def change_pnml_file_attribute_value(
        file_path: Path,
        attribute: str,
        value: str
) -> None:
    """
    Changes value of a specific .pnml file attribute.

    :param file_path: File path of .pnml file
    :param attribute: Attribute name
    :param value: New attribute value
    :return: None
    """

    # identify attribute in .pnml file and change it to new value
    tree = ET.parse(file_path)
    tree.getroot().find('.//{*}net').find('./{*}' + attribute + '/{*}text').text = value

    # write changed .pnml file
    tree.write(file_path)


def set_pnml_file_net_attribute(
        file_path: Path,
        attribute: str,
        value: str
) -> None:
    """
    Sets net attribute in pnml. file.

    :param file_path: File path of .pnml file
    :param attribute: Attribute name
    :param value: Attribute value
    :return: None
    """

    # set net attribute in .pnml file
    tree = ET.parse(file_path)
    tree.getroot().find('.//{*}net').set(attribute, value)  # ET.SubElement()

    # write changed .pnml file
    tree.write(file_path)


def get_pnml_file_net_attribute(
        file_path: Path,
        attribute: str
) -> str:
    """
    Returns net attribute from pnml. file.

    :param file_path: File path of .pnml file
    :param attribute: Attribute name
    :return: Attribute value
    """

    # get net attribute from .pnml file
    tree = ET.parse(file_path)
    value = tree.getroot().find('.//{*}net').get(attribute)  # .find('./{*}' + attribute + '/{*}text').text

    return value
