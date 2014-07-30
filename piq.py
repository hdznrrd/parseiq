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
        self.haystack = {}
        self.needle = {}

    def do_dump(self):
        """Dump a file to stdout"""
        pass

    def do_find(self):
        """Find a pattern within another file"""
        pass

    def readiq(self, wavfile, offset, length):
        pass

    def verifyfileformat(self, wavfile_a, wavfile_b=None):
        """Verify file format of input files to be valid and consistent"""
        if wavfile_b:
            # First test the second paramter as if we just had one
            self.verifyfileformat(wavfile_b)
            # make sure we have matching frame rates if there's two parameters
            if wavfile_a.getframerate() != wavfile_b.getframerate():
                raise TypeError('Input filenames must have matching framerates')

        # Tests that apply to all input files individually
        if wavfile_a.getchannels() != 2:
            raise TypeError('Input file must be stereo')
        if wavfile_a.getsamplewidth() != 2:
            raise TypeError('Input file must be 16 bit')
        if wavfile_a.getcomptype() != 'NONE':
            raise TypeError('Input file must not be compressed')

    def populatefilemetadata(self, metastore):
        """Populate a given input files dict with some usefull meta data"""
        metastore['framerate'] = metastore['fh'].getframerate()
        metastore['nframes'] = metastore['fh'].getnframes()

    def dispatch(self):
        """Dispatcher for the command interface"""
        if self.arguments['dump']:
            try:
                self.haystack['fh'] = wave.open(self.arguments['FILE'], 'rb')
                self.verifyfileformat(self.haystack['fh'])
                self.populatefilemetadata(self.haystack)
                self.do_dump()
            finally:
                if self.haystack['fh']:
                    self.haystack['fh'].close()

        elif self.arguments['find']:
            try:
                self.needle['fh'] = wave.open(self.arguments['PATTERN'], 'rb')
                self.haystack['fh'] = wave.open(self.arguments['FILE'], 'rb')
                self.verifyfileformat(self.haystack['fh'], self.needle['fh'])
                self.populatefilemetadata(self.haystack)
                self.populatefilemetadata(self.needle)
                self.do_find()
            finally:
                if self.needle['fh']:
                    self.needle['fh'].close()
                if self.haystack['fh']:
                    self.haystack['fh'].close()

    def run(self):
        """Entry point of the application"""
        try:
            self.dispatch()
        except:
            pass

if __name__ == '__main__':
    Piq(docopt(__doc__)).run()
