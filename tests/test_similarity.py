import unittest

from utils import compare_look_back_links, compare_look_ahead_links
from elfs.data.read import import_log, read_log, read_model
from elfs.data.write import delete_log, write_model, delete_model
from elfs.data.access.utils import LogAttributes
from elfs.core.filter import filter_events, filter_start_and_end_events
from elfs.core.discover import discover_model
from elfs.core.objects.BusinessProcessGraph import BusinessProcessGraph
from elfs.core.calc_similarity import calculate_similarity_score
from elfs.core.complexity_kpis.avg_gateway_degree import calculate_avg_gateway_degree
from elfs.core.complexity_kpis.case_count import calculate_case_count
from elfs.core.complexity_kpis.cnc import calculate_cnc
from elfs.core.complexity_kpis.max_gateway_degree import calculate_max_gateway_degree
from elfs.core.complexity_kpis.noa import calculate_noa
from elfs.core.complexity_kpis.nof import calculate_nof
from elfs.core.complexity_kpis.nog import calculate_nog
from elfs.core.complexity_kpis.variant_count import calculate_variant_count


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

        # read log
        log = read_log('running')

        # discover model
        petri_net = discover_model(log=log)
        petri_net.name = 'running'

        # store model
        write_model(model=petri_net, model_name='running')

    def test_bpg_generation_1(self):

        # read petri net
        ext_petri_net = read_model('running')

        # generate bpg
        bpg = BusinessProcessGraph(ext_petri_net=ext_petri_net, max_depth=1)

        # set correct values
        node_keys = {'register request', 'decide', 'reject request', 'check ticket', 'pay compensation',
                     'reinitiate request', 'examine thoroughly', 'examine casually'}
        look_back_links = {
            'examine casually': {frozenset({'register request'})},
            'decide' : {frozenset({'check ticket', 'examine casually', 'examine thoroughly'})},
            'reinitiate request': {frozenset({'decide'})},
            'reject request': {frozenset({'decide'})},
            'pay compensation': {frozenset({'decide'})},
        }
        look_ahead_links = {
            'examine casually': {frozenset({'decide'})},
            'check ticket': {frozenset({'decide'})},
            'decide': {frozenset({'reinitiate request', 'reject request', 'pay compensation'})},
            'reinitiate request': {frozenset({'examine thoroughly'})},
            'examine thoroughly': {frozenset({'decide'})},
        }

        # check whether bpg generated correctly
        test_look_back_links = compare_look_back_links(bpg=bpg, look_back_links=look_back_links)
        test_look_ahead_links = compare_look_ahead_links(bpg=bpg, look_ahead_links=look_ahead_links)
        if bpg.name == 'running' and bpg.nodes.keys() == node_keys and test_look_back_links and test_look_ahead_links:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_bpg_generation_2(self):

        # read petri net
        ext_petri_net = read_model('running')

        # generate bpg
        bpg = BusinessProcessGraph(ext_petri_net=ext_petri_net, max_depth=2)

        # set correct values
        node_keys = {'register request', 'decide', 'reject request', 'check ticket', 'pay compensation',
                     'reinitiate request', 'examine thoroughly', 'examine casually'}
        look_back_links = {
            'examine casually': {frozenset({'register request'})},
            'decide' : {frozenset({'check ticket', 'examine casually', 'examine thoroughly'}), frozenset({'check ticket', 'register request', 'examine thoroughly'})},
            'reinitiate request': {frozenset({'decide'}), frozenset({'check ticket', 'examine casually', 'examine thoroughly'})},
            'reject request': {frozenset({'decide'}), frozenset({'check ticket', 'examine casually', 'examine thoroughly'})},
            'pay compensation': {frozenset({'decide'}), frozenset({'check ticket', 'examine casually', 'examine thoroughly'})},
            'check ticket': {frozenset({'register request'})},
            'examine thoroughly': {frozenset({'register request', 'reinitiate request'})}
        }
        look_ahead_links = {
            'examine casually': {frozenset({'decide'}), frozenset({'reinitiate request', 'reject request', 'pay compensation'})},
            'check ticket': {frozenset({'decide'}), frozenset({'reinitiate request', 'reject request', 'pay compensation'})},
            'decide': {frozenset({'reinitiate request', 'reject request', 'pay compensation'}), frozenset({'examine thoroughly', 'reject request', 'pay compensation'})},
            'reinitiate request': {frozenset({'examine thoroughly'}), frozenset({'decide'})},
            'examine thoroughly': {frozenset({'decide'}), frozenset({'reinitiate request', 'reject request', 'pay compensation'})},
            'register request': {frozenset({'check ticket', 'examine casually'}), frozenset({'examine casually', 'examine thoroughly'})},
        }

        # check whether bpg generated correctly
        test_look_back_links = compare_look_back_links(bpg=bpg, look_back_links=look_back_links)
        test_look_ahead_links = compare_look_ahead_links(bpg=bpg, look_ahead_links=look_ahead_links)
        if bpg.name == 'running' and bpg.nodes.keys() == node_keys and test_look_back_links and test_look_ahead_links:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_similarity_score_1(self):

        # read petri net
        ext_petri_net = read_model('running')

        # generate bpg
        bpg = BusinessProcessGraph(ext_petri_net=ext_petri_net, max_depth=1)

        # calculate similarity
        similarity_score = calculate_similarity_score(bpgs=[bpg, bpg])

        # check whether similarity score equals 1
        if round(similarity_score['running - running'], 5) == 1:
            self.assertTrue(True)
        else:
            self.assertTrue(False, msg=f'{similarity_score} / 1')

    def test_similarity_score_2(self):

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

        # discover model
        petri_net = discover_model(log=filtered_log)
        petri_net.name = 'running_event'

        # store model
        write_model(model=petri_net, model_name='running_event')

        # read petri nets
        ext_petri_net_1 = read_model('running')
        ext_petri_net_2 = read_model('running_event')

        # generate bpg
        bpg_1 = BusinessProcessGraph(ext_petri_net=ext_petri_net_1, max_depth=0)
        bpg_2 = BusinessProcessGraph(ext_petri_net=ext_petri_net_2, max_depth=0)

        # calculate similarity
        similarity_score = calculate_similarity_score(bpgs=[bpg_1, bpg_2])

        # check whether similarity score equals 0.83961
        if round(similarity_score['running - running_event'], 5) == 0.83961:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_similarity_score_3(self):

        # read log
        log = read_log('running')

        # filter log by event events
        filtered_log = filter_start_and_end_events(
            log=log,
            start_activities=[],
            end_activities=['pay compensation'],
            activity_attribute_key=LogAttributes.ACTIVITY_ATTRIBUTE_KEY,
            case_attribute_key=LogAttributes.CASE_ATTRIBUTE_KEY,
            activity_timestamp_attribute_key=LogAttributes.TIMESTAMP_ATTRIBUTE_KEY,
            set_variant='union',
            selection_variant='include'
        )

        # discover model
        petri_net = discover_model(log=filtered_log)
        petri_net.name = 'running_end_events'

        # store model
        write_model(model=petri_net, model_name='running_end_events')

        # read petri nets
        ext_petri_net_1 = read_model('running')
        ext_petri_net_2 = read_model('running_end_events')

        # generate bpg
        bpg_1 = BusinessProcessGraph(ext_petri_net=ext_petri_net_1, max_depth=0)
        bpg_2 = BusinessProcessGraph(ext_petri_net=ext_petri_net_2, max_depth=0)

        # calculate similarity
        similarity_score = calculate_similarity_score(bpgs=[bpg_1, bpg_2])

        # check whether similarity score equals 0.86225
        if round(similarity_score['running - running_end_events'], 5) == 0.86225:
            self.assertTrue(True)
        else:
            self.assertTrue(False, similarity_score)

    def test_complexity_kpi_avg_gateway_degree(self):

        # read petri net
        ext_petri_net = read_model('running')

        avg_gateway_degree = calculate_avg_gateway_degree(ext_petri_net=ext_petri_net)

        # set correct average gateway degree
        avg_gateway_degree_cor = (3 + 3 + 4 + 4 + 3 + 2) / 6

        # check whether average gateway degree equals 3.4
        if avg_gateway_degree == avg_gateway_degree_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False, msg=f'{avg_gateway_degree} / {avg_gateway_degree_cor}')

    def test_complexity_kpi_case_count(self):

        # read petri net
        ext_petri_net = read_model('running')

        case_count = calculate_case_count(ext_petri_net=ext_petri_net)

        # set correct case count
        case_count_cor = 5

        # check whether case count equals 5
        if case_count == case_count_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_cnc(self):

        # read petri net
        ext_petri_net = read_model('running')

        cnc = calculate_cnc(
            ext_petri_net=ext_petri_net,
            nof=calculate_nof(ext_petri_net),
            noa=calculate_noa(ext_petri_net)
        )

        # set correct coefficient of network complexity
        cnc_cor = 19 / (8 + 7)

        # check whether coefficient of network complexity equals 1.26667
        if cnc == cnc_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_max_gateway_degree(self):

        # read petri net
        ext_petri_net = read_model('running')

        max_gateway_degree = calculate_max_gateway_degree(ext_petri_net=ext_petri_net)

        # set correct maximal gateway degree
        max_gateway_degree_cor = 4

        # check whether maximal gateway degree equals 4
        if max_gateway_degree == max_gateway_degree_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_noa(self):

        # read petri net
        ext_petri_net = read_model('running')

        noa = calculate_noa(ext_petri_net=ext_petri_net)

        # set correct number of activities
        noa_cor = 8

        # check whether number of activities equals 8
        if noa == noa_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_nof(self):

        # read petri net
        ext_petri_net = read_model('running')

        nof = calculate_nof(ext_petri_net=ext_petri_net)

        # set correct number of control flow elements
        nof_cor = 19

        # check whether number of control flow elements equals 19
        if nof == nof_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_nog(self):

        # read petri net
        ext_petri_net = read_model('running')

        nog = calculate_nog(ext_petri_net=ext_petri_net)

        # set correct number of control flow elements
        nog_cor = 6

        # check whether number of control flow elements equals 19
        if nog == nog_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_complexity_kpi_variant_count(self):

        # read petri net
        ext_petri_net = read_model('running')

        variant_count = calculate_variant_count(ext_petri_net=ext_petri_net)

        # set correct variant count
        variant_count_cor = 5

        # check whether variant count equals 5
        if variant_count == variant_count_cor:
            self.assertTrue(True)
        else:
            self.assertTrue(False, msg=f'{variant_count} / {variant_count_cor}')

    @classmethod
    def tearDownClass(cls):

        from pathlib import Path

        delete_log('running')
        delete_model('running')
        delete_model('running_event')
        delete_model('running_end_events')
        Path('logs').rmdir()
        Path('models').rmdir()


if __name__ == '__main__':
    unittest.main()
