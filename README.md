# opcorp_splitter
[OpenCorpora](http://opencorpora.org/) export xml file splitter
    usage: split2files.py [-h] [-v {0,1,2}] [-e ENCODING] [-t]
                          CORPUS_FILE OUTPUT_PATH

    Split opencorpora single file into text files

    positional arguments:
      CORPUS_FILE           path to opencorpora xml file
      OUTPUT_PATH           path to extract files to

    optional arguments:
      -h, --help            show this help message and exit
      -v {0,1,2}, --verbosity {0,1,2}
                            show more/less output; default = 1
      -e ENCODING, --encoding ENCODING
                            encoding of output files; defaults to utf-8
      -t, --time            print execution time in the end

