# coding=utf-8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""Usage:   parseiq.py dump [-o OFFSET] [-f FRAMES] FILE
            parseiq.py peaksearch [-b BLOCKSIZE] [-s SKIPFRAMES] [-f FRAMES] FILE
            parseiq.py search [-t THRESHOLD] FILE PATTERN_FILE

Arguments:
    FILE            input file (WAV, IQ data))
    PATTERN_FILE    input file used as search pattern (WAV, IQ data)

Options:
    -h --help       show this help message and exit
    -b BLOCKSIZE    blocksize for FFT [default: 1024]
    -s SKIPFRAMES   number of frames to skip between exacting FFT blocks [default: 1]
    -o OFFSET       number of frames from the beginning of the file to skip [default: 0]
    -f FRAMES       limit search to at most this number of frames
    -t THRESHOLD    correlation threshold. between -1 and +1 [default: 0.5]
"""

# https://docs.python.org/2/library/wave.html
import wave

# http://stackoverflow.com/questions/3694918/how-to-extract-frequency-associated-with-fft-values-in-python
# https://docs.python.org/2/library/struct.html
import struct
import numpy as np

from multiprocessing import Process, Queue

# https://github.com/docopt/docopt
from docopt import docopt

def read_n_iq_frames(wav_file, n_frames=None, offset=None):
    """Reads n_frames or all frame starting from offset and
    returns an numpy array of complex numbers"""
    if n_frames == None:
        n_frames = wav_file.getnframes()

    if offset is not None:
        wav_file.setpos(offset)

    n_frames = min(n_frames, wav_file.getnframes()-offset)

    data = np.array(struct.unpack(
                    '<{n}h'.format(n=n_frames*wav_file.getnchannels()),
                    wav_file.readframes(n_frames)))
    return data[0:][::2] + 1j*data[1:][::2]

def correlate(first, second):
    """Calculates correlation between (complex) arrays a and b"""
    min_length = min(len(first), len(second))

    first_std = np.std(first[0:min_length]) 
    second_std = np.std(second[0:min_length]) 

    first_mean = np.mean(first[0:min_length])
    second_mean = np.mean(second[0:min_length])

    firstsecond_sum = np.sum(np.multiply(first[0:min_length], second[0:min_length].conjugate()))

    numerator = firstsecond_sum - min_length*first_mean*second_mean.conjugate()
    denominator = (min_length-1)*first_std*second_std
    corr = numerator/denominator
    return corr

#def do_fft(data,frate):
#    w = np.fft.fft(data)
#    freqs = np.fft.fftfreq(len(w))
#
#    # Find the peak in the coefficients
#    idx=np.argmax(np.abs(w)**2)
#    freq=freqs[idx]
#    freq_in_hertz=abs(freq*frate)
#    return (freqs.min(), freqs.max(), freq_in_hertz
#           , math.sqrt(np.sum(np.abs(w)**2))/len(w))


def output_dump(wav_file, n_frames=None, offset=None):
    """Dumps the provided wave file as text formatted complex numbers"""
    if not n_frames:
        n_frames = wav_file.getnframes()

    if not offset:
        offset = 0

    iq_data = read_n_iq_frames(wav_file, n_frames, offset)

    for i in range(len(iq_data)):
        print '{iq}'.format(iq=iq_data[i])


def worker(haystack, needle, work_queue, done_queue):
    """Worker thread funktion to calculate correlation"""
    for task in iter(work_queue.get, 'STOP'):
        correlation_values = []
        for i in task:
            correlation_values.append(correlate(haystack[i:len(needle)]
                                                , needle))
        done_queue.put([task, correlation_values])


def correlation_index(haystack, needle):
    """Calculate correlation for all offsets of needle inside haystack"""
    workers = 5
    workload_size = 1000000
    work_queue = Queue()
    done_queue = Queue()
    processes = []

    length = 1+max(0, len(haystack)-len(needle))

    print "generating tasks"
    for i in range(0, length, workload_size):
        work_queue.put(range(i, max(length, i+workload_size)))

    print "generated " + str(work_queue.qsize()) + " jobs"
    print "setting up workers"
    for w in xrange(workers):
        process = Process(target=worker
                          , args=(haystack, needle, work_queue, done_queue))
        process.start()
        processes.append(process)
        work_queue.put('STOP')

    print "crunching..."
    for process in processes:
        process.join()

    done_queue.put('STOP')

    print "consolidating..."
    correlation_values = []
    for result in sorted(iter(done_queue.get, 'STOP')):
        correlation_values += result[1]

    print "done"
    return correlation_values

def output_correlation_find(haystack, needle, peak_threshold
                            , haystack_n=None, haystack_offset=None):
    """Calculates correlation of needle with every possible
    offset in haystack and reports location of all values that have
    higher correlation than peak_threshold"""
    if not haystack_n:
        haystack_n = haystack.getnframes()

    if not haystack_offset:
        haystack_offset = 0

    print "loading pattern..."
    needle_iq = read_n_iq_frames(needle)
    print "loading haystack..."
    hay_iq = read_n_iq_frames(haystack, haystack_n, haystack_offset)

    print "correlating..."
    correlation_values = correlation_index(hay_iq, needle_iq)

    print "peak extraction..."
    peak_idxs = np.where(correlation_values > peak_threshold)[0]

    print "done"
    print peak_idxs + haystack_offset
    print correlation_values[peak_idxs]

def main():
    """entry point"""
    arguments = docopt(__doc__)

    #block_size = int(arguments['-b'])
    #skip_frames = int(arguments['-s'])
    #offset_frames = int(arguments['-o'])

    #if arguments['peaksearch']:
    #    output_analysis(wav_file)

    if arguments['dump']:
        output_dump(wave.open(arguments['FILE'], 'r')
                    , int(arguments['-f'])
                    , int(arguments['-o']))

    if arguments['search']:
        output_correlation_find(wave.open(arguments['FILE'], 'r')
                                , wave.open(arguments['PATTERN_FILE'], 'r')
                                , float(arguments['-t']))

if __name__ == '__main__':
    main()
