from elfs.core.objects.BusinessProcessGraph import BusinessProcessGraph


def compare_look_back_links(
        bpg: BusinessProcessGraph,
        look_back_links: dict[str, set[frozenset[str]]]
) -> bool:
    """
    Tests whether bpg has correct look ahead links.

    :param bpg: Business process graph to compare
    :param look_back_links: Correct look back links
    :return: True if bpg has correct look back links
    """

    # pre-process bpg look ahead links
    bpg_look_back_links: dict[str, set[frozenset[str]]] = {}
    for node, node_set in bpg.causal_footprint.look_back_links.items():
        for nodes in node_set:
            if node.id not in bpg_look_back_links.keys():
                bpg_look_back_links[node.id] = {frozenset({node.id for node in nodes})}
            else:
                bpg_look_back_links[node.id].add(frozenset({node.id for node in nodes}))

    if look_back_links == bpg_look_back_links:
        return True
    else:
        return False


def compare_look_ahead_links(
        bpg: BusinessProcessGraph,
        look_ahead_links: dict[str, set[frozenset[str]]]
) -> bool:
    """
    Tests whether bpg has correct look ahead links.

    :param bpg: Business process graph to compare
    :param look_ahead_links: Correct look ahead links
    :return: True if bpg has correct look ahead links
    """

    # pre-process bpg look ahead links
    bpg_look_ahead_links: dict[str, set[frozenset[str]]] = {}
    for node, node_set in bpg.causal_footprint.look_ahead_links.items():
        for nodes in node_set:
            if node.id not in bpg_look_ahead_links.keys():
                bpg_look_ahead_links[node.id] = {frozenset({node.id for node in nodes})}
            else:
                bpg_look_ahead_links[node.id].add(frozenset({node.id for node in nodes}))

    if look_ahead_links == bpg_look_ahead_links:
        return True
    else:
        return False
