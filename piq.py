"""\
Usage:  piq.py dump [-o OFFSET] [-f FRAMES] FILE
        piq.py find [-o OFFSET] [-f FRAMES] PATTERN FILE

Arguments:
        FILE        Input file in 16 bit I/Q format
        PATTERN     Pattern in 16 bit I/Q format to be searched in FILE

Options:
        -h --help   Show this help message and exit
        -o OFFSET   Number of frames to skip before processing [default: 0]
        -f FRAMES   Limit number of frames to process (at most)
"""

from docopt import docopt
import wave

class Piq(object):
    """Application class for piq"""
    def __init__(self, arguments):
        self.arguments = arguments

    def do_dump(self):
        """Dump a file to stdout"""
        pass

    def do_find(self):
        """Find a pattern within another file"""
        pass

    def dispatch(self):
        """Dispatcher for the command interface"""
        if self.arguments['dump']:
            try:
                self.haystack_file = wave.open(self.arguments['FILE'], 'rb')
                self.do_dump()
            finally:
                if self.haystack_file:
                    self.haystack_file.close()

        elif self.arguments['find']:
            try:
                self.needle_file = wave.open(self.arguments['PATTERN'], 'rb')
                self.haystack_file = wave.open(self.arguments['FILE'], 'rb')
                self.do_find()
            finally:
                if self.needle_file:
                    self.needle_file.close()
                if self.haystack_file:
                    self.haystack_file.close()

    def run(self):
        """Entry point of the application"""
        try:
            self.dispatch()
        except:
            pass

if __name__ == '__main__':
    Piq(docopt(__doc__)).run()
