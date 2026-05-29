from collections import defaultdict

from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet
from elfs.core.complexity_kpis.noa import calculate_noa
from elfs.core.complexity_kpis.nof import calculate_nof
from elfs.core.complexity_kpis.nog import calculate_nog
from elfs.core.complexity_kpis.cnc import calculate_cnc
from elfs.core.complexity_kpis.case_count import calculate_case_count
from elfs.core.complexity_kpis.variant_count import calculate_variant_count
from elfs.core.complexity_kpis.avg_gateway_degree import calculate_avg_gateway_degree
from elfs.core.complexity_kpis.max_gateway_degree import calculate_max_gateway_degree


def analyze_model_complexity(
        ext_petri_nets: set[ExtendedPetriNet]
) -> defaultdict[str, dict[str, float]]:
    """
    Analyzes the complexity of a set (2 or 3) petri nets.

    Returns the number of activities, number of flow elements, number of gateways, coefficient of network complexity,
    average gateway degree, and maximal gateway degree of a petri net.

    :param ext_petri_nets: Petri nets to analyze
    :return: complexity kpis as dict
    """

    complexity_kpis: defaultdict[str, dict[str, float]] = defaultdict(dict)

    for ext_petri_net in ext_petri_nets:

        # calculate number of activities
        noa = calculate_noa(ext_petri_net=ext_petri_net)
        complexity_kpis['Number of Activities'][ext_petri_net.petri_net.name] = noa

        # calculate number of control flow connections
        nof = calculate_nof(ext_petri_net=ext_petri_net)
        complexity_kpis['Number of Control Flow Elements'][ext_petri_net.petri_net.name] = nof

        # calculate number of gateways
        nog = calculate_nog(ext_petri_net=ext_petri_net)
        complexity_kpis['Number of Gateways'][ext_petri_net.petri_net.name] = nog

        # calculate coefficient of network complexity
        cnc = round(calculate_cnc(ext_petri_net=ext_petri_net, nof=nof, noa=noa), 4)
        complexity_kpis['Coefficient of Network Complexity'][ext_petri_net.petri_net.name] = cnc

        # average gateway degree
        avg_gateway_degree = round(calculate_avg_gateway_degree(ext_petri_net=ext_petri_net), 2)
        complexity_kpis['Average Gateway Degree'][ext_petri_net.petri_net.name] = avg_gateway_degree

        # maximum gateway degree
        max_gateway_degree = calculate_max_gateway_degree(ext_petri_net=ext_petri_net)
        complexity_kpis['Maximal Gateway Degree'][ext_petri_net.petri_net.name] = max_gateway_degree

    return complexity_kpis


def analyze_log_complexity(
        ext_petri_nets: set[ExtendedPetriNet]
) -> defaultdict[str, dict[str, float]]:
    """
    Analyzes the complexity of the underlying event logs from which petri nets were discovered.

    Returns the number of cases and variants per underlying event log.

    :param ext_petri_nets: Petri nets to analyze
    :return: complexity kpis as dict
    """

    complexity_kpis: defaultdict[str, dict[str, float]] = defaultdict(dict)

    for ext_petri_net in ext_petri_nets:

        # get number of cases
        case_count = calculate_case_count(ext_petri_net=ext_petri_net)
        complexity_kpis['Number of Cases'][ext_petri_net.petri_net.name] = case_count

        # get number of variants
        variant_count = calculate_variant_count(ext_petri_net=ext_petri_net)
        complexity_kpis['Number of Variants'][ext_petri_net.petri_net.name] = variant_count

    return complexity_kpis


def analyze_model_complexity_via_cnc(
        ext_petri_nets: set[ExtendedPetriNet]
) -> dict[str, float]:
    """
    Retruns the coefficient of network complexity of a petri net.

    :param ext_petri_nets: Petri nets to analyze
    :return: Coefficients of network complexity as list
    """

    cnc_values: dict[str, float] = dict()

    for ext_petri_net in ext_petri_nets:

        # calculate number of activities
        noa = calculate_noa(ext_petri_net=ext_petri_net)

        # calculate number of control flow connections
        nof = calculate_nof(ext_petri_net=ext_petri_net)

        # calculate coefficient of network complexity
        cnc = round(calculate_cnc(ext_petri_net=ext_petri_net, nof=nof, noa=noa), 4)
        cnc_values[ext_petri_net.petri_net.name] = cnc

    return cnc_values
