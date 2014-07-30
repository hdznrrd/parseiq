from piq import Piq
import unittest as ut
from mock import Mock
import struct

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

class PiqFixture(ut.TestCase):
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

class ReadiqHandlesZeroLengthData(PiqFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 0
        self.piq.needle['fh'].readnframes.return_value = ''

        data = self.piq.readiq(self.piq.needle, 0, 100)

        assert len(data) == 0
        self.piq.needle['fh'].readnframes.assert_called_with(0)
     
class ReadiqClips(PiqFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 1
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<2h', 23, 42)

        data = self.piq.readiq(self.piq.needle, 0, 100)

        assert len(data) == 1
        self.piq.needle['fh'].readnframes.assert_called_with(1)

class ReadiqReadsAllAvailableData(PiqFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 4
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<8h', 1, 2, 3, 4, 5, 6, 7, 8)

        data = self.piq.readiq(self.piq.needle, 0, 4)

        assert len(data) == 4
        self.piq.needle['fh'].readnframes.assert_called_with(4)

class ReadiqReadsLessThanAllAvailableData(PiqFixture):
    def runTest(self):
        self.piq.needle['fh'].getnframes.return_value = 100
        self.piq.needle['fh'].readnframes.return_value = struct.pack('<6h', 1, 2, 3, 4, 5, 6)

        data = self.piq.readiq(self.piq.needle, 0, 3)

        assert len(data) == 3
        self.piq.needle['fh'].readnframes.assert_called_with(3)


if __name__ == '__main__':
    ut.main()
