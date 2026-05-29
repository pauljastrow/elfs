import unittest
from pathlib import Path

from elfs.data.read import import_log, read_log
from elfs.data.write import delete_log, write_model, delete_model, rename_log, rename_model
from elfs.core.discover import discover_model


class MyTestCase(unittest.TestCase):

    def test_rename_log(self):

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

        # rename log file
        rename_log(log_name='running', new_log_name='running-example')

        # check whether log file was successfully renamed
        path = Path('logs/running-example.xes')
        if path.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_delete_log(self):

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

        # delete log
        delete_log(log_name='running')

        # check whether log was successfully deleted
        path = Path('logs/running.xes')
        if not path.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_rename_model(self):

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

        # read log
        log = read_log('running')

        # discover model
        petri_net = discover_model(log=log)
        petri_net.name = 'running'

        # store model
        write_model(model=petri_net, model_name='running')

        # rename model file
        rename_model(model_name='running', new_model_name='running-example')

        # check whether model files was successfully renamed
        path_pnml = Path('models/running-example/running-example.pnml')
        path_svg = Path('models/running-example/running-example.svg')
        if path_pnml.exists() and path_svg.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_delete_model(self):

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

        # read log
        log = read_log('running')

        # discover model
        petri_net = discover_model(log=log)
        petri_net.name = 'running'

        # store model
        write_model(model=petri_net, model_name='running')

        # rename model file
        delete_model(model_name='running')

        # check whether model files was successfully renamed
        path = Path('models/running-example')
        if not path.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    @classmethod
    def tearDownClass(cls):

        from pathlib import Path

        delete_log('running')
        delete_log('running-example')
        delete_model('running')
        delete_model('running-example')
        Path('logs').rmdir()
        Path('models').rmdir()


if __name__ == '__main__':
    unittest.main()
