from enum import StrEnum


class Gateway:
    """
    Gateway describes a gateway candidate in a business process graph.
    """

    class GatewayTypes(StrEnum):
        """
        Types of supported gateway candidates
        """
        AND_SPLIT = 'and_split'
        AND_JOIN = 'and_join'
        XOR_SPLIT = 'xor_split'
        XOR_JOIN = 'xor_join'

    def __init__(
            self,
            gateway_id: str,
            gateway_type: GatewayTypes,
            number_in_edges: int,
            number_out_edges: int
    ) -> None:
        """
        Initializes a new Gateway object.

        :param gateway_id: ID of gateway
        :param gateway_type: Type of gateway
        :param number_in_edges: Number of edges going in gateway
        :param number_out_edges: Number of edges going out gateway
        :return: None
        """

        self.id = gateway_id
        self.type = gateway_type
        self.number_in_edges = number_in_edges
        self.number_out_edges = number_out_edges

    def __eq__(
            self,
            other
    ) -> bool:
        """
        Checks equality of a Gateway object with another object.

        :param other: Object to compare
        :return: bool
        """

        if not isinstance(other, Gateway):
            return NotImplemented
        else:
            return self.id == other.id and self.type == other.type

    def __hash__(
            self
    ) -> int:
        """
        Returns hash value for Gateway object.

        :return: Hash value
        """

        return hash((self.id, self.type))
