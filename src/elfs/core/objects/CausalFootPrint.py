from collections import defaultdict

from elfs.core.objects.Node import Node


class CausalFootprint:
    """
    Causal footprint that is able to approximate the behavior of a business process graph.

    A causal footprint consists of causal links that can be directed backward (look-back links) or forward (look-ahead
    links).
    """

    def __init__(self):
        """
        Initializes a new CausalFootprint object.

        :return: None
        """

        self.look_back_links: dict[Node, set[frozenset[Node]]] = defaultdict()
        self.look_ahead_links: dict[Node, set[frozenset[Node]]] = defaultdict()

    def generate_minimal_causal_closure_of_causal_footprint(
            self,
            max_depth: int
    ) -> None:
        """
        Generates the minimal causal footprint under closure criteria with a maximal search depth as bound.

        :param max_depth: Maximum search depth for causal footprint.
        :return: None
        """

        new_look_back_link_found = True
        new_look_ahead_link_found = True

        # while new_look_back_link_found or new_look_ahead_link_found:
        for n in range(max_depth - 1):

            if new_look_back_link_found:

                new_look_back_link_found = False
                look_back_links_temp = self.look_back_links
                new_look_back_links: set[(Node, frozenset[Node])] = set()

                # substitution and chaining of look-back links
                for target_node in look_back_links_temp.keys():
                    for source_node_set in look_back_links_temp[target_node]:
                        for source_node in source_node_set:
                            for last_source_node_set in look_back_links_temp.get(source_node, ()):
                                inferred_source_node_set = set(
                                    (source_node_set - {source_node}) | last_source_node_set
                                )
                                if len(inferred_source_node_set) > 0 and inferred_source_node_set not in \
                                        self.look_back_links[target_node]:
                                    new_look_back_links.add((target_node, frozenset(inferred_source_node_set)))
                                    #self.add_look_back_link(source_nodes=inferred_source_node_set, target_node=target_node)
                                    new_look_back_link_found = True

                # minimize look-back links
                if new_look_back_link_found:
                    for node, inferred_source_node_set in new_look_back_links:
                        self.add_look_back_link(source_nodes=inferred_source_node_set, target_node=node)
                    self.minimize_look_back_links()

            if new_look_ahead_link_found:

                new_look_ahead_link_found = False
                look_ahead_links_temp = self.look_ahead_links
                new_look_ahead_links: set[(Node, frozenset[Node])] = set()

                # substitution and chaining of look-ahead links
                for source_node in look_ahead_links_temp.keys():
                    for target_node_set in look_ahead_links_temp[source_node]:
                        for target_node in target_node_set:
                            for next_target_node_set in look_ahead_links_temp.get(target_node, ()):
                                inferred_target_node_set = set(
                                    (target_node_set - {target_node}) | next_target_node_set
                                )
                                if len(inferred_target_node_set) > 0 and inferred_target_node_set not in \
                                        self.look_ahead_links[source_node]:
                                    new_look_ahead_links.add((source_node, frozenset(inferred_target_node_set)))
                                    #self.add_look_ahead_link(source_node=source_node, target_nodes=inferred_target_node_set)
                                    new_look_ahead_link_found = True

                # minimize look-back links
                if new_look_ahead_link_found:
                    for source_node, inferred_target_node_set in new_look_ahead_links:
                        self.add_look_ahead_link(source_node=source_node, target_nodes=inferred_target_node_set)
                    self.minimize_look_ahead_links()

    def add_look_back_link(
            self,
            source_nodes: set[Node],
            target_node: Node
    ) -> None:
        """
        Adds a look-back link to the causal footprint.

        :param source_nodes: Source nodes of look-back link
        :param target_node: Target nodes of look-back link
        :return: None
        """
        if target_node not in self.look_back_links.keys():
            self.look_back_links[target_node] = {frozenset(source_nodes)}
        else:
            self.look_back_links[target_node].add(frozenset(source_nodes))

    def add_look_ahead_link(
            self,
            source_node: Node,
            target_nodes: set[Node]
    ) -> None:
        """
        Adds a look-ahead link to the causal footprint.

        :param source_node: Source nodes of look-ahead link
        :param target_nodes: Target nodes of look-ahead link
        :return:
        """
        if source_node not in self.look_ahead_links.keys():
            self.look_ahead_links[source_node] = {frozenset(target_nodes)}
        else:
            self.look_ahead_links[source_node].add(frozenset(target_nodes))

    def minimize_look_back_links(
            self
    ) -> None:
        """
        Minimizes source node sets of look-back links
        :return:
        """

        # identify all nodes that have at least one look-back link
        target_nodes = self.look_back_links.keys()

        for target_node in target_nodes:

            minimal_sets: set[frozenset[Node]] = set()

            # identify all source node sets of a node
            source_node_sets = self.look_back_links[target_node]

            # check every source node set whether it is a minimal set
            for source_node_set in source_node_sets:
                is_dominated = any((source_nodes < source_node_set) for source_nodes in source_node_sets)
                if not is_dominated:
                    minimal_sets.add(source_node_set)

            # replace source node sets with minimal source node sets
            self.look_back_links[target_node] = minimal_sets

    def minimize_look_ahead_links(
            self
    ) -> None:
        """
        Minimizes target node sets of look-ahead links.

        :return: None
        """

        # identify all nodes that have at least one look-ahead link
        source_nodes = self.look_ahead_links.keys()

        for source_node in source_nodes:

            minimal_sets: set[frozenset[Node]] = set()

            # identify all target node sets of a node
            target_node_sets = self.look_ahead_links[source_node]

            # check every target node set whether it is a minimal set
            for target_node_set in target_node_sets:
                is_dominated = any((target_nodes < target_node_set) for target_nodes in target_node_sets)
                if not is_dominated:
                    minimal_sets.add(target_node_set)

            # replace target node sets with minimal target node sets
            self.look_ahead_links[source_node] = minimal_sets

    def remove_look_back_links_not_in_nodes(
            self,
            nodes: set[Node]
    ) -> None:
        """
        Removes any look_back_link that contains nodes not in given node set.

        :param nodes: Nodes to keep
        :return: None
        """

        new_look_back_links: dict[Node, set[frozenset[Node]]] = defaultdict()
        for target_node, source_node_sets in self.look_back_links.items():
            if target_node in nodes:
                for source_node_set in source_node_sets:
                    if source_node_set.issubset(nodes):
                        if target_node not in new_look_back_links.keys():
                            new_look_back_links[target_node] = {source_node_set}
                        else:
                            new_look_back_links[target_node].add(source_node_set)

        self.look_back_links = new_look_back_links

    def remove_look_ahead_links_not_in_nodes(
            self,
            nodes: set[Node]
    ) -> None:
        """
        Removes any look_ahead_link that contains nodes not in given node set.

        :param nodes: Nodes to keep
        :return: None
        """

        new_look_ahead_links: dict[Node, set[frozenset[Node]]] = defaultdict()
        for source_node, target_node_sets in self.look_ahead_links.items():
            if source_node in nodes:
                for target_node_set in target_node_sets:
                    if target_node_set.issubset(nodes):
                        if source_node not in new_look_ahead_links.keys():
                            new_look_ahead_links[source_node] = {target_node_set}
                        else:
                            new_look_ahead_links[source_node].add(target_node_set)

        self.look_ahead_links = new_look_ahead_links
