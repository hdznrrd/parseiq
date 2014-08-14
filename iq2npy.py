"""\
Usage: iq2npy.py [-v] INFILE [OUTFILE]

Arguments:
        INFILE      Input WAV file in 16 bit I/Q format
        OUTFILE     Name of output file in NPY format

Options:
        -v          verbose output
"""

from __future__ import print_function
from docopt import docopt
import sys
import wave
import struct
import numpy as np
import logging

def error(*objs):
    """print error message to stderr"""
    print("ERROR: ", *objs, file=sys.stderr)


def verifyfileformat(wavfile):
    """Verify input file format"""
    if wavfile.getnchannels() != 2:
        raise TypeError('Input file must be stereo')
    if wavfile.getsampwidth() != 2:
        raise TypeError('Input file must be 16 bit')
    if wavfile.getcomptype() != 'NONE':
        raise TypeError('Input file must not be compressed')

def convert(in_name, out_name):
    """convert the file identified by filename in_name to a complex numpy array and store it to a file named out_name"""
    wav = wave.open(in_name,'rb')
    verifyfileformat(wav)

    length = wav.getnframes()
    channels = wav.getnchannels()

    logging.info('length: {} frames, channels: {}'.format(length, channels))

    data = wav.readframes(length)
    data = np.array(struct.unpack('<{}h'.format(length*channels),
                                  data),
                    dtype=np.complex64)
    wav.close()
    npfile = np.memmap(out_name, dtype=np.complex64,
                       mode='w+', shape=(1, length))

    npfile[:] = data[0::2] + 1j * data[1::2]
    del npfile

def main():
    """entry point"""
    logger = logging.getLogger('')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logger.addHandler(console)

    try:
        args = docopt(__doc__)
        infile_name = args['INFILE']
        outfile_name = args['OUTFILE']

        if outfile_name == None:
            outfile_name = infile_name + '.npy'

        if args['-v']:
            logger.setLevel(logging.DEBUG)

        logging.info('input: "{}", output: "{}"'.format(infile_name,
                                                        outfile_name))

        convert(infile_name, outfile_name)

        logging.info("done")

    except Exception, e:
        logging.fatal(e)

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        error(e)
