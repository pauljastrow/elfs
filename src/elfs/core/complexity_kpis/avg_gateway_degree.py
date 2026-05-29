from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_avg_gateway_degree(ext_petri_net: ExtendedPetriNet) -> float:
    """
    Calculate the average gateway degree of a petri net

    :param ext_petri_net: Petri net
    :return: Average gateway degree
    """

    total_num_of_gateway_connections = sum(ext_petri_net.get_number_of_gateway_connections())
    gateway_count = ext_petri_net.get_number_of_gateways()

    if gateway_count != 0:
        avg_gateway_degree = total_num_of_gateway_connections / gateway_count
    else:
        avg_gateway_degree = 0

    return avg_gateway_degree
