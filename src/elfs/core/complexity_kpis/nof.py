from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_nof(ext_petri_net: ExtendedPetriNet) -> int:
    """
    Calculate total number of control flow connections / edges of a petri net

    :param ext_petri_net: Petri net
    :return: number of control flow connections / edges
    """

    return ext_petri_net.get_number_of_edges()
