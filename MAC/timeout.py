import random
from threading import Timer

from .backoff import MILDBackoffCounter

class TimerRunningError(Exception):
    def __init__(self):
        super().__init__("Timer is still running!")

class MACAWTimeout:
    def __init__(self, slotTime, backoff: MILDBackoffCounter, handler):
        self._slotTime = slotTime
        self._backoff  = backoff
        self._handler  = handler

        self._timer = None

        self._contentionStepCount = 20
        self._contentionWindow = self._slotTime

        self._contentionStepLen = self._contentionWindow / self._contentionStepCount

    def _handler_wrapper(self):
        self._timer = None
        self._handler()

    def isRunning(self):
        return self._timer is not None

    def start_contend(self):
        if self.isRunning(): raise TimerRunningError()

        # Use quarter of slot time
        intervalStep = random.randrange(0,self._contentionStepCount)
        interval = self._contentionStepLen * intervalStep

        self._timer = Timer(interval, self._handler_wrapper)
        self._timer.start()

    def start_slot(self, slots):
        if self.isRunning(): raise TimerRunningError()

        self._timer = Timer(slots * self._slotTime, self._handler_wrapper)
        self._timer.start()

    def start_wait(self):
        self.start_slot(2)

    def start_backoff(self):
        # Random slot count
        slots = self._backoff.random()
        self.start_slot(slots)

    def reset(self):
        if self.isRunning():
            self._timer.cancel()
            self._timer = None
