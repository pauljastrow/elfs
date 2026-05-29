from pathlib import Path

from pm4py.objects.log.obj import EventLog

from elfs.data.access.utils import ensure_storage_dir, change_pnml_file_attribute_value, set_pnml_file_net_attribute
from elfs.data.access.writer import (
    write_event_log_to_xes_file,
    write_petri_net_to_pnml_file,
    write_petri_net_to_svg_file,
    delete_file_from_storage,
    delete_dir_from_storage,
    rename_file_from_storage
)
from elfs.data.access.converter import convert_log
from elfs.core.objects.ExtendedPetriNet import ExtendedPetriNet


def write_log(
        log: EventLog,
        log_name: str
) -> None:
    """
    Stores event log as a .xes file.

    :param log: Event log to store
    :param log_name: Name for event log
    :return: None
    """

    # convert event log to DataFrame
    log = convert_log(log=log)

    # store event log
    write_event_log_to_xes_file(log=log, log_name=log_name)


def write_model(
        model: ExtendedPetriNet,
        model_name: str
) -> None:
    """
    Stores petri net as a .pnml and .svg file.

    :param model: Petri net to store
    :param model_name: Name of petri net
    :return: None
    """

    # ensure existence of storage directories
    dir_path = Path('models')
    ensure_storage_dir(dir_path)
    dir_path = Path(f'models/{model_name.removesuffix('_n')}')
    ensure_storage_dir(dir_path)

    model.petri_net.name = model_name

    # save petri net as .pnml and .svg
    write_petri_net_to_pnml_file(
        petri_net=model.petri_net,
        initial_marking=model.initial_marking,
        final_marking=model.final_marking,
        file_path=f'{dir_path}/{model_name}.pnml',
    )
    write_petri_net_to_svg_file(
        petri_net=model.petri_net,
        initial_marking=model.initial_marking,
        final_marking=model.final_marking,
        file_path=f'{dir_path}/{model_name}.svg',
    )

    # write additional information to .pnml file
    set_pnml_file_net_attribute(
        file_path=Path(f'{dir_path}/{model_name}.pnml'),
        attribute='cases',
        value=str(model.case_count)
    )
    set_pnml_file_net_attribute(
        file_path=Path(f'{dir_path}/{model_name}.pnml'),
        attribute='variants',
        value=str(model.variant_count)
    )


def delete_log(log_name: str) -> None:
    """
    Delete stored event log as .xes file.

    :param log_name: Name of event log to delete
    :return: None
    """

    # ensure presence of storage directory
    dir_path = Path('logs')
    ensure_storage_dir(dir_path)

    # delete .xes file
    delete_file_from_storage(file_path=Path(f'{dir_path}/{log_name}.xes'))


def delete_model(model_name: str) -> None:
    """
    Delete stored petri net as .pnml and .svg file.

    When deleting, the model and its negative are considered. Both .pnml and .svg files are deleted.

    :param model_name: Name of model to delete
    :return: None
    """

    # ensure existence of storage directory
    dir_path = Path('models')
    ensure_storage_dir(dir_path)
    dir_path = Path(f'models/{model_name}')
    ensure_storage_dir(dir_path)

    # delete .pnml and .svg files
    delete_file_from_storage(file_path=Path(f'{dir_path}/{model_name}.pnml'))
    delete_file_from_storage(file_path=Path(f'{dir_path}/{model_name}_n.pnml'))
    delete_file_from_storage(file_path=Path(f'{dir_path}/{model_name}.svg'))
    delete_file_from_storage(file_path=Path(f'{dir_path}/{model_name}_n.svg'))
    delete_dir_from_storage(dir_path=dir_path)


def rename_log(log_name: str, new_log_name: str) -> None:
    """
    Rename stored event log.

    :param log_name: Name of event log to rename
    :param new_log_name: New name for event log
    :return: None
    """

    # ensure presence of storage directory
    dir_path = Path('logs')
    ensure_storage_dir(dir_path)

    # change file path of .xes file
    rename_file_from_storage(
        file_path=Path(f'{dir_path}/{log_name}.xes'),
        new_file_path=Path(f'{dir_path}/{new_log_name}.xes')
    )


def rename_model(model_name: str, new_model_name: str) -> None:
    """
    Rename stored petri net.

    The name of the petri net stored within the .pnml file is also changed to the new name.

    :param model_name: Name of model to rename
    :param new_model_name: New name for model
    :return: None
    """

    # ensure presence of storage directory
    dir_path = Path(f'models/{model_name}')
    ensure_storage_dir(path=dir_path)
    new_dir_path = Path(f'models/{new_model_name}')
    ensure_storage_dir(path=new_dir_path)

    # check whether negative model is present
    n_present = False
    path_n = Path(f'models/{model_name}/{model_name}_n.pnml')
    if path_n.exists():
        n_present = True


    # change file paths of .pnml and .svg files
    rename_file_from_storage(
        file_path=Path(f'{dir_path}/{model_name}.pnml'),
        new_file_path=Path(f'{new_dir_path}/{new_model_name}.pnml')
    )
    rename_file_from_storage(
        file_path=Path(f'{dir_path}/{model_name}.svg'),
        new_file_path=Path(f'{new_dir_path}/{new_model_name}.svg')
    )
    if n_present:
        rename_file_from_storage(
            file_path=Path(f'{dir_path}/{model_name}_n.pnml'),
            new_file_path=Path(f'{new_dir_path}/{new_model_name}_n.pnml')
        )
        rename_file_from_storage(
            file_path=Path(f'{dir_path}/{model_name}_n.svg'),
            new_file_path=Path(f'{new_dir_path}/{new_model_name}_n.svg')
        )

    # delete old directory
    delete_dir_from_storage(dir_path=dir_path)

    # rename petri net names
    change_pnml_file_attribute_value(
        file_path=Path(f'{new_dir_path}/{new_model_name}.pnml'),
        attribute='name',
        value=new_model_name
    )
    if n_present:
        change_pnml_file_attribute_value(
            file_path=Path(f'{new_dir_path}/{new_model_name}_n.pnml'),
            attribute='name',
            value=f'{new_model_name}_n'
        )
