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


def do_dump():
    pass

def do_find():
    pass


def main():
    """Entry point"""
    arguments = docopt(__doc__)


    if arguments['dump']:
        do_dump()

    if arguments['find']:
        do_find()

if __name__ == '__main__':
    main()
