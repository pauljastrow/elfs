from pathlib import Path

from xml.etree import ElementTree as ET

from pm4py.objects.log.obj import EventLog

from elfs.data.access.utils import ensure_storage_dir, validate_file_log, format_log, get_pnml_file_net_attribute
from elfs.data.access.writer import write_event_log_to_xes_file
from elfs.data.access.importer import import_xes, import_csv
from elfs.data.access.reader import read_log_from_xes_file, read_petri_net_from_pnml_file
from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def import_log(
        file_path: str,
        log_name: str,
        case_attribute: str,
        case_start_date_attribute: str,
        case_end_date_attribute: str,
        case_completion_attribute: str,
        activity_attribute: str,
        time_stamp_attribute: str,
        start_timestamp_attribute: str
) -> None:
    """
    Imports, formats and stores an event log from an external .xes or .csv file

    :param file_path: Path to external event lof file
    :param log_name: Name used for storing the event log
    :param case_attribute: Name of case attribute from log
    :param case_start_date_attribute: Name of case start date attribute from log
    :param case_end_date_attribute: Name of case end date attribute from log
    :param case_completion_attribute: Name of case completion attribute from log
    :param activity_attribute: Name of activity attribute from log
    :param time_stamp_attribute: Name of time stamp attribute from log
    :param start_timestamp_attribute: Name of activity start timestamp attribute from log
    :return: None
    """

    # validate file path and file format
    file_path = validate_file_log(file_path=Path(file_path))

    # read xes file and convert to csv
    if file_path.suffix == '.xes':
        log = import_xes(file_path=file_path)
    else:
        log = import_csv(file_path=file_path)

    # format log
    log = format_log(
        log=log,
        case_attribute=case_attribute,
        case_start_date_attribute=case_start_date_attribute,
        case_end_date_attribute=case_end_date_attribute,
        case_completion_attribute=case_completion_attribute,
        activity_attribute=activity_attribute,
        time_stamp_attribute=time_stamp_attribute,
        start_timestamp_attribute=start_timestamp_attribute
    )

    # check presence of storage directory
    dir_path = Path('logs')
    ensure_storage_dir(path=dir_path)

    # write xes file
    write_event_log_to_xes_file(log, log_name)


def read_log(
        log_name: str
) -> EventLog:
    """
    Returns event log from stored .xes file.

    :param log_name: Name of stored event log
    :return: Event log as pm4py EventLog
    """

    # read event log from .xes file
    file_path = f'logs/{log_name}.xes'
    log = read_log_from_xes_file(file_path)

    return log


def read_model(
        model_name: str
) -> ExtendedPetriNet:
    """
    Returns petri net from stored .pnml file.

    Since pm4py does not initialize the name of the petri net correctly, the correct name is read from the stores .pnml
    file and set as name of the read petri net.

    :param model_name: Name of stored petri net
    :return: Petri net as pm4py PetriNet
    """

    # ensure presence of storage directory
    dir_path = Path(f'models/{model_name.removesuffix('_n')}')
    ensure_storage_dir(dir_path)

    file_path = f'{dir_path}/{model_name}.pnml'

    # read petri net
    petri_net, initial_marking, final_marking = read_petri_net_from_pnml_file(file_path=f'{dir_path}/{model_name}.pnml')

    # set name of petri net correctly
    net = ET.parse(file_path).getroot().find('.//{*}net')
    petri_net.name = net.find('./{*}name/{*}text').text

    # read additional information from petri net
    cases = get_pnml_file_net_attribute(file_path=Path(f'{dir_path}/{model_name}.pnml'), attribute='cases')
    variants = get_pnml_file_net_attribute(file_path=Path(f'{dir_path}/{model_name}.pnml'), attribute='variants')

    # create extended petri net
    ext_petri_net = ExtendedPetriNet(
        petri_net=petri_net,
        initial_marking=initial_marking,
        final_marking=final_marking,
        case_count=int(cases),
        variant_count=int(variants)
    )

    return ext_petri_net


def get_all_stored_logs() -> list[str]:
    """
    Returns names of all stored event logs.

    The file suffixes are removed from the names.

    :return: Names of stored event logs as list
    """

    # ensure presence of storage directory
    dir_path = Path('logs')
    ensure_storage_dir(dir_path)

    # get names of all stored event logs
    log_names = [log.name.removesuffix('.xes') for log in dir_path.iterdir() if log.is_file()]

    return log_names


def get_all_stored_models() -> list[str]:
    """
    Returns names of all stored petri net models.

    Only the name of the underlying models is returned. There is no distinction made between models and their negatives.

    :return: Names of stored models as list
    """

    # ensure presence of storage directory
    dir_path = Path('models')
    ensure_storage_dir(dir_path)

    # get names of all stored petri nets
    model_names = [log.name for log in dir_path.iterdir() if log.is_dir()]

    return model_names


