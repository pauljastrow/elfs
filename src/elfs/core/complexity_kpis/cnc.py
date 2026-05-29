from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_cnc(ext_petri_net: ExtendedPetriNet, nof: int, noa: int, ) -> float:
    """
    Calculate the network complexity coefficient of a business process

    :param ext_petri_net: Petri net
    :param nof: Number of flow elements of petri net
    :param noa: Number of activities of petri net
    :return: network complexity coefficient
    """

    place_count = ext_petri_net.get_number_of_places()
    return nof / (noa + place_count)
