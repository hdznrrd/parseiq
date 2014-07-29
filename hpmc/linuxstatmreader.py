# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""\
Measure process memory consumption using Linux' /proc/<pid>/statm


/proc/[pid]/statm
              Provides information about memory usage, measured in pages.
              The columns are:

                  size       (1) total program size
                             (same as VmSize in /proc/[pid]/status)
                  resident   (2) resident set size
                             (same as VmRSS in /proc/[pid]/status)
                  share      (3) shared pages (i.e., backed by a file)
                  text       (4) text (code)
                  lib        (5) library (unused in Linux 2.6)
                  data       (6) data + stack
                  dt         (7) dirty pages (unused in Linux 2.6)
"""


import os

class LinuxStatmReader(object):
    keys = ['size', 'resident', 'share', 'text', 'lib', 'data', 'dt']

    def __init__(self, pid = None):
        self.pid = pid
        if not self.pid:
            self.pid = os.getpid()

    def readstatm(self):
        """Read data from /proc/<pid>/statm and return it as string"""
        lines = []
        with open('/proc/{}/statm'.format(pid), 'r') as statm:
            lines = statm.readlines()
        return lines[0]
        
    def get(self):
        """Returns memory information as a dictionary with fields
        corresponding with Linux' statm interface"""
        values = [int(x) for x in self.readstatm().split(" ")]
        return dict(zip(LinuxStatmReader.keys, values))

if __name__ == '__main__':
    import unittest as ut
    from mock import Mock

    lsr = LinuxStatmReader
    
    class ALinuxStatmReaderInitilizesPIDWithTheCurrentPIDByDefault(ut.TestCase):
        def runTest(self):
            assert lsr().pid == os.getpid()

    class ALinuxStatmReaderInitilizesPIDWithThePIDProvided(ut.TestCase):
        def runTest(self):
            assert lsr(123).pid == 123
    
    class MockedLSR(ut.TestCase):
        def setUp(self):
            self.mylsr = lsr()
            self.mylsr.readstatm = Mock(return_value="1 2 3 4 5 6 7")

    class ALinuxStatmReaderParsesValuePosition1ToSize(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['size'] == 1

    class ALinuxStatmReaderParsesValuePosition2ToResident(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['resident'] == 2

    class ALinuxStatmReaderParsesValuePosition3ToShare(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['share'] == 3

    class ALinuxStatmReaderParsesValuePosition4ToText(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['text'] == 4

    class ALinuxStatmReaderParsesValuePosition5ToLib(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['lib'] == 5

    class ALinuxStatmReaderParsesValuePosition6ToData(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['data'] == 6

    class ALinuxStatmReaderParsesValuePosition7ToDt(MockedLSR):
        def runTest(self):
            res = self.mylsr.get()
            self.mylsr.readstatm.assert_called()
            assert res['dt'] == 7

    ut.main()
