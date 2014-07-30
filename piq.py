"""\
Usage:  piq.py dump [-o OFFSET] [-f FRAMES] FILE
        piq.py findreftick  [-o OFFSET] [-f FRAMES] FILE
        piq.py findpattern [-o OFFSET] [-f FRAMES] PATTERN FILE

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
import struct
import numpy as np

class Piq(object):
    """Application class for piq"""
    def __init__(self, arguments):
        self.arguments = arguments
        self.haystack = {}
        self.needle = {}

    def do_dump(self):
        """Dump a file to stdout"""
        pass

    def do_findpattern(self):
        """Find a pattern within another file"""
        pass

    def do_findireftick(self):
        """Find occurences of reference timer ticks"""
        pass

    def readiq(self, metastore, offset, length):
        wav = metastore['fh']
        wav.setpos(offset)
        length = max(0, min(wav.getnframes() - offset, length))
        data = wav.readnframes(length)
        if len(data) > 0:
            data = np.array(struct.unpack(
                            '<{}h'.format(length*wav.getnchannels()),
                            wav.readnframes(length)),
                            dtype=np.complex64)
        else:
            data =np.array([], dtype=np.complex64)

        result = data[0::2] + 1j * data[1::2]

        return result

    def verifyfileformat(self, wavfile_a, wavfile_b=None):
        """Verify file format of input files to be valid and consistent"""
        if wavfile_b:
            # make sure we have matching frame rates if there's two parameters
            if wavfile_a.getframerate() != wavfile_b.getframerate():
                raise TypeError('Input filenames must have matching framerates')
            # First test the second paramter as if we just had one
            self.verifyfileformat(wavfile_b)

        # Tests that apply to all input files individually
        if wavfile_a.getnchannels() != 2:
            raise TypeError('Input file must be stereo')
        if wavfile_a.getsampwidth() != 2:
            raise TypeError('Input file must be 16 bit')
        if wavfile_a.getcomptype() != 'NONE':
            raise TypeError('Input file must not be compressed')

    def dispatch(self):
        """Dispatcher for the command interface"""
        if self.arguments['dump']:
            try:
                self.haystack['fh'] = wave.open(self.arguments['FILE'], 'rb')
                self.verifyfileformat(self.haystack['fh'])
                self.do_dump()
            finally:
                if self.haystack['fh']:
                    self.haystack['fh'].close()
        elif self.arguments['findreftick']:
            try:
                self.haystack['fh'] = wave.open(self.arguments['FILE'], 'rb')
                self.verifyfileformat(self.haystack['fh'])
                self.do_findreftick()
            finally:
                if self.haystack['fh']:
                    self.haystack['fh'].close()
        elif self.arguments['findpattern']:
            try:
                self.needle['fh'] = wave.open(self.arguments['PATTERN'], 'rb')
                self.haystack['fh'] = wave.open(self.arguments['FILE'], 'rb')
                self.verifyfileformat(self.haystack['fh'], self.needle['fh'])
                self.do_findpattern()
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
