from piq import Piq
import unittest as ut
from mock import Mock, patch
import wave
import tempfile
import math
import struct
import numpy as np

def populatewavfile(wav):
    """Generates 16 bit stereo file with 440 Hz on left and 730 Hz
    on the right channel with a sampling rate of 44.1 kHz"""
    nframes = 1000
    frate = 44100.0
    amp = 64000.0
    wav.setparams((2, 2, frate, nframes, 'NONE', 'no compressed'))

    data = zip([int(math.sin(2 * math.pi * 440 * (x / frate))*amp/2)
                for x in range(nframes)],
                [int(math.sin(2 * math.pi * 730 * (x / frate))*amp/2)
                for x in range(nframes)])

    for v in data:
        wav.writeframes(struct.pack('<2h', v[0], v[1]))

    wav.close()

class PiqFixture(ut.TestCase):
    """Test fixture containing two actual wave files"""
    def setUp(self):
        self.piq = Piq({})
        #self.haystack_tmp = tempfile.NamedTemporaryFile()
        #self.needle_tmp = tempfile.NamedTemporaryFile()

        #for name in [self.haystack_tmp.name, self.needle_tmp.name]:
        #    wavfile = wave.open(name, 'wb')
        #    populatewavfile(wavfile)
        #    wavfile.close()

        #self.piq.haystack['fh'] = wave.open(self.haystack_tmp.name, 'rb')
        #self.piq.needle['fh'] = wave.open(self.needle_tmp.name, 'rb')

        mocka = Mock()
        mockb = Mock()

        mocka.getframerate.return_value = 44100
        mocka.getnchannels.return_value = 2
        mocka.getsampwidth.return_value = 2
        mocka.getcomptype.return_value = 'NONE'

        mockb.getframerate.return_value = 44100
        mockb.getnchannels.return_value = 2
        mockb.getsampwidth.return_value = 2
        mockb.getcomptype.return_value = 'NONE'

        self.piq.haystack['fh'] = mocka
        self.piq.needle['fh'] = mockb

    def tearDown(self):
        pass
        #self.piq.haystack['fh'].close()
        #self.piq.needle['fh'].close()
        #del self.haystack_tmp
        #del self.needle_tmp

#class PiqMockedWavFixture(ut.TestCase):
#    """Test fixture containing two mocked WAV files"""
#    def setUp(self):
#        self.piq = Piq({})
#        self.haystack['fh'] = patch(wave.Wave_read)
#        self.needle['fh'] = patch(wave.Wave_read)

class VerifiesFilesIntegrityWithActualFiles(PiqFixture):
    def runTest(self):
        self.piq.verifyfileformat(self.piq.haystack['fh'],
                                  self.piq.needle['fh'])
        

class RequiresStereoFile(PiqFixture):
    def runTest(self):
        self.piq.haystack['fh'].getnchannels.return_value = 1
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getnchannels.assert_called_with()

class Requires16BitFile(PiqFixture):
    def runTest(self):
        self.piq.haystack['fh'].getsampwidth.return_value = 1
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getsampwidth.assert_called_with()

class RequiresUncompressedFile(PiqFixture):
    def runTest(self):
        self.piq.haystack['fh'].getcomptype.return_value = 'LZW'
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getcomptype.assert_called_with()

class RequiresMatchingFramerate(PiqFixture):
    def runTest(self):
        self.piq.haystack['fh'].getframerate.return_value = 23
        self.piq.needle['fh'].getframerate.return_value = 42
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'],
                          self.piq.needle['fh'])
        self.piq.haystack['fh'].getframerate.assert_called_with()
        self.piq.needle['fh'].getframerate.assert_called_with()
 
if __name__ == '__main__':
    ut.main()
