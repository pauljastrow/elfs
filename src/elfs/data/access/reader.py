from pm4py.objects.log.importer.xes.importer import Variants as ImporterVariants, apply
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.importer import importer as petri_net_importer


def read_log_from_xes_file(
        file_path: str
) -> EventLog:

    """
    Reads event log from stored or external .xes file.

    :param file_path: File path to .xes file
    :return: Event log as pm4py EventLog
    """

    # set parameters
    parameters = {
        "encoding": 'utf-8',
        "return_legacy_log_object": False,
        "return_pl_lazyframe": False
    }
    variant = ImporterVariants.CHUNK_REGEX

    # read .xes file via pm4py
    log = apply(path=file_path, parameters=parameters, variant=variant)

    return log


def read_petri_net_from_pnml_file(
        file_path: str
) -> tuple[PetriNet, Marking, Marking]:
    """
    Read petri net from stored .pnml file.

    :param file_path: File path to .pnml file
    :return: Petri net as pm4py PetriNet
    """

    # read petri net from .pnml file via pm4py
    petri_net, initial_marking, final_marking = petri_net_importer.apply(input_file_path=file_path)

    return petri_net, initial_marking, final_marking
