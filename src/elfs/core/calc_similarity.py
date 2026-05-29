from tqdm import tqdm
from elfs.core.similarity.behavioral_similarity import calculate_similarity_score
from elfs.core.objects.BusinessProcessGraph import BusinessProcessGraph
from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def behavioral_similarity(
        model_1: ExtendedPetriNet,
        model_2: ExtendedPetriNet,
        max_depth: int,
        prog_bar: tqdm,
        model_2_n: ExtendedPetriNet = None
) -> tuple[dict[str, float], list[BusinessProcessGraph]]:
    """
    Generates causal footprints of two petri nets and calculates their similarity

    :param model_1: Base petri net
    :param model_2: Comparison petri net
    :param model_2_n: Comparison petri net (negative)
    :param max_depth: Maximal search depth for causal footprints
    :param prog_bar: Progress bar for cli
    :return: Similarity score
    """

    bpgs: list[BusinessProcessGraph] = list()

    # initialize business process graphs
    bpg_1 = BusinessProcessGraph(ext_petri_net=model_1, max_depth=max_depth)
    bpgs.append(bpg_1)
    prog_bar.update(4)
    bpg_2 = BusinessProcessGraph(ext_petri_net=model_2, max_depth=max_depth)
    bpgs.append(bpg_2)
    prog_bar.update(2)

    if model_2_n is not None:
        bpg_2_n = BusinessProcessGraph(ext_petri_net=model_2_n, max_depth=max_depth)
        bpgs.append(bpg_2_n)
    prog_bar.update(2)

    similarity_scores = calculate_similarity_score(bpgs=bpgs)
    prog_bar.update(2)

    return similarity_scores, bpgs
