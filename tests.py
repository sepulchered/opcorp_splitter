import unittest
import functools
import os
from unittest import mock


from split2files import OpcorpSplitter


class TestSplit2Files(unittest.TestCase):
    def test_sets_cli_args(self):
        splitter = OpcorpSplitter(['test_sample.xml', '--output', 'output', '-v', '2'])
        self.assertEqual(splitter.in_file, 'test_sample.xml')
        self.assertEqual(splitter.output, 'output')
        self.assertEqual(splitter.verbosity, 2)

    def test_output_not_required(self):
        splitter = OpcorpSplitter(['test_sample.xml'])
        self.assertEqual(splitter.in_file, 'test_sample.xml')
        self.assertEqual(splitter.output, 'v.0.11.3709973')

    def test_verbose_not_required(self):
        splitter = OpcorpSplitter(['test_sample.xml'])
        self.assertEqual(splitter.in_file, 'test_sample.xml')
        self.assertEqual(splitter.output, 'v.0.11.3709973')
        self.assertEqual(splitter.verbosity, 1)

    def test_ask_overwrite(self):
        def mock_input(retval, message):
            return retval

        input_default = functools.partial(mock_input, '')
        input_n = functools.partial(mock_input, 'n')
        input_y = functools.partial(mock_input, 'y')

        splitter = OpcorpSplitter(['test_sample.xml', '--output', 'output'])
        self.assertFalse(splitter._ask_for_overwrite(input=input_default))
        self.assertFalse(splitter._ask_for_overwrite(input=input_n))
        self.assertTrue(splitter._ask_for_overwrite(input=input_y))
        splitter = OpcorpSplitter(['test_sample.xml', '--output', 'output', '-v', '0'])
        self.assertTrue(splitter._ask_for_overwrite(input=input_default))
        self.assertTrue(splitter._ask_for_overwrite(input=input_n))
        self.assertTrue(splitter._ask_for_overwrite(input=input_y))

    def test_ask_overwrite_in_process_if_output_exists(self):
        if not os.path.exists('output'):
            os.mkdir('output')
        splitter = OpcorpSplitter(['test_sample.xml', '--output', 'output'])
        with mock._patch_object(splitter, '_ask_for_overwrite', return_value=True) as mock_method:
            splitter.process()
        self.assertTrue(mock_method.called)

        os.rmdir('output')
        with mock._patch_object(splitter, '_ask_for_overwrite', return_value=True) as mock_method:
            splitter.process()
        self.assertFalse(mock_method.called)

    def test_init_calls_get_out_path(self):
        with mock._patch_object(OpcorpSplitter, '_get_out_path', return_value='v.0.11.3709973') as mock_method:
            splitter = OpcorpSplitter(['test_sample.xml'])
        self.assertTrue(mock_method.called)

        with mock._patch_object(OpcorpSplitter, '_get_out_path', return_value='v.0.11.3709973') as mock_method:
            splitter = OpcorpSplitter(['test_sample.xml', '-o', 'output'])
        self.assertFalse(mock_method.called)

    def test_get_out_path(self):
        splitter = OpcorpSplitter(['test_sample.xml'])
        self.assertEqual(splitter._get_out_path(), 'v.0.11.3709973')
        splitter = OpcorpSplitter(['test_sample.xml', '-o', 'output'])
        self.assertEqual(splitter._get_out_path(), 'v.0.11.3709973')


