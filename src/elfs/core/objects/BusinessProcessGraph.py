from typing import Union

from numpy import zeros, ndarray, dtype, float64

from pm4py.objects.petri_net.obj import PetriNet

from elfs.core.objects.Node import Node
from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet
from elfs.core.objects.CausalFootPrint import CausalFootprint


class BusinessProcessGraph:
    """
    General graph representation of a business process

    The general graph notation consists of nodes (activities) and edges between nodes. The behavior of the business
    process graph is described by causal footprints. Gateways are stored separately but are abstracted to nodes.
    """
    def __init__(
            self,
            ext_petri_net: ExtendedPetriNet,
            max_depth: int
    ) -> None:
        """
        Initializes a new BusinessProcessGraph object.

        :param ext_petri_net: Petri net the business process graph results from
        :param max_depth: Maximal search depth for causal footprint generation
        :return: None
        """

        self.ext_petri_net = ext_petri_net
        self.name = ext_petri_net.petri_net.name
        self.nodes: dict[str, Node] = dict()
        self.causal_footprint: CausalFootprint = CausalFootprint()

        # generate general graph notation and causal footprints
        self._generate_initial_causal_footprint(ext_petri_net=ext_petri_net)
        self.causal_footprint.generate_minimal_causal_closure_of_causal_footprint(max_depth=max_depth)
        self._remove_silent_transitions()

    def _generate_initial_causal_footprint(
            self,
            ext_petri_net: ExtendedPetriNet
    ) -> None:
        """
        Generates the initial causal footprint of a petri net.

        :param ext_petri_net: Extended petri net
        :return: None
        """

        # transform petri net transitions to nodes
        for transition in ext_petri_net.petri_net.transitions:

            node_id = transition.name
            node_label = transition.label

            # verify whether node is a task or silent transition (which are excluded)
            if node_label is None:
                node_label = node_id
                node_type = Node.NodeTypes.SILENT_TRANSITION
            else:
                node_type = Node.NodeTypes.TASK

            node = Node(
                node_id=node_id,
                node_label=node_label,
                node_type=node_type
            )
            self.add_node(node)

        for place in ext_petri_net.petri_net.places:

            producers = self.get_producers(place=place)
            consumers = self.get_consumer(place=place)

            # add look-back links
            if len(producers) > 0:

                # create set of producers
                producer_nodes: set[Node] = set()
                for producer in producers:
                    producer_nodes.add(self.get_node(producer.name))

                # create look-back links: ({producers}, consumer)
                for consumer in consumers:
                    consumer_node = self.get_node(consumer.name)
                    self.causal_footprint.add_look_back_link(source_nodes=producer_nodes, target_node=consumer_node)

            # add look-ahead links
            if len(consumers) > 0:

                # create set of consumers
                consumer_nodes: set[Node] = set()
                for consumer in consumers:
                    consumer_nodes.add(self.get_node(consumer.name))

                # create look-ahead links: (producer, {consumers})
                for producer in producers:
                    producer_node = self.get_node(producer.name)
                    self.causal_footprint.add_look_ahead_link(source_node=producer_node, target_nodes=consumer_nodes)

        # minimize causal links
        self.causal_footprint.minimize_look_back_links()
        self.causal_footprint.minimize_look_ahead_links()

    def _remove_silent_transitions(
            self
    ) -> None:
        """
        Removes silent transitions and causal links that contain them from the business process graph and its causal
        footprint.

        :return: None
        """

        # check each node whether to keep or remove
        nodes_to_keep: set[Node] = set()
        nodes_to_remove: set[Node] = set()
        for node in self.nodes.values():
            if node.type == Node.NodeTypes.SILENT_TRANSITION:
                nodes_to_remove.add(node)
            else:
                nodes_to_keep.add(node)

        # remove any causal links that contain nodes to remove
        self.causal_footprint.remove_look_back_links_not_in_nodes(nodes=nodes_to_keep)
        self.causal_footprint.remove_look_ahead_links_not_in_nodes(nodes=nodes_to_keep)

        # remove nodes from business process graph
        for node in nodes_to_remove:
            self.remove_node(node_id=node.id)

    def get_producers(
            self,
            place: PetriNet.Place,
    ) -> set[PetriNet.Transition]:
        """
        Returns the producer transitions of a petri net place.

        :param place: Place in a petri net
        :return: Producer transitions
        """

        return {arc.source for arc in place.in_arcs}

    def get_consumer(
            self,
            place: PetriNet.Place,
    ) -> set[PetriNet.Transition]:
        """
        Returns the consumer transitions of a petri net place.

        :param place: Place in a petri net
        :return: Consumer transitions
        """

        return {arc.target for arc in place.out_arcs}

    def get_new_footprint_vector(
            self,
            nodes: set[Node],
            look_back_links: set[tuple[Node, frozenset[frozenset[Node]]]],
            look_ahead_links: set[tuple[Node, frozenset[frozenset[Node]]]]
    ) -> ndarray[tuple[int], dtype[float64]]:
        """
        Returns the footprint vector of the business process graph calculated from a given set of terms.

        :param nodes: Union of nodes from two business process graphs
        :param look_back_links: Union of look-back links of two business process graphs
        :param look_ahead_links: Union of look-ahead links of two business process graphs
        :return: Footprint vector
        """

        # reformat terms
        terms = self._reformat_terms(nodes=nodes, look_back_links=look_back_links, look_ahead_links=look_ahead_links)
        graph_terms = self._reformat_terms(
            nodes=set(self.nodes.values()),
            look_back_links=set({(k, frozenset(v)) for k, v in self.causal_footprint.look_back_links.items()}),
            look_ahead_links=set({(k, frozenset(v)) for k, v in self.causal_footprint.look_ahead_links.items()})
        )

        # calculate weights for present terms
        footprint_vec = zeros(len(terms))
        for counter, term in enumerate(terms):
            if term in graph_terms:

                # calculate weight for causal links
                if isinstance(term, tuple):
                    if isinstance(term[0], Node):
                        term_length = len(term[1])
                    else:
                        term_length = len(term[0])
                    term_weight = 1 / 2 ** term_length

                # calculate weight for node
                else:
                    term_weight = 1

                footprint_vec[counter] = term_weight

        return footprint_vec

    def _reformat_terms(
            self,
            nodes: set[Node],
            look_back_links: set[tuple[Node, frozenset[frozenset[Node]]]],
            look_ahead_links: set[tuple[Node, frozenset[frozenset]]]
    ) -> Union[set[Node], set[tuple[frozenset[Node], Node]], set[tuple[Node, frozenset[Node]]]]:
        """
        Creates set of terms from dicts of nodes, look-back links, and look-ahead links.

        :param nodes: Nodes of a business process graph
        :param look_back_links: Look-back links of a process graph's causal footprint
        :param look_ahead_links: Look-ahead links of a process graph's causal footprint
        :return: Terms
        """

        # reformat look-back links
        reformatted_look_back_links: set[tuple[frozenset[Node], Node]] = set()
        for (target_node, source_nodes) in look_back_links:
            for source_node_set in source_nodes:
                reformatted_look_back_links.add((source_node_set, target_node))

        # reformat look-ahead links
        reformatted_look_ahead_links: set[tuple[Node, frozenset[Node]]] = set()
        for (source_node, target_nodes) in look_ahead_links:
            for target_node_set in target_nodes:
                reformatted_look_ahead_links.add((source_node, target_node_set))

        return nodes | reformatted_look_back_links | reformatted_look_ahead_links

    def get_node(
            self,
            node_id: str
    ) -> Node:
        """
        Returns node with a given id.

        :param node_id: ID of node
        :return: Node
        """

        return self.nodes[node_id]

    def add_node(
            self,
            node: Node
    ) -> None:
        """
        Adds node to business process graph nodes.

        :param node: Node to add
        :return: None
        """

        self.nodes[node.id] = node

    def remove_node(
            self,
            node_id: str
    ) -> None:
        """
        Removes node with given id from business process graph nodes.

        :param node_id: ID of node
        :return: None
        """

        self.nodes.pop(node_id, None)
