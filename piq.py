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

    def run(self):
        """Entry point of the application"""
        if self.arguments['dump']:
            self.do_dump()
        elif self.arguments['find']:
            self.do_find()


if __name__ == '__main__':
    Piq(docopt(__doc__)).run()
