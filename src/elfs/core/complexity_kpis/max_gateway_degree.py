from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_max_gateway_degree(ext_petri_net: ExtendedPetriNet) -> float:
    """
    Calculate the maximal gateway degree of a petri net

    :param ext_petri_net: Petri net
    :return: Maximal gateway degree
    """

    gateway_connections = ext_petri_net.get_number_of_gateway_connections()
    if len(gateway_connections) > 0:
        max_gateway_degree = max(gateway_connections)
    else:
        max_gateway_degree = 0

    return max_gateway_degree
