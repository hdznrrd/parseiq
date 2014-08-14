"""\
Usage:  piq.py dump [-o OFFSET] [-f FRAMES] FILE
        piq.py findreftick  [-o OFFSET] [-f FRAMES] FILE
        piq.py findpattern [-o OFFSET] [-f FRAMES] PATTERN FILE

Arguments:
        FILE        Input file in complex64 NPY format
        PATTERN     Pattern in complex64 NPY format to be searched in FILE

Options:
        -h --help   Show this help message and exit
        -o OFFSET   Number of frames to skip before processing [default: 0]
        -f FRAMES   Limit number of frames to process (at most)
"""

from docopt import docopt
import wave
import struct
import numpy as np

class Piq(object):
    """Application class for piq"""
    def __init__(self, arguments):
        self.arguments = arguments
        self.haystack = {}
        self.needle = {}
        self.haystack['data'] = None
        self.haystack['offset'] = 0
        self.needle['data'] = None
        self.needle['offset'] = 0

    def do_dump(self):
        """Dump a file to stdout"""
        for v in self.haystack['data']:
            print v

    def do_findpattern(self):
        """Find a pattern within another file"""
        pass

    def do_findreftick(self):
        """Find occurences of reference timer ticks"""
        pass

    def dispatch(self):
        """Dispatcher for the command interface"""
        if self.arguments['dump']:
            self.haystack['data'] = np.memmap(self.arguments['FILE'], mode='r', dtype=np.complex64)
            self.do_dump()
        elif self.arguments['findreftick']:
            self.haystack['data'] = np.memmap(self.arguments['FILE'], mode='r', dtype=np.complex64)
            self.do_findreftick()
        elif self.arguments['findpattern']:
            self.needle['data'] = np.memmap(self.arguments['PATTERN'], mode='r', dtype=np.complex64)
            self.haystack['data'] = np.memmap(self.arguments['FILE'], mode='r', dtype=np.complex64)
            self.do_findpattern()

    def run(self):
        """Entry point of the application"""
        self.dispatch()

if __name__ == '__main__':
    Piq(docopt(__doc__)).run()
