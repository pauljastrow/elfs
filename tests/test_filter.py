import unittest
from pathlib import Path

from elfs.data.read import import_log, read_log
from elfs.data.write import delete_log, write_model, delete_model
from elfs.data.access.utils import LogAttributes
from elfs.data.access.converter import convert_log
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


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUp(cls):

        # import log
        import_log(
            file_path=r'data\running-small.xes',
            log_name='running',
            case_attribute='',
            case_start_date_attribute='',
            case_end_date_attribute='',
            case_completion_attribute='',
            activity_attribute='',
            time_stamp_attribute='',
            start_timestamp_attribute=''
        )

    def test_filter_case_attribute_1(self):

        # read log
        log = read_log('running')

        # filter log by attribute
        filtered_log = filter_case_attribute(
            log=log,
            attribute_key='Resource',
            attribute_values='Ellen',
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 4 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 4:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_filter_case_attribute_2(self):

        # read log
        log = read_log('running')

        # filter log by attribute
        filtered_log = filter_case_attribute(
            log=log,
            attribute_key='Resource',
            attribute_values='Pete',
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 3 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 3:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_filter_case_completion(self):

        # read log
        log = read_log('running')

        # filter log by case completion
        filtered_log = filter_case_completion(
            log=log,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            case_completion_attribute_key=LogAttributes.CASE_COMPLETION_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 5 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 5:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_filter_case_duration_1(self):

        # read log
        log = read_log('running')

        # filter log by case duration
        filtered_log = filter_case_duration(
            log=log,
            case_duration_intervals={(0, 7)},
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            case_start_date_attribute_key=LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
            case_end_date_attribute_key=LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
            case_duration_unit='D',
            selection_variant='include'
        )

        # check whether filtered log contains 1 trace
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 1:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_filter_case_duration_2(self):

        # read log
        log = read_log('running')

        # filter log by case duration
        filtered_log = filter_case_duration(
            log=log,
            case_duration_intervals={(8, 10)},
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            case_start_date_attribute_key=LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
            case_end_date_attribute_key=LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
            case_duration_unit='D',
            selection_variant='include'
        )

        # check whether filtered log contains 3 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 3:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_filter_event_repetitions(self):

        # read log
        log = read_log('running')

        # filter log by event repetitions
        filtered_log = filter_event_repetitions(
            log=log,
            repetition_intervals={(1, 1)},
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 4 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 4:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_events_1(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_events(
            log=log,
            activities=['reinitiate request'],
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 1 trace
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 1:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_events_2(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_events(
            log=log,
            activities=['examine thoroughly'],
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            selection_variant='include'
        )

        # check whether filtered log contains 3 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 3:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_start_and_end_events_1(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_start_and_end_events(
            log=log,
            start_activities=['register request'],
            end_activities=[],
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            activity_timestamp_attribute_key=LogAttributes.TIMESTAMP_ATTRIBUTE_KEY,
            set_variant='union',
            selection_variant='include'
        )

        # check whether filtered log contains 5 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 5:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_start_and_end_events_2(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_start_and_end_events(
            log=log,
            start_activities=[],
            end_activities=['reject request'],
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            activity_timestamp_attribute_key=LogAttributes.TIMESTAMP_ATTRIBUTE_KEY,
            set_variant='union',
            selection_variant='include'
        )

        # check whether filtered log contains 2 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 2:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_timeframe_1(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_timeframe(
            log=log,
            timeframe_intervals={('30.12.2010', '31.12.2010')},
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            start_date_attribute_key=LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
            end_date_attribute_key=LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
            interval_variant='start_date',
            selection_variant='include'
        )

        # check whether filtered log contains 3 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 3:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_timeframe_2(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_timeframe(
            log=log,
            timeframe_intervals={('01.01.2011', '31.12.2011')},
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            start_date_attribute_key=LogAttributes.CASE_START_DATE_ATTRIBUTE_KEY,
            end_date_attribute_key=LogAttributes.CASE_END_DATE_ATTRIBUTE_KEY,
            interval_variant='end_date',
            selection_variant='include'
        )

        # check whether filtered log contains 5 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 5:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_filter_variants(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_variants(
            log=log,
            frequency_intervals={(0, 3)},
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            interval_type='absolute',
            selection_variant='include'
        )

        # check whether filtered log contains 3 traces
        filtered_log_df = convert_log(log=filtered_log)
        num_traces = filtered_log_df[LogAttributes.CASE_ATTRIBUTE_KEY].nunique()
        if num_traces == 3:
            self.assertTrue(True)
        else:
            self.assertTrue(False, num_traces)

    def test_discovery(self):

        # delete model if present
        delete_model('running')

        # read log
        log = read_log('running')

        # discover model
        petri_net = discover_model(log=log)
        petri_net.name = 'running'

        # store model
        write_model(model=petri_net, model_name='running')

        # check whether model writing was successful
        path = Path('models/running/running.pnml')
        if path.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    @classmethod
    def tearDownClass(cls):

        from pathlib import Path

        delete_log('running')
        delete_model('running')
        Path('logs').rmdir()
        Path('models').rmdir()


if __name__ == '__main__':
    unittest.main()
