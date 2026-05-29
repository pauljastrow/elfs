from pathlib import Path

from pandas import DataFrame

from pm4py.objects.petri_net.exporter import exporter
from pm4py import save_vis_petri_net, write_xes as write_xes_file
from pm4py.objects.petri_net.obj import PetriNet, Marking


def write_event_log_to_xes_file(
        log: DataFrame,
        log_name: str
) -> None:
    """
    Writes event log as an .xes file.

    .xes file is written to storage: elfs/logs/.

    :param log:
    :param log_name:
    :return:
    """

    file_path = f'logs/{log_name}.xes'
    write_xes_file(log=log, file_path=file_path)


def write_petri_net_to_pnml_file(
        petri_net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
        file_path: str
) -> None:
    """
    Writes petri net to pnml file.

    .pnml file is written to storage: elfs/models/{model_name}/.

    :param petri_net: Petri net to write
    :param initial_marking: Initial marking of petri net
    :param final_marking: Final marking of petri net
    :param file_path: File path to write .pnml file at
    :return:
    """

    # write petri net to .pnml file via pm4py
    exporter.apply(
        net=petri_net,
        initial_marking=initial_marking,
        final_marking=final_marking,
        output_filename=file_path
    )


def write_petri_net_to_svg_file(
        petri_net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
        file_path: str
) -> None:
    """
    Writes petri net to svg file.

    .svg file is written to storage: elfs/models/{model_name}/.

    :param petri_net: Petri net to write
    :param initial_marking: Initial marking of petri net
    :param final_marking: Final marking of petri net
    :param file_path: File path to write .svg file at
    :return: None
    """

    # write petri net to .svg file via pm4py
    save_vis_petri_net(
        petri_net=petri_net,
        initial_marking=initial_marking,
        final_marking=final_marking,
        file_path=file_path
    )


def delete_file_from_storage(
        file_path: Path
) -> None:
    """
    Deletes file from storage.

    :param file_path: Path of file to delete
    :return: None
    """

    # delete file
    file_path.unlink(missing_ok=True)


def delete_dir_from_storage(
        dir_path: Path
) -> None:
    """
    Deletes directory from storage.

    :param dir_path: Path of directory to delete
    :return: None
    """

    # delete directory
    dir_path.rmdir()


def rename_file_from_storage(
        file_path: Path,
        new_file_path: Path
) -> None:
    """
    Renames file from storage.
    
    :param file_path: Path of file to rename
    :param new_file_path: New path of file
    :return: None
    """

    # rename file
    file_path.rename(new_file_path)
