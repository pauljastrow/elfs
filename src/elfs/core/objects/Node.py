from enum import StrEnum


class Node:
    """
    Node describes a node in a business process graph.
    """

    class NodeTypes(StrEnum):
        """
        Types of nodes
        """

        TASK = 'task'
        SILENT_TRANSITION = 'silent_transition'

    def __init__(
            self,
            node_id: str,
            node_label: str,
            node_type: NodeTypes
    ) -> None:
        """
        Initializes a new Node object.

        :param node_id: ID of node
        :param node_label: Label of node
        :param node_type: Type of node
        :return: None
        """

        self.id = node_id
        self.label = node_label
        self.type = node_type

    def __eq__(
            self,
            other
    ) -> bool:
        """
        Checks equality of a Node object with another object.

        :param other: Object to compare
        :return: bool
        """

        if not isinstance(other, Node):
            return NotImplemented
        else:
            return self.id == other.id
            # return self.label == other.label and self.type == self.type

    def __hash__(
            self
    ) -> int:
        """
        Returns hash value for Node object.

        :return: Hash value
        """

        return hash(self.id)
        # return hash((self.label, self.type))
