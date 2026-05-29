from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_noa(ext_petri_net: ExtendedPetriNet) -> int:
    """
    Calculate total number of activities of a petri net

    :param ext_petri_net: Petri net
    :return: Number of activities
    """

    return ext_petri_net.get_number_of_activities()
