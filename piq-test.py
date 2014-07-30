from piq import Piq
import unittest as ut
from mock import Mock
import struct
import numpy as np

#def populatewavfile(wav):
#    """Generates 16 bit stereo file with 440 Hz on left and 730 Hz
#    on the right channel with a sampling rate of 44.1 kHz"""
#    nframes = 1000
#    frate = 44100.0
#    amp = 64000.0
#    wav.setparams((2, 2, frate, nframes, 'NONE', 'no compressed'))
#
#    data = zip([int(math.sin(2 * math.pi * 440 * (x / frate))*amp/2)
#                for x in range(nframes)],
#                [int(math.sin(2 * math.pi * 730 * (x / frate))*amp/2)
#                for x in range(nframes)])
#
#    for v in data:
#        wav.writeframes(struct.pack('<2h', v[0], v[1]))
#
#    wav.close()

class MockWaveReaderFixture(ut.TestCase):
    """Test fixture containing two mocked wave files"""
    def setUp(self):
        self.piq = Piq({})

        self.piq.haystack['fh'] = Mock()
        self.piq.needle['fh'] = Mock()
        
        def setupmock(amock):
            amock.getframerate.return_value = 44100
            amock.getnchannels.return_value = 2
            amock.getsampwidth.return_value = 2
            amock.getcomptype.return_value = 'NONE'

        setupmock(self.piq.haystack['fh'])
        setupmock(self.piq.needle['fh'])

class MockReadiqFixture(ut.TestCase):
    """Test fixture containing two mocked wave files"""
    def setUp(self):
        self.piq = Piq({})
        self.piq.readiq = Mock()
        self.piq.readiq.return_value = np.array([], dtype=np.complex64)

class VerifiesFilesIntegrityWithActualFiles(MockWaveReaderFixture):
    def runTest(self):
        self.piq.verifyfileformat(self.piq.haystack['fh'],
                                  self.piq.needle['fh'])

class RequiresStereoFile(MockWaveReaderFixture):
    def runTest(self):
        self.piq.haystack['fh'].getnchannels.return_value = 1
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getnchannels.assert_called_with()

class Requires16BitFile(MockWaveReaderFixture):
    def runTest(self):
        self.piq.haystack['fh'].getsampwidth.return_value = 1
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getsampwidth.assert_called_with()

class RequiresUncompressedFile(MockWaveReaderFixture):
    def runTest(self):
        self.piq.haystack['fh'].getcomptype.return_value = 'LZW'
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'])
        self.piq.haystack['fh'].getcomptype.assert_called_with()

class RequiresMatchingFramerate(MockWaveReaderFixture):
    def runTest(self):
        self.piq.haystack['fh'].getframerate.return_value = 23
        self.piq.needle['fh'].getframerate.return_value = 42
        self.assertRaises(TypeError,
                          self.piq.verifyfileformat,
                          self.piq.haystack['fh'],
                          self.piq.needle['fh'])
        self.piq.haystack['fh'].getframerate.assert_called_with()
        self.piq.needle['fh'].getframerate.assert_called_with()

class ReadiqHandlesZeroLengthData(MockWaveReaderFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 0
        self.piq.needle['fh'].readnframes.return_value = ''

        data = self.piq.readiq(self.piq.needle, 0, 100)

        assert len(data) == 0
        self.piq.needle['fh'].readnframes.assert_called_with(0)
     
class ReadiqClips(MockWaveReaderFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 1
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<2h', 23, 42)

        data = self.piq.readiq(self.piq.needle, 0, 100)

        assert len(data) == 1
        self.piq.needle['fh'].readnframes.assert_called_with(1)

class ReadiqReadsAllAvailableData(MockWaveReaderFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 4
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<8h', 1, 2, 3, 4, 5, 6, 7, 8)

        data = self.piq.readiq(self.piq.needle, 0, 4)

        assert len(data) == 4
        self.piq.needle['fh'].readnframes.assert_called_with(4)

class ReadiqReadsLessThanAllAvailableData(MockWaveReaderFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 100
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<6h', 1, 2, 3, 4, 5, 6)

        data = self.piq.readiq(self.piq.needle, 0, 3)

        assert len(data) == 3
        self.piq.needle['fh'].readnframes.assert_called_with(3)

class HaystackBufferIsEmptyListOnCreation(ut.TestCase):
    def runTest(self):
        assert len(Piq({}).haystack['data']) == 0

class NeedleBufferIsEmptyListOnCreation(ut.TestCase):
    def runTest(self):
        assert len(Piq({}).needle['data']) == 0

class HaystackOffsetIsZeroOnCreation(ut.TestCase):
    def runTest(self):
        assert Piq({}).haystack['offset'] == 0

class NeedleOffsetIsZeroOnCreation(ut.TestCase):
    def runTest(self):
        assert Piq({}).needle['offset'] == 0

class AdvanceFillsInitialBuffer(MockReadiqFixture):
    def runTest(self):
        reference = np.array([0+0j, 1+1j, 2+2j, 3+3j],
                             dtype=np.complex64)
        self.piq.readiq.return_value = reference
        
        self.piq.advance(self.piq.haystack, 4)

        self.piq.readiq.assert_call_with(self.piq.haystack, 4)
        np.testing.assert_array_equal(self.piq.haystack['data'], reference)

class AdvanceIncrementsOffset(MockReadiqFixture):
    def runTest(self):
        reference = np.array([0+0j, 1+1j, 2+2j, 3+3j],
                             dtype=np.complex64)
        self.piq.readiq.return_value = reference
        
        self.piq.advance(self.piq.haystack, 4)

        self.piq.readiq.assert_call_with(self.piq.haystack, 4)
        assert self.piq.haystack['offset'] == 4

class PiqStoresPassedArgumentsDict(ut.TestCase):
    def runTest(self):
        reference = {'a':42, 'b':23}
        self.assertDictEqual(Piq(reference).arguments, reference)

class AdvanceDeletesAsManyItemsAsItFetches(MockReadiqFixture):
    pass

if __name__ == '__main__':
    ut.main()
