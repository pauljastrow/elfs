from numpy import dot
from numpy.linalg import norm

from itertools import combinations

from elfs.core.objects.BusinessProcessGraph import BusinessProcessGraph


def calculate_similarity_score(
        bpgs: list[BusinessProcessGraph]
) -> dict[str, float]:
    """
    Calculate similarity score from two footprint vectors

    :param bpgs: List of business process graphs
    :return: similarity score
    """

    similarity_scores: dict[str, float] = dict()

    # calculate similarity score for every combination of business process graphs
    for bpg_1, bpg_2 in combinations(bpgs, 2):

        # create set of nodes, look-back links, and look-ahead links for terms
        nodes = set(bpg_1.nodes.values()) | set(bpg_2.nodes.values())
        look_back_links = (set({(k, frozenset(v)) for k, v in bpg_1.causal_footprint.look_back_links.items()}) |
                           set({(k, frozenset(v)) for k, v in bpg_2.causal_footprint.look_back_links.items()}))
        look_ahead_links = (set({(k, frozenset(v)) for k, v in bpg_1.causal_footprint.look_ahead_links.items()}) |
                            set({(k, frozenset(v)) for k, v in bpg_2.causal_footprint.look_ahead_links.items()}))

        # generate footprint vectors
        footprint_vector_1 = bpg_1.get_new_footprint_vector(
            nodes=nodes,
            look_back_links=look_back_links,
            look_ahead_links=look_ahead_links
        )
        footprint_vector_2 = bpg_2.get_new_footprint_vector(
            nodes=nodes,
            look_back_links=look_back_links,
            look_ahead_links=look_ahead_links
        )

        # calculate norm of footprint vectors
        norm_1 = norm(footprint_vector_1)
        norm_2 = norm(footprint_vector_2)

        # calculate similarity score
        if norm_1 == 0 or norm_2 == 0:
            similarity_score = 0
        else:
            dot_product = dot(footprint_vector_1, footprint_vector_2)
            similarity_score = dot_product / (norm_1 * norm_2)

        similarity_scores[f'{bpg_1.name} - {bpg_2.name}'] = similarity_score

    return similarity_scores
