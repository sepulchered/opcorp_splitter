import os
import sys
import json
import datetime
import argparse
import shutil
import xml.sax


class OpcorpContentHandler(xml.sax.ContentHandler):
    def __init__(self, out_path, encoding, out_format):
        super().__init__()
        self.out_path = out_path
        self.out_format = out_format
        self.encoding = encoding

        self.file = None
        self._txt = None
        self._txt_node = None
        self._paragraph = None
        self._sentence = None
        self._token = None
        self._variant = None

    def _new_file(self, fid):
        path = os.path.join(self.out_path, '{}.{}'.format(fid, self.out_format))
        if self.out_format == 'xml':
            file_modifier = 'wb'
        else:
            file_modifier = 'w'
        self.file = open(path, file_modifier)
        if self.out_format == 'xml':
            bang_u = '<?xml version="1.0" encoding="{}"?>'.format(self.encoding)
            self.file.write(bang_u.encode(self.encoding))

    def _gen_start_tag(self, name, attrs):
        attributes = ' '.join('{}="{}"'.format(k, v) for k, v in attrs.items())
        st_u = '<{} {}>'.format(name, attributes)
        return st_u.encode(self.encoding)

    def _gen_end_tag(self, name):
        st_u = '</{}>'.format(name)
        return st_u.encode(self.encoding)

    def _start_element_xml(self, name, attrs):
        if name == 'text':
            self.file.write(self._gen_start_tag(name, attrs))
        elif name != 'annotation':  # all tags that are in text
            self.file.write(self._gen_start_tag(name, attrs))
        else:  # annotation
            with open(os.path.join(self.out_path, 'annotation.json'), 'w') as annot:
                json.dump({k: v for k, v in attrs.items()}, annot)

    def _start_element_json(self, name, attrs):
        if name == 'text':
            self._txt = {
                'id': int(attrs.get('id')),
                'parent': int(attrs.get('parent', 0)),
                'name': attrs.get('name', ''),
                'tags': [],
                'paragraphs': []
            }
        elif name != 'annotation':  # all tags that are in text
            if name == 'tag':
                self._txt_node = 'tag'
            elif name == 'source':
                self._txt_node = 'source'
            elif name == 'paragraph':
                self._paragraph = {
                    'id': int(attrs.get('id', 0)),
                    'sentences': []
                }
            elif name == 'sentence':
                self._sentence = {
                    'id': int(attrs.get('id', 0)),
                    'source': '',
                    'tokens': []
                }
            elif name == 'token':
                self._token = {
                    'id': int(attrs.get('id', 0)),
                    'text': attrs.get('text', ''),
                    'variants': []
                }
            elif name == 'l':
                self._variant = {
                    'id': int(attrs.get('id', 0)),
                    't': attrs.get('t', ''),
                    'grammemes': []
                }
            elif name == 'g':
                if attrs.get('v'):
                    self._variant['grammemes'].append(attrs.get('v'))

        else:  # annotation
            with open(os.path.join(self.out_path, 'annotation.json'), 'w') as annot:
                json.dump({k: v for k, v in attrs.items()}, annot)

    def _end_element_json(self, name):
        if name == 'text':
            json.dump(self._txt, self.file)
            self.file.close()
            self._txt = None
        elif name == 'tag':
            self._txt_node = None
        elif name == 'source':
            self._txt_node = None
        elif name == 'paragraph':
            self._txt['paragraphs'].append(self._paragraph)
            self._paragraph = None
        elif name == 'sentence':
            self._paragraph['sentences'].append(self._sentence)
            self._sentence = None
        elif name == 'token':
            self._sentence['tokens'].append(self._token)
        elif name == 'l':
            self._token['variants'].append(self._variant)

    def _end_element_xml(self, name):
        if name != 'annotation':
            self.file.write(self._gen_end_tag(name))
        if name == 'text':
            self.file.close()

    def startElement(self, name, attrs):
        if name == 'text':
            fid = attrs.get('id')
            self._new_file(fid)

        if self.out_format == 'xml':
            self._start_element_xml(name, attrs)
        elif self.out_format == 'json':
            self._start_element_json(name, attrs)

    def endElement(self, name):
        if self.out_format == 'xml':
            self._end_element_xml(name)
        elif self.out_format == 'json':
            self._end_element_json(name)

    def characters(self, content):
        if content.strip():
            if self.out_format == 'xml':
                self.file.write(content.strip().encode(self.encoding))
            elif self.out_format == 'json':
                if self._txt_node == 'tag':
                    self._txt['tags'].append(content.strip())
                elif self._txt_node == 'source':
                    self._sentence['source'] = content.strip()



class OpcorpSplitter():
    def __init__(self):
        self._process_cli_args()

    def _process_cli_args(self):
        parser = argparse.ArgumentParser(description='Split opencorpora single '
                                                     'file into text files')
        parser.add_argument('in_file', metavar='CORPUS_FILE',
                            help='path to opencorpora xml file')
        parser.add_argument('output', metavar='OUTPUT_PATH',
                            help='path to extract files to')
        parser.add_argument('-v', '--verbosity',
                            help='show more/less output; default = 1',
                            type=int, choices=[0, 1, 2], default=1)
        parser.add_argument('-e', '--encoding', default='utf-8',
                            help='encoding of output files; defaults to utf-8')
        parser.add_argument('-t', '--time', action='store_true', default=False,
                            help='print execution time in the end')
        parser.add_argument('-f', '--format', default='xml', choices=['xml', 'json'],
                            help='output files format; default=xml')
        parser.parse_args(namespace=self)

    def _ask_for_overwrite(self):  # input set for tests
        if not self.verbosity:  # silently overwrite if verbosity set to 0
            return True

        answer = None
        while answer not in ['', 'y', 'n']:
            answer = input('Output folder {0} already exists. Overwrite it? '
                           '{{[n],y}}'.format(self.output))

        if answer in ['', 'n']:
            return False
        else:
            return True

    def process(self):
        # check if input file exists
        if not os.path.exists(self.in_file):
            print('Invalid input file provided')
            sys.exit(1)

        # check if output path exists
        if os.path.exists(self.output):
            overwrite = self._ask_for_overwrite()

            if not overwrite:
                sys.exit(0)
            else:
                shutil.rmtree(self.output)
                os.makedirs(self.output)
        else:
            os.makedirs(self.output)

        parser = xml.sax.parse(self.in_file, OpcorpContentHandler(self.output, self.encoding, self.format))

if __name__ == "__main__":
    start = datetime.datetime.now()
    splitter = OpcorpSplitter()
    splitter.process()
    if splitter.time:
        end = abs(start-datetime.datetime.now())
        print('executed in {0} sec'.format(end.total_seconds()))
