from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def calculate_variant_count(ext_petri_net: ExtendedPetriNet):
    """
    Calculate variant count of a petri net

    :param ext_petri_net: Petri net
    :return: Variant count
    """

    return ext_petri_net.get_variant_count()
