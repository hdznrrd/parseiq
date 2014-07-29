"""\
Record memory usage points over time
"""

import time

class Recorder(object):
    """Records arbitrary x/y data.
    Optionally add a comment to each sample"""
    getmillis = lambda x: int(round(time.time() * 1000))
    incrementer = lambda x: x
    constantone = lambda x: 1

    def __init__(self, samplefunctionx=incrementer, samplefunctiony=constantone):
        self.samplefunctionx = samplefunctionx
        self.samplefunctiony = samplefunctiony
        self.data = []
        self.counter = 0

    def record(self, comment=None):
        """Record a new x/y sample and optionally add a commend"""
        self.data.append({'x': self.samplefunctionx(self.counter),
                          'y': self.samplefunctiony(self.counter),
                          'comment': comment})
        self.counter += 1

    def getrecordeddata(self):
        """Get all of the recorded data"""
        return self.data

    def reset(self):
        """Clear all recorded data"""
        self.data = []
        self.counter = 0



if __name__ == '__main__':
    import unittest as ut
    from mock import Mock

    class ARecorderInitializesDataToEmptyList(ut.TestCase):
        def runTest(self):
            assert Recorder().data == []

    class ARecorderInitializesCounterToZero(ut.TestCase):
        def runTest(self):
            assert Recorder().counter == 0

    class ARecorderAutoincrementsXByDefault(ut.TestCase):
        def runTest(self):
            rec = Recorder()
            rec.record()
            rec.record()
            assert rec.getrecordeddata()[0]['x'] == 0
            assert rec.getrecordeddata()[1]['x'] == 1

    class ARecorderStoresRecordsYConstantOneByDefault(ut.TestCase):
        def runTest(self):
            rec = Recorder()
            rec.record()
            rec.record()
            assert rec.getrecordeddata()[0]['y'] == 1
            assert rec.getrecordeddata()[1]['y'] == 1

    class ARecorderUsesProvidedXSampleFunction(ut.TestCase):
        def runTest(self):
            rec = Recorder(samplefunctionx = lambda x: 2*x)
            rec.record()
            rec.record()
            rec.record()
            assert rec.getrecordeddata()[0]['x'] == 0
            assert rec.getrecordeddata()[1]['x'] == 2
            assert rec.getrecordeddata()[2]['x'] == 4

    class ARecorderUsesProvidedYSampleFunction(ut.TestCase):
        def runTest(self):
            rec = Recorder(samplefunctiony = lambda x: 2*x)
            rec.record()
            rec.record()
            rec.record()
            assert rec.getrecordeddata()[0]['y'] == 0
            assert rec.getrecordeddata()[1]['y'] == 2
            assert rec.getrecordeddata()[2]['y'] == 4

    class ARecorderStoresProvidedComments(ut.TestCase):
        def runTest(self):
            rec = Recorder()
            rec.record("hello")
            rec.record()
            rec.record(123)
            assert rec.getrecordeddata()[0]['comment'] == "hello"
            assert rec.getrecordeddata()[1]['comment'] == None
            assert rec.getrecordeddata()[2]['comment'] == 123

    ut.main()




