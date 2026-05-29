from pm4py.objects.log.obj import EventLog

from elfs.core.discovery.petri_net import discover_petri_net
from elfs.core.discovery.utils import determine_log_case_count, determine_log_variant_count
from elfs.data.access.converter import convert_log
from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def discover_model(
        log: EventLog
) -> ExtendedPetriNet:
    """
    Discovers petri net from event log.

    Discovered pm4py PetriNet is transformed to an petri net extended with additional information.

    :param log: Event log to discover petri net from
    :return: Extended petri net
    """

    log = convert_log(log=log)

    # determine number of cases and variants
    case_count = determine_log_case_count(log=log)
    variant_count = determine_log_variant_count(log=log)

    petri_net, initial_marking, final_marking = discover_petri_net(log=log)

    # create extended petri net
    ext_petri_net = ExtendedPetriNet(
        petri_net=petri_net,
        initial_marking=initial_marking,
        final_marking=final_marking,
        case_count=case_count,
        variant_count=variant_count
    )

    return ext_petri_net
