from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_case_count(ext_petri_net: ExtendedPetriNet):
    """
    Calculate case count of a petri net

    :param ext_petri_net: Petri net
    :return: Case count
    """

    return ext_petri_net.get_case_count()
