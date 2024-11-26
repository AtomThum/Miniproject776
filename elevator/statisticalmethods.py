import copy as cp
import itertools as itr
import pprint as pp

from elevator.elevator import Elevator
from elevator.people import People
from elevator.queues import ExternalQueue, InternalQueue, Outlist


class OutlistMethods:
    def __init__(self, outlist):
        self.outlist = outlist

    def sumWaitingTime(self):
        return sum(people.waitingTimer for people in self.outlist.outlist)

    def sumJourneyTime(self):
        return sum(people.journeyTimer for people in self.outlist.outlist)

    def sumElevatorBreakCount(self):
        return sum(people.elevatorBreakCount for people in self.outlist.outlist)

    def meanWaitingTime(self):
        try:
            return self.sumWaitingTime() / len(self.outlist.outlist)
        except ZeroDivisionError:
            return 0

    def meanJourneyTime(self):
        try:
            return self.sumJourneyTime() / len(self.outlist.outlist)
        except ZeroDivisionError:
            return 0

    def meanElevatorBreakCount(self):
        try:
            return self.sumElevatorBreakCount() / len(self.outlist.outlist)
        except ZeroDivisionError:
            return 0


class QueueMethods:
    pass
