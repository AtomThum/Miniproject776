from elevator.elevator import Elevator
from elevator.people import People
from elevator.queues import Outlist, InternalQueue, ExternalQueue
import itertools as itr
import pprint as pp
import copy as cp


class OutlistMethods:
    @staticmethod
    def sumWaitingTime(outlist: Outlist):
        return sum(people.waitingTimer for people in outlist.outlist)

    @staticmethod
    def sumJourneyTime(outlist: Outlist):
        return sum(people.journeyTimer for people in outlist.outlist)

    @staticmethod
    def sumElevatorBreakCount(outlist: Outlist):
        return sum(people.elevatorBreakCount for people in outlist.outlist)

    def meanWaitingTime(self, outlist: Outlist):
        return self.sumWaitingTime(outlist) / len(outlist.outlist)

    def meanJourneyTime(self, outlist: Outlist):
        return self.sumJourneyTime(outlist) / len(outlist.outlist)

    def meanElevatorBreakCount(self, outlist: Outlist):
        return self.sumElevatorBreakCount(outlist) / len(outlist.outlist)


class QueueMethods:
    pass
