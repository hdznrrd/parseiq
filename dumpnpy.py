"""\
Usage:  dumpnpy.py FILE

Arguments:
        FILE    NPY file to dump
"""

from docopt import docopt
import sys
import numpy as np

def main():
    """entry point"""
    args = docopt(__doc__)
    data = np.memmap(args['FILE'], dtype=np.complex64, mode='r')

    for v in np.nditer(data, flags=['external_loop', 'buffered'], op_flags=['readonly']):
        print v


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print 'ERROR: ' + e
