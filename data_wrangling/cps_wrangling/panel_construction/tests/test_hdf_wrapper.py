import os
import unittest

import pandas as pd
import pandas.util.testing as tm

from ..hdf_wrapper import HDFHandler


class TestHDFWrapper(unittest.TestCase):

    def setUp(self):
        self.fdir = os.path.join('.', 'test_files', 'panel')

        settings = {'base_path': './test_files/'}
        months = ['1994_01', '1994_02', '1994_03']
        frequency = 'monthly'
        self.handler = HDFHandler(settings, 'panel', months, frequency)

    def test_file_creation(self):
        _ = self.handler._make_stores(self.handler.months, self.handler.frequency)
        expected = [os.path.join('test_files', 'panel', x) for x in
                    ('m1994_01.h5', 'm1994_02.h5', 'm1994_03.h5')]
        print(os.listdir('test_files'))

        assert all([os.path.exists(x) for x in expected])

    def test_getitem(self):
        result = self.handler['1994_01']
        expected = self.handler.stores['m1994_01']
        assert result is expected

        result = self.handler['m1994_01']
        assert result is expected

    def test_write(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        self.handler.write(df, 'm1994_01', format='f', append=False)
        res = self.handler.stores['m1994_01'].select('m1994_01')
        tm.assert_frame_equal(df, res)

    def tearDown(self):
        for f in os.listdir(os.path.join('test_files', 'panel')):
            file_path = os.path.join(self.fdir, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        os.rmdir(os.path.join('test_files', 'panel'))
        os.rmdir('test_files')
