from pm4py.discovery import discover_petri_net_heuristics as discover
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking

from elfs.data.access.utils import LogAttributes


def discover_petri_net(
        log: EventLog
) -> tuple[PetriNet, Marking, Marking]:
    """
    Discovers petri net from event log.

    :param log: Event log to discover petri net from
    :return: petri net as pm4py PetriNet, initial marking as pm4py Marking, and final marking as pm4py Marking
    """

    # discover petri net from event log
    petri_net, initial_marking, final_marking = discover(
        log=log,
        activity_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
        timestamp_key=LogAttributes.TIMESTAMP_ATTRIBUTE_KEY,
        case_id_key=LogAttributes.CASE_ATTRIBUTE_KEY
    )

    return petri_net, initial_marking, final_marking
