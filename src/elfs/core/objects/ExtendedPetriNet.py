from pm4py.objects.petri_net.obj import PetriNet, Marking

from elfs.core.objects.Gateway import Gateway


class ExtendedPetriNet:
    """
    ExtendedPetriNet describes a petri net.

    The pm4py PetriNet is extended with additional information from the underlying event log.
    """
    def __init__(
            self,
            petri_net: PetriNet,
            initial_marking: Marking,
            final_marking: Marking,
            case_count: int,
            variant_count: int
    ) -> None:
        """
        Initializes a new ExtendedPetriNet object.

        :param petri_net: Petri net the business process graph results from
        :param initial_marking: Initial marking of the petri net
        :param final_marking: Final marking of the petri net
        :param case_count: Number of cases of the underlying event log
        :param variant_count: Number of variants of the underlying event log
        :return: None
        """
        self.petri_net = petri_net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.case_count = case_count
        self.variant_count = variant_count

        self.gateways: set[Gateway] = set()

    def get_number_of_activities(
            self
    ) -> int:
        """
        Returns number of activities of the petri net.

        :return: Number of activities
        """

        activity_count = 0

        # identify activities in petri net transitions and calculate number of activities
        transitions = self.petri_net.transitions
        for transition in transitions:
            if transition.label is not None:
                activity_count += 1

        return activity_count

    def get_number_of_gateways(
            self
    ) -> int:
        """
        Returns number of gateways of the petri net.

        :return: Number of gateways
        """

        # identify gateways in case they have not been
        if len(self.gateways) == 0:
            self._identify_gateways()

        # calculate number of gateways
        return len(self.gateways)

    def get_number_of_places(
            self
    ) -> int:
        """
        Returns number of places of the petri net.

        :return: Number of places
        """

        # calculate number of places
        return len(self.petri_net.places)

    def get_number_of_edges(
            self
    ) -> int:
        """
        Returns number of edges of the petri net.

        :return: Number of edges
        """

        # calculate number of edges
        return len(self.petri_net.arcs)

    def get_number_of_gateway_connections(
            self
    ) -> list:
        """
        Returns a list of the number of the connections per gateway of the petri net.

        :return: List with gateway connections
        """

        # identify gateways in case they have not been
        if len(self.gateways) == 0:
            self._identify_gateways()

        # crate list with number of connections per gateway
        return list(gateway.number_in_edges + gateway.number_out_edges for gateway in self.gateways)

    def get_case_count(
            self
    ) -> int:
        """
        Returns number of cases of the underlying event log.

        :return: Number of cases
        """

        return self.case_count

    def get_variant_count(
            self
    ) -> int:
        """
        Returns number of variants of the underlying event log.

        :return: Number of variants
        """

        return self.variant_count

    def _identify_gateways(
            self
    ) -> None:
        """
        Identifies and then sets gateways of the petri net.

        Identifies and-gateways from transitions with multiple incoming or outgoing connections.
        Identifies xor-gateways from places with multiple incoming or outgoing connections.

        :return: None
        """

        # Identify and-gateways in transitions
        transitions = self.petri_net.transitions
        for transition in transitions:
            if len(transition.in_arcs) == 1 and len(transition.out_arcs) > 1:
                gateway = Gateway(
                    gateway_id=transition.name,
                    gateway_type=Gateway.GatewayTypes.AND_SPLIT,
                    number_in_edges=len(transition.in_arcs),
                    number_out_edges=len(transition.out_arcs),
                )
                self.gateways.add(gateway)

            elif len(transition.in_arcs) > 1 and len(transition.out_arcs) == 1:
                gateway = Gateway(
                    gateway_id=transition.name,
                    gateway_type=Gateway.GatewayTypes.AND_JOIN,
                    number_in_edges=len(transition.in_arcs),
                    number_out_edges=len(transition.out_arcs)
                )
                self.gateways.add(gateway)

        # Identify xor-gateways in places
        places = self.petri_net.places
        for place in places:
            if len(place.in_arcs) <= 1 and len(place.out_arcs) > 1:
                gateway = Gateway(
                    gateway_id=place.name,
                    gateway_type=Gateway.GatewayTypes.XOR_SPLIT,
                    number_in_edges=len(place.in_arcs),
                    number_out_edges=len(place.out_arcs)
                )
                self.gateways.add(gateway)

            elif len(place.in_arcs) > 1 and len(place.out_arcs) <= 1:
                gateway = Gateway(
                    gateway_id=place.name,
                    gateway_type=Gateway.GatewayTypes.XOR_SPLIT,
                    number_in_edges=len(place.in_arcs),
                    number_out_edges=len(place.out_arcs)
                )
                self.gateways.add(gateway)
