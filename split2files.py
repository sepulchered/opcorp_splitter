import os
import argparse

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


class OpcorpSplitter():
    def __init__(self, args=None):  # args is for testing cli interface, patching sys.argv is tricky
        self._process_cli_args(args)

    def _process_cli_args(self, args):
        parser = argparse.ArgumentParser(description='Split opencorpora single file into text files')
        parser.add_argument('in_file', metavar='CORPUS_FILE', help='path to opencorpora xml file')
        parser.add_argument('-o', '--output', help='path to extract files to default path will be in current '
                                                   'dir based on annotation revision')
        parser.add_argument('-v', '--verbosity', help='show more/less output; default = 1', type=int, choices=[0, 1, 2], default=1)
        if args is not None:
            parser.parse_args(args, namespace=self)
        else:
            parser.parse_args(namespace=self)

    def _ask_for_overwrite(self, input=input):  # input set for tests
        if not self.verbosity:  # silently overwrite if verbosity set to 0
            return True

        answer = None
        while answer not in ['', 'y', 'n']:
            answer = input('Output folder {} already exists. Overwrite it? {[n],y}')

        if not answer or answer == 'n':
            print('Try with -o/--output option to set proper output path')
            return False
        else:
            return True

    def process(self):
        if os.path.exists(self.output):
            overwrite = self._ask_for_overwrite()

if __name__ == "__main__":
    splitter = OpcorpSplitter()
    splitter.process()
