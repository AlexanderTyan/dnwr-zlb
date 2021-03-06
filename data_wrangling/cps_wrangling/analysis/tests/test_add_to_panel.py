import unittest

import pandas as pd
import numpy as np
from numpy import nan
import pandas.util.testing as tm

from data_wrangling.cps_wrangling.analysis import add_to_panel

class TestAddHistory(unittest.TestCase):

    def setUp(self):

        self.test = pd.HDFStore('test_store.h5')
        # will be transposed
        status_frame = pd.DataFrame({'a': [1, 1, 1, 1, 1, 1, 1, 1],
                                     'b': [1, 2, 1, 2, 1, 1, 1, 3],
                                     'c': [3, 1, 1, 1, 3, 3, 3, 1],
                                     'd': [3, 1, 1, 3, 1, 1, 1, 5],
                                     'e': [5, 1, 1, 1, 3, 3, 3, 3],
                                     'f': [5, 1, 1, 5, 5, 5, 1, 1],
                                     'g': [5, 1, 1, 3, 1, 1, 6, 1],
                                     'h': [1, 1, 1, 3, 1, 1, 3, 1],
                                     'i': [1, 1, 1, 5, 1, 1, 1, 2]
                                     }, index=range(1, 9)).T
        self.wp = pd.Panel({'labor_status': status_frame})

    def test_history(self):
        wp = self.wp.copy()
        result = add_to_panel._add_employment_status_last_period(wp, 'unemployed',
                                                                 inplace=False)
        expected = pd.DataFrame([np.nan]).reindex_like(wp['labor_status'])
        expected.loc['a', [4, 8]] = 0
        expected.loc['b', 4] = 0
        expected.loc['c', [4, 8]] = 1
        # expected.loc['e', 4] = np.NaN  #  donesn't match kind
        # expected.loc['f', 8] = np.Nan
        # expected.loc['g', 8] = np.Nan
        expected.loc['h', 8] = 1
        expected.loc['i', 8] = 0
        expected = expected.fillna(-1)
        expected = expected.astype('int64')

        tm.assert_frame_equal(result, expected)

    def test_status(self):
        result = add_to_panel._add_flows_panel(self.wp, inplace=False)
        expected = pd.DataFrame({'a': [nan, 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'ee'],
                                 'b': [nan, 'ee', 'ee', 'ee', 'ee', 'ee', 'ee', 'eu'],
                                 'c': [nan, 'ue', 'ee', 'ee', 'eu', 'uu', 'uu', 'ue'],
                                 'd': [nan, 'ue', 'ee', 'eu', 'ue', 'ee', 'ee', 'en'],
                                 'e': [nan, 'ne', 'ee', 'ee', 'eu', 'uu', 'uu', 'uu'],
                                 'f': [nan, 'ne', 'ee', 'en', 'nn', 'nn', 'ne', 'ee'],
                                 'g': [nan, 'ne', 'ee', 'eu', 'ue', 'ee', 'en', 'ne'],
                                 'h': [nan, 'ee', 'ee', 'eu', 'ue', 'ee', 'eu', 'ue'],
                                 'i': [nan, 'ee', 'ee', 'en', 'ne', 'ee', 'ee', 'ee']
                                 }, index=range(1, 9)).T
        expected = expected.convert_objects(convert_numeric=True)
        tm.assert_frame_equal(result, expected)

    def test_status_partial(self):
        wp = self.wp.loc[:, :, (1, 2, 3, 4, 5)]
        result = add_to_panel._add_flows_panel(wp, inplace=False)
        expected = pd.DataFrame({'a': [nan, 'ee', 'ee', 'ee', 'ee'],
                                 'b': [nan, 'ee', 'ee', 'ee', 'ee'],
                                 'c': [nan, 'ue', 'ee', 'ee', 'eu'],
                                 'd': [nan, 'ue', 'ee', 'eu', 'ue'],
                                 'e': [nan, 'ne', 'ee', 'ee', 'eu'],
                                 'f': [nan, 'ne', 'ee', 'en', 'nn'],
                                 'g': [nan, 'ne', 'ee', 'eu', 'ue'],
                                 'h': [nan, 'ee', 'ee', 'eu', 'ue'],
                                 'i': [nan, 'ee', 'ee', 'en', 'ne']
                                 }, index=range(1, 6)).T
        expected = expected.convert_objects(convert_numeric=True)
        tm.assert_frame_equal(result, expected)

    def test_history_partial(self):
        wp = self.wp.copy().loc[:, :, (1, 2, 3, 4, 5)]
        result = add_to_panel._add_employment_status_last_period(wp, 'unemployed',
                                                                 inplace=False)
        expected = pd.DataFrame([np.nan]).reindex_like(wp['labor_status'])
        expected.loc['a', 4] = 0
        expected.loc['b', 4] = 0
        expected.loc['c', 4] = 1
        expected = expected.fillna(-1)
        expected = expected.astype('int64')

        tm.assert_frame_equal(result, expected)

    def tearDown(self):

        import os
        self.test.close()
        os.remove('test_store.h5')
