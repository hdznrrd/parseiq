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
import math

class Piq(object):
    """Application class for piq"""
    def __init__(self, arguments):
        self.arguments = arguments
        self.haystack = {}
        self.needle = {}
        self.haystack['data'] = np.array([], dtype=np.complex64)
        self.haystack['offset'] = 0
        self.needle['data'] = np.array([], dtype=np.complex64)
        self.needle['offset'] = 0

    def advance(self, metastore, nframes):
        """Read up to nframes from the wave file associated
        with the provided metastore and use it to virtually
        shift the window into the file by the amount read"""
        data = self.readiq(metastore, metastore['offset'], nframes)
        elementsread = len(data)

        if elementsread > 0:
            metastore['offset'] += elementsread
            metastore['data'] = metastore['data'][np.s_[elementsread::]]
            metastore['data'] = np.concatenate((metastore['data'], data))

        return elementsread

    def do_dump(self):
        """Dump a file to stdout"""
        pass

    def do_findreftick(self):
        """Find the reference tick (pulse)"""

        print "trying to find all ticks in this file ..."

        """ known inputs """
        gap_length_sec = 0.1
        samplerate = 2048000
        gap_frames = 10

        gap_samples = gap_length_sec * samplerate
        samples_per_frame = int(math.ceil(gap_samples/gap_frames))

        haystack_reduced = []

        while(self.advance(self.haystack,samples_per_frame)):
            sum = 0
            for v in self.haystack['data']:
                 sum = sum + abs(v.real)
            haystack_reduced.append(sum/len(self.haystack['data']))
            """ length of the the returned haystack part is always the same, even for the last fraction"""

        needle_reduced = []
        needle_length = gap_frames-2

        for i in range(needle_length):
            needle_reduced.append(1)
        for i in range(needle_length):
            needle_reduced.append(0.2)

        data = self.do_findreftick_rough(haystack_reduced, needle_reduced)

        tick_period = 1024
        """millis"""
        tick_period_samples = samplerate*1000/tick_period
        tick_period_samples_reduced = tick_period_samples/samples_per_frame

        """ finding the exact starting point of the ticks """
        select_norm_cross_corr_best_index = self.findtickstart(data, gap_frames)

        """ next level of accuracy """
        print "starting to find exact start of falling edge of pulse(s)..."

        select_offset = []
        select_frames = []

        for v in xrange(len(select_norm_cross_corr_best_index)):
            select_offset.append((select_norm_cross_corr_best_index[v] - 2) * samples_per_frame)
            """ for uncertainty reasons the search will started one index before the detected index """
            select_frames.append((len(needle_reduced)+4)*samples_per_frame)
            """ a zone of 3 times the size of reduced_gap_length_samples around the detected index will be searched"""

        while samples_per_frame >= 2:
            select_offset_b4 = 0

            del needle_reduced[:]
            factor = 2.0

            corr_factor = (samples_per_frame/factor)/math.floor(samples_per_frame/factor)

            needle_length = int(needle_length * factor * corr_factor)
            samples_per_frame = samples_per_frame/int(factor)
            """ doubles needle length every step """

            for i in range(needle_length):
                needle_reduced.append(1.0)
            for i in range(needle_length):
                needle_reduced.append(0.2)

            print ""
            print "needle length =", len(needle_reduced), "samples per frame =", samples_per_frame
            print "samples =", len(needle_reduced)*samples_per_frame, "select samples", select_frames[0]
            print "gap# | start index | start offset | p2p samples | p2p seconds || [data below]"

            for d in xrange(len(select_norm_cross_corr_best_index)):
                del haystack_reduced[:]
                datax = self.readiq(self.haystack, select_offset[d], select_frames[d])
                sum = 0
                sample_counter = 0
                for v in datax:
                    sum = sum + abs(v.real)
                    sample_counter+=1
                    if sample_counter == samples_per_frame:
                        haystack_reduced.append(sum/samples_per_frame)
                        sample_counter = 0
                        sum = 0

                del data[:]
                data = self.do_findreftick_rough(haystack_reduced, needle_reduced)

                select_norm_cross_corr_best_index1 = self.findbest(data)

                if select_norm_cross_corr_best_index1 == 0:
                    print "<- start index should be further left"
                elif select_norm_cross_corr_best_index1 == len(haystack_reduced)-len(needle_reduced):
                    print "-> start index should be further right"
                else:
                    select_offset[d] = select_offset[d]+((select_norm_cross_corr_best_index1-2) * samples_per_frame)
                    select_frames[d] = ((len(needle_reduced)+4)*samples_per_frame)
                    print d,select_norm_cross_corr_best_index1,select_offset[d],(select_offset[d]-select_offset_b4),(select_offset[d]-select_offset_b4)*1.0/(1.0*samplerate)
                    select_offset_b4 = select_offset[d]

        print ""
        print "aaaaand it's gone!"


    def do_findpattern(self):
        """Find a pattern within another file"""
        pass

    def do_findreftick_rough(self,haystack, needle):
        """Find occurences of reference timer ticks"""
        out = []

        sum_numinator_needle = 0
        for i in range(len(needle)):
            sum_numinator_needle = sum_numinator_needle+(needle[i]**2)

        for sample in range(len(haystack)-len(needle)):
            sum_numinator_haystack = 0

            for i in range(len(needle)):
                sum_numinator_haystack = sum_numinator_haystack+(haystack[sample+i].real**2)

                norm_corr_numinator = (sum_numinator_haystack * sum_numinator_needle)**0.5

            norm_corr_denuminator = 0

            for i in range(len(needle)):
                norm_corr_denuminator = norm_corr_denuminator + (abs(haystack[sample+i].real) * needle[i])

            out.append(norm_corr_denuminator/norm_corr_numinator)

        return out

    def findtickstart(self, data, gap_frames):
        """ will try to find the ref tick start in the complete iq stream file """
        """ it will only accept data matches better than 0.9 (1.0 is best) """
        """ Further more it is assumed that the reftick will happen within about 1 second """

        select_norm_cross_corr_best_index = []
        norm_cross_corr_best = 0
        norm_cross_corr_best_b4 = 0
        norm_cross_corr_best_index = 0
        timer = 0
        timer_on = 0
        gap_counter = 0

        index_b4 = 0

        for h in xrange(len(data)):
            if data[h] >= 0.9:
                if data[h] >= norm_cross_corr_best:
                    norm_cross_corr_best = data[h]
                    norm_cross_corr_best_index = h
                timer_on = 1

            if timer_on == 1:
                timer += 1

            if timer == gap_frames:
                print "gap end ",gap_counter,(norm_cross_corr_best_index-index_b4),norm_cross_corr_best_index, norm_cross_corr_best
                index_b4 = norm_cross_corr_best_index

                norm_cross_corr_best = 0
                select_norm_cross_corr_best_index.append(norm_cross_corr_best_index)
                gap_counter += 1

                """ resetting timer """
                timer_on = 0
                timer = 0

            norm_cross_corr_best_b4 = norm_cross_corr_best

        print len(select_norm_cross_corr_best_index),norm_cross_corr_best_index, norm_cross_corr_best

        return select_norm_cross_corr_best_index

    def findbest(self,data):
        """ will only return the highest number in data """

        index_best = 0
        value_best = 0

        for v in xrange(len(data)):
            if value_best <= data[v]:
                index_best = v
                value_best = data[v]

        return index_best

    def readiq(self, metastore, offset, length):
        wav = metastore['fh']
        wav.setpos(offset)
        length = max(0, min(wav.getnframes() - offset, length))
        data = wav.readframes(length)
        if len(data) > 0:
            data = np.array(struct.unpack(
                            '<{}h'.format(length*wav.getnchannels()),
                            data),
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
        self.dispatch()

if __name__ == '__main__':
    Piq(docopt(__doc__)).run()
