import unittest
from pathlib import Path

from elfs.data.read import import_log
from elfs.data.write import delete_log


class MyTestCase(unittest.TestCase):

    def test_log_import(self):

        # delete log if present
        delete_log(log_name='running')

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

        # check whether log import was successful
        path = Path('logs/running.xes')
        if path.exists():
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    @classmethod
    def tearDownClass(cls):

        from pathlib import Path

        delete_log('running')
        Path('logs').rmdir()


if __name__ == '__main__':
    unittest.main()
