from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_nog(ext_petri_net: ExtendedPetriNet) -> int:
    """
    Calculate total number of gateways of a petri net

    :param ext_petri_net: Petri net
    :return: Number of gateways
    """

    return ext_petri_net.get_number_of_gateways()
