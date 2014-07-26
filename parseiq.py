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
import math

# https://github.com/docopt/docopt
from docopt import docopt

def read_n_iq_frames(wav_file, n=None, offset=None):
    if n == None:
        n = wav_file.getnframes()

    if offset != None:
        wav_file.setpos(offset)

    data = np.array( struct.unpack( '<{n}h'.format( n=n*wav_file.getnchannels() ), wav_file.readframes(n) ) )
    return data[0:][::2] + 1j*data[1:][::2]

def correlate(a,b):
    ml = min(len(a),len(b))
    
    a_std = np.std(a[0:ml]) 
    b_std = np.std(b[0:ml]) 
    
    a_mean = np.mean(a[0:ml])
    b_mean = np.mean(b[0:ml])
    
    ab_sum = np.sum(np.multiply(a[0:ml],b[0:ml].conjugate()))
    
    corr = (ab_sum - ml*a_mean*b_mean.conjugate())/((ml-1)*a_std*b_std)
    
    return corr

#def do_fft(data,frate):
#    w = np.fft.fft(data)
#    freqs = np.fft.fftfreq(len(w))
#
#    # Find the peak in the coefficients
#    idx=np.argmax(np.abs(w)**2)
#    freq=freqs[idx]
#    freq_in_hertz=abs(freq*frate)
#    return (freqs.min(),freqs.max(),freq_in_hertz,math.sqrt(np.sum(np.abs(w)**2))/len(w))


def output_dump(wav_file, n=None, offset=None):
    if n==None:
        n = wav_file.getnframes()

    if offset==None:
        offset = 0

    iq = read_n_iq_frames(wav_file, n, offset)

    for i in range(len(iq)):
        print '{iq}'.format(iq=iq[i])

def correlation_index(haystack, needle):
    ci = []
    
    length = max(0,len(haystack)-len(needle))
    for i in range(1+max(0,length)):
        if i%500 == 0:
            perc = (100.0/length)*i
            print str(i) + "/" + str(len(haystack)) + " (" + str(perc) + ")"
        ci.append( correlate(haystack[i:len(needle)],needle) )
    
    return ci

def output_correlation_find(haystack, needle, peak_threshold, haystack_n=None, haystack_offset=None):
    if not haystack_n:
        haystack_n = haystack.getnframes()

    if not haystack_offset:
        haystack_offset = 0

    print "loading pattern..."
    needle_iq = read_n_iq_frames(needle)
    print "loading haystack..."
    hay_iq = read_n_iq_frames(haystack, haystack_n, haystack_offset)

    print "correlating..."
    ci = correlation_index(hay_iq, needle_iq)

    print "peak extraction..."
    peaks = np.where(ci > peak_threshold)[0]

    print "done"
    print peaks + haystack_offset;
    print ci[peaks]

if __name__=='__main__':
    arguments = docopt(__doc__)

    block_size = int(arguments['-b'])
    skip_frames = int(arguments['-s'])
    offset_frames = int(arguments['-o'])

    #if arguments['peaksearch']:
    #    output_analysis(wav_file)

    if arguments['dump']:
        output_dump(wave.open(arguments['FILE'],'r'), int(arguments['-f']), int(arguments['-o']))

    if arguments['search']:
        output_correlation_find( wave.open(arguments['FILE'],'r'), wave.open(arguments['PATTERN_FILE'],'r'), float(arguments['-t']))

