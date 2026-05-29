from argparse import (ArgumentParser, Namespace)

from itertools import combinations

from typing import Any

from tqdm import tqdm

from textwrap import fill

from pm4py.objects.log.obj import EventLog

from elfs.utils import (
    validate_input,
    validate_log_name,
    validate_reference_model,
    print_matrixwise_similarity_analysis_output,
    print_pairwise_similarity_analysis_output
)
from elfs.data.write import delete_model, rename_log, rename_model, delete_log, write_log
from elfs.data.read import get_all_stored_logs, get_all_stored_models
from elfs.data.read import (import_log, read_log, read_model)
from elfs.core.filter import (
    filter_case_attribute,
    filter_case_completion,
    filter_case_duration,
    filter_event_repetitions,
    filter_events,
    filter_start_and_end_events,
    filter_timeframe,
    filter_variants
)
from elfs.core.discover import discover_model
from elfs.data.write import write_model
from elfs.core.calc_similarity import behavioral_similarity
from elfs.core.analyze_complexity import (
    analyze_model_complexity,
    analyze_log_complexity,
    analyze_model_complexity_via_cnc
)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    # data import
    import_parser = subparsers.add_parser(name='import', help='Import event log')
    import_parser.set_defaults(func=cmd_import_data)
    import_parser.add_argument('-file_path', help='File path to import event log')
    import_parser.add_argument('-name', help='Name of event log')
    import_parser.add_argument('-case_attribute_key', help='Case attribute name from event log')
    import_parser.add_argument(
        '-case_start_date_attribute_key', help='Case start date attribute name from event log'
    )
    import_parser.add_argument(
        '-case_end_date_attribute_key', help='Case end date attribute name from event log'
    )
    import_parser.add_argument(
        '-case_completion_attribute_key', help='Case completion attribute name from event log'
    )
    import_parser.add_argument('-activity_attribute_key', help='Activity attribute name from event log')
    import_parser.add_argument(
        '-timestamp_attribute_key', help='Timestamp attribute from event log'
    )
    import_parser.add_argument(
        '-start_timestamp_attribute_key', help='Activity start timestamp attribute from event log'
    )

    # data manager
    data_management_parser = subparsers.add_parser(name='manage', help='Data management')
    data_management_parser.set_defaults(func=cmd_manage_data)
    data_management_parser.add_argument('-data_object_type', help='Data object type: log, model')
    data_management_parser.add_argument('-data_object_name', help='Name of data object')
    data_management_parser.add_argument('-data_object_name_new', help='New name of data object')
    data_management_parser.add_argument('-task', choices=['delete', 'update'], help='Delete data object')

    # filter event log
    filter_parser = subparsers.add_parser(name='filter', help='Analyze event log')
    filter_parser.set_defaults(func=cmd_filter_and_discover)

    # global filter arguments
    filter_parser.add_argument('-log_name', help='Name of event log')
    filter_parser.add_argument('-model_name', help='Name of model')
    filter_parser.add_argument('-type', help='Name of event log filter')
    filter_parser.add_argument('-variant', help='Variant of event log filter')
    filter_parser.add_argument('-store_log', help='Store filtered event log')

    # case duration filter specific arguments
    filter_parser.add_argument('-case_duration', help='Duration intervals of cases')
    filter_parser.add_argument('-case_duration_unit', help='Unit if case duration')

    # timeframe filter specific arguments
    filter_parser.add_argument('-timeframe', help='Timeframe intervals of cases')
    filter_parser.add_argument(
        '-interval_variant',
        help='Variant of the filter that either considers the case start date, end date, or both: '
             '[start_date, end_date, both]'
    )

    # event filter specific arguments
    filter_parser.add_argument('-activities', help='List of activities')

    # start and end event filter specific arguments
    filter_parser.add_argument('-start_activities', help='List of start activities')
    filter_parser.add_argument('-end_activities', help='List of end activities')
    filter_parser.add_argument('-set_variant', help='Filter variant: intersection, union')
    filter_parser.add_argument('-selection_variant', help='Filter variant: include, exclude')

    # case attribute filter specific arguments
    filter_parser.add_argument('-attribute', help='Name of case attribute')
    filter_parser.add_argument('-attribute_data_type',
                                 choices=['alphabetical', 'numerical'],
                                 help='Data type of case attribute')
    filter_parser.add_argument('-value_type',
                                 choices=['value', 'list', 'interval'],
                                 help='Data type of value(s)')
    filter_parser.add_argument('-attribute_value', help='Value of case attribute')
    filter_parser.add_argument('-values', help='List of attribute values')

    # case variants filter specific arguments
    filter_parser.add_argument('-frequency_intervals', help='Frequency interval of variants')
    filter_parser.add_argument('-interval_type', help='Interval type: absolute or relative')

    # event repetitions filter specific arguments
    filter_parser.add_argument('-repetitions', help='Number of repetition intervals')

    # similarity analysis
    similarity_parser = subparsers.add_parser(name='similarity', help='Calculate similarity score between two models')
    similarity_parser.set_defaults(func=cmd_calculate_similarity)
    similarity_parser.add_argument(
        '-output',
        choices=['pairwise', 'matrixwise'],
        help='Output type of similarity analysis'
    )
    similarity_parser.add_argument('-model_1', help='Model for pairwise similarity score calculation')
    similarity_parser.add_argument('-model_2', help='Model for pairwise similarity score calculation')
    similarity_parser.add_argument('-models', help='Models for matrixwise similarity score calculation')
    similarity_parser.add_argument(
        '-negative_model',
        choices=['true', 'false'],
        help='Inclusion of negative comparison model')
    similarity_parser.add_argument(
        '-max_depth', help='Maximal search depth for causal footprints')

    return parser


def cmd_import_data(args: Namespace) -> None:

    # provide user explanations
    print(
        '\nEvent Log Import\n'
        '----------------------------------------------------------------------------------------------------'
    )

    # demand user input
    file_path = validate_input(input_arg=args.file_path, arg_name='File Path')
    log_name = validate_input(input_arg=args.name, arg_name='Log Name')
    case_attribute_key = validate_input(input_arg=args.case_attribute_key, arg_name='Case Attribute Key')
    case_start_date_attribute_key = validate_input(input_arg=args.case_start_date_attribute_key,
                                                   arg_name='Case Start Date Attribute Key')
    case_end_date_attribute_key = validate_input(input_arg=args.case_end_date_attribute_key,
                                                 arg_name='Case End Date Attribute Key')
    case_completion_attribute_key = validate_input(input_arg=args.case_completion_attribute_key,
                                                   arg_name='Case Completion Attribute Key')
    activity_attribute_key = validate_input(input_arg=args.activity_attribute_key,
                                            arg_name='Activity Attribute Key')
    timestamp_attribute_key = validate_input(input_arg=args.timestamp_attribute_key,
                                             arg_name='Timestamp Attribute Key')
    start_timestamp_attribute_key = validate_input(input_arg=args.start_timestamp_attribute_key,
                                                   arg_name='Activity Start Date Attribute Key')

    print('----------------------------------------------------------------------------------------------------')

    # import event log from external file
    import_log(
        file_path=file_path,
        log_name=log_name,
        case_attribute=case_attribute_key,
        case_start_date_attribute=case_start_date_attribute_key,
        case_end_date_attribute=case_end_date_attribute_key,
        case_completion_attribute=case_completion_attribute_key,
        activity_attribute=activity_attribute_key,
        time_stamp_attribute=timestamp_attribute_key,
        start_timestamp_attribute=start_timestamp_attribute_key
    )

    print('✓ Event log successfully imported!\n')


def cmd_manage_data(args: Namespace) -> None:

    # provide user explanation
    print('\nData Management\n'
          '----------------------------------------------------------------------------------------------------\n'
          ' i Data Type: log, model\n'
          '----------------------------------------------------------------------------------------------------'
          )

    data_object_type = validate_input(input_arg=args.data_object_type, arg_name='Data object type')

    if data_object_type == 'log':
        log_names = ', '.join(get_all_stored_logs())
        print(
            '----------------------------------------------------------------------------------------------------\n'
            f' i Stored Logs: {fill(log_names, width=83, subsequent_indent='                ')}\n'
            ' i Task: delete, rename\n'
            '----------------------------------------------------------------------------------------------------'
        )
        data_object_name = validate_input(input_arg=args.data_object_name, arg_name='Data object name')
        task = validate_input(input_arg=args.task, arg_name='Task')
        if task == 'delete':
            delete_log(log_name=data_object_name)
            print(
                '----------------------------------------------------------------------------------------------------\n'
                '✓ Event log successfully deleted!\n'
            )
        elif task == 'rename':
            data_object_name_new = validate_input(input_arg=args.data_object_name_new, arg_name='New data object name')
            rename_log(log_name=data_object_name, new_log_name=data_object_name_new)
            print(
                '----------------------------------------------------------------------------------------------------\n'
                '✓ Event log successfully renamed!\n'
            )

    elif data_object_type == 'model':
        model_names = ', '.join(get_all_stored_models())
        print(
            '----------------------------------------------------------------------------------------------------\n'
            f' i Stored Models: {fill(model_names, width=81, subsequent_indent='                  ')}\n'
            ' i Task: delete, rename\n'
            '----------------------------------------------------------------------------------------------------'
        )
        data_object_name = validate_input(input_arg=args.data_object_name, arg_name='Data object name')
        task = validate_input(input_arg=args.task, arg_name='Task')
        if task == 'delete':
            delete_model(model_name=data_object_name)
            print(
                '----------------------------------------------------------------------------------------------------\n'
                '✓ Process model successfully deleted!\n'
            )
        elif task == 'rename':
            data_object_name_new = validate_input(input_arg=args.data_object_name_new, arg_name='New data object name')
            rename_model(model_name=data_object_name, new_model_name=data_object_name_new)
            print(
                '----------------------------------------------------------------------------------------------------\n'
                '✓ Process model successfully renamed!\n'
            )


def cmd_filter_and_discover(args: Namespace) -> None:

    # provide user explanations
    log_names = ', '.join(get_all_stored_logs())
    print(
        '\nEvent Log Filtering and Discovery\n'
        '----------------------------------------------------------------------------------------------------\n'
        f' i Stored Logs: {fill(log_names, width=83, subsequent_indent='                ')}\n'
        ' i Filter: case_attribute, case_completion, case_duration, event_repetitions,\n'
        '   events, start_and_end_events, timeframe, variants, none\n'
        ' i Store Log: true, false\n'
        '----------------------------------------------------------------------------------------------------'
        )

    log_name = validate_input(input_arg=args.log_name, arg_name='Name of event log')
    model_name = validate_input(input_arg=args.model_name, arg_name='Name for model')
    store_log_filtered = validate_input(input_arg=args.store_log, arg_name='Store filtered log')
    filter_type = validate_input(input_arg=args.type, arg_name='Filter')

    # validate log name and read from storage directory
    log_name = validate_log_name(log_name)
    log = read_log(log_name)

    # filter log
    if filter_type == 'none':

        # discover model
        petri_net = discover_model(log=log)
        petri_net.name = model_name

        # store model
        write_model(model=petri_net, model_name=model_name)
    else:

        # filter log
        log_filtered, log_filtered_n = filtering(log=log, args=args, filter_type=filter_type)

        # store filtered log if demanded
        if store_log_filtered == 'true':
            name_log_filtered = model_name
            write_log(log=log_filtered, log_name=name_log_filtered)

        # discover and store models
        petri_net = discover_model(log=log_filtered)
        petri_net.name = model_name
        write_model(model=petri_net, model_name=model_name)

        try:
            petri_net_n = discover_model(log=log_filtered_n)
            petri_net_n.name = f'{model_name}_n'
            write_model(model=petri_net_n, model_name=f'{model_name}_n')
        except KeyError:
            pass

    print(
        '----------------------------------------------------------------------------------------------------\n'
        '✓ Process model successfully discovered and stored!\n'
    )


def cmd_calculate_similarity(args: Namespace) -> None:

    # provide user explanations
    model_names = ', '.join(get_all_stored_models())
    print(
        '\nEvent Log Filtering and Discovery\n'
        '----------------------------------------------------------------------------------------------------\n'
        f' i Stored Models: {fill(model_names, width=81, subsequent_indent='                  ')}\n'
        ' i Output Type: pairwise, matrixwise\n'
        ' i Neg. Model: true, false\n'
        ' i Split models with ;\n'
        '----------------------------------------------------------------------------------------------------'
    )

    # demand user input and validate input
    output_type = validate_input(input_arg=args.output, arg_name='Output Type')

    if output_type == 'pairwise':

        # demand user input and validate input
        model_1_name = validate_input(input_arg=args.model_1, arg_name='Base Model')
        model_1_name = validate_reference_model(model_name=model_1_name)
        model_2_name = validate_input(input_arg=args.model_2, arg_name='Comparison Model')
        model_2_name = validate_reference_model(model_name=model_2_name)
        n_model = validate_input(input_arg=args.negative_model, arg_name='Inclusion of neg. Comparison Model')
        max_depth = validate_input(input_arg=args.max_depth, arg_name='Max_depth', number=True)
        model_names = [model_1_name, model_2_name]

        # read models
        ext_petri_net_1 = read_model(model_name=model_1_name)
        ext_petri_net_2 = read_model(model_name=model_2_name)
        ext_petri_nets = {ext_petri_net_1, ext_petri_net_2}

        # read and validate negative model if required
        if n_model == 'true':
            model_2_n_name = validate_reference_model(model_name=f'{model_2_name}_n')
            ext_petri_net_2_n = read_model(model_name=model_2_n_name)
            ext_petri_nets.add(ext_petri_net_2_n)
            model_names.append(model_2_n_name)
        else:
            # model_2_n_name = ''
            ext_petri_net_2_n = None

        # progress bar
        print('----------------------------------------------------------------------------------------------------')
        prog_bar = tqdm(total=10, ncols=100, desc='Processing', leave=False)

        # calculate similarity
        similarity_scores, bpgs = behavioral_similarity(
            model_1=ext_petri_net_1,
            model_2=ext_petri_net_2,
            model_2_n=ext_petri_net_2_n,
            max_depth=max_depth,
            prog_bar=prog_bar
        )

        prog_bar.close()

        # calculate complexity kpis
        log_complexity_kpis = analyze_log_complexity(ext_petri_nets=ext_petri_nets)
        model_complexity_kpis = analyze_model_complexity(ext_petri_nets=ext_petri_nets)

        # print output
        print_pairwise_similarity_analysis_output(
            model_names=model_names,
            similarity_scores=similarity_scores,
            log_complexity_kpis=log_complexity_kpis,
            model_complexity_kpis=model_complexity_kpis,
            n_model=n_model
        )

    if output_type == 'matrixwise':

        # demand user input and validate it
        models = validate_input(input_arg=args.models, arg_name='Models', multiple=True)
        for model in models:
            validate_reference_model(model)
        max_depth = validate_input(input_arg=args.max_depth, arg_name='Max_depth', number=True)

        # read petri nets
        ext_petri_nets = set()
        for model in models:
            ext_petri_net = read_model(model_name=model)
            ext_petri_nets.add(ext_petri_net)

        # progress bar
        print(
            '----------------------------------------------------------------------------------------------------')
        prog_bar = tqdm(total=10*len(models), ncols=100, desc='Processing', leave=False)

        # calculate similarity for every model combination
        similarity_scores: dict[str, float] = dict()
        for ext_petri_net_1, ext_petri_net_2 in combinations(ext_petri_nets, 2):
            temp_similarity_scores, bpgs = behavioral_similarity(
                model_1=ext_petri_net_1,
                model_2=ext_petri_net_2,
                max_depth=max_depth,
                prog_bar=prog_bar
            )
            similarity_scores = similarity_scores | temp_similarity_scores

        prog_bar.close()

        # calculate cnc values per model
        cnc_values = analyze_model_complexity_via_cnc(ext_petri_nets=ext_petri_nets)

        # print output
        print_matrixwise_similarity_analysis_output(model_names=models, similarity_scores=similarity_scores, cnc_values=cnc_values)


def filtering(log: EventLog, args: Namespace, filter_type: Any) -> [EventLog, EventLog]:

    match filter_type:
        case 'case_attribute':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Data Type: alphabetical, numerical, boolean\n'
                ' i Value Type: value, list, interval\n'
                ' i Input intervals as [a, b] and split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
            )

            attribute = validate_input(input_arg=args.attribute, arg_name='Attribute')
            data_type = validate_input(input_arg=args.attribute_data_type, arg_name='Data Type')
            value_type = validate_input(input_arg=args.value_type, arg_name='Value Type')

            number = False
            multiple = False
            interval = False
            boolean = False
            if data_type == 'numerical':
                number = True
            if data_type == 'boolean':
                boolean = True
            if value_type == 'list':
                multiple = True
            if value_type == 'interval':
                interval = True

            values = validate_input(input_arg=args.values, arg_name='Values',
                                    number=number, multiple=multiple, interval=interval, boolean=boolean)

            log_filtered = filter_case_attribute(
                log=log,
                attribute_key=attribute,
                attribute_values=values,
                selection_variant='include'
            )
            log_filtered_n = filter_case_attribute(
                log=log,
                attribute_key=attribute,
                attribute_values=values,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'case_completion':

            print(
                '----------------------------------------------------------------------------------------------------\n'
            )

            log_filtered = filter_case_completion(
                log=log,
                selection_variant='include'
            )
            log_filtered_n = filter_case_completion(
                log=log,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'case_duration':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Case duration unit: s, m, h, D, W\n'
                ' i Input intervals as [a, b] and split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
            )

            case_duration = validate_input(
                input_arg=args.case_duration,
                arg_name='Case duration intervals',
                number=True,
                multiple=True,
                interval=True
            )
            case_duration_unit = validate_input(
                input_arg=args.case_duration_unit,
                arg_name='Case duration unit',
            )

            log_filtered = filter_case_duration(
                log=log,
                case_duration_intervals=case_duration,
                case_duration_unit=case_duration_unit,
                selection_variant='include'
            )
            log_filtered_n = filter_case_duration(
                log=log,
                case_duration_intervals=case_duration,
                case_duration_unit=case_duration_unit,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'event_repetitions':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Input intervals as [a, b] and split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
            )

            repetition_intervals = validate_input(
                input_arg=args.repetitions,
                arg_name='Repetitions',
                number=True,
                multiple=True,
                interval=True
            )

            log_filtered = filter_event_repetitions(
                log=log,
                repetition_intervals=repetition_intervals,
                selection_variant='include'
            )
            log_filtered_n = filter_event_repetitions(
                log=log,
                repetition_intervals=repetition_intervals,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'events':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
                )

            activities = validate_input(input_arg=args.activities, arg_name='Activities', multiple=True)

            log_filtered = filter_events(
                log=log,
                activities=activities,
                selection_variant='include'
            )
            log_filtered_n = filter_events(
                log=log,
                activities=activities,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'start_and_end_events':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Set_variant: union, intersection\n'
                '----------------------------------------------------------------------------------------------------'
            )

            start_activities = validate_input(
                input_arg=args.start_activities,
                arg_name='Start_activities',
                multiple=True
            )
            end_activities = validate_input(
                input_arg=args.end_activities,
                arg_name='End_activities',
                multiple=True
            )
            set_variant = validate_input(input_arg=args.set_variant, arg_name='Set_variant')

            log_filtered = filter_start_and_end_events(
                log=log,
                start_activities=start_activities,
                end_activities=end_activities,
                set_variant=set_variant,
                selection_variant='include'
            )
            log_filtered_n = filter_start_and_end_events(
                log=log,
                start_activities=start_activities,
                end_activities=end_activities,
                set_variant=set_variant,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'timeframe':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Input intervals as [a, b] and split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
            )

            timeframe = validate_input(input_arg=args.timeframe, arg_name='Timeframe', multiple=True, interval=True)
            interval_variant = validate_input(input_arg=args.interval_variant, arg_name='Interval_variant')

            log_filtered = filter_timeframe(
                log=log,
                timeframe_intervals=timeframe,
                interval_variant=interval_variant,
                selection_variant='include'
            )
            log_filtered_n = filter_timeframe(
                log=log,
                timeframe_intervals=timeframe,
                interval_variant=interval_variant,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n

        case 'variants':

            print(
                '----------------------------------------------------------------------------------------------------\n'
                ' i Interval_type: absolute, relative\n'
                ' i Input intervals as [a, b] and split objects with ;\n'
                '----------------------------------------------------------------------------------------------------'
            )

            frequency_intervals = validate_input(
                input_arg=args.frequency_intervals,
                arg_name='Frequency_intervals',
                number=True,
                multiple=True,
                interval=True
            )
            interval_type = validate_input(input_arg=args.interval_type, arg_name='Interval_type')

            log_filtered = filter_variants(
                log=log,
                frequency_intervals=frequency_intervals,
                interval_type=interval_type,
                selection_variant='include'
            )
            log_filtered_n = filter_variants(
                log=log,
                frequency_intervals=frequency_intervals,
                interval_type=interval_type,
                selection_variant='exclude'
            )

            return log_filtered, log_filtered_n


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
