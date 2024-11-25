from elevator.elevator import Elevator
from elevator.people import People
from elevator.queues import Outlist, InternalQueue, ExternalQueue
import itertools as itr
import pprint as pp
import copy as cp


class QueueMethods:
    def __init__(self, queue: InternalQueue|ExternalQueue):
        self.queue = queue
        self.floorAmount = cp.copy(queue.floorAmount)
    
    def sumWaitingTime(self):
        waitingTime = 0
        for floor in range(self.floorAmount):
            for people in self.queue.queue[floor]:
                waitingTime += people.waitingTimer
        return waitingTime

    def sumJourneyTime(self):
        journeyTime = 0
        for floor in range(self.floorAmount):
            for people in self.queue.queue[floor]:
                journeyTime += people.journeyTime
        return journeyTime
            

class OutlistMethods:
    pass