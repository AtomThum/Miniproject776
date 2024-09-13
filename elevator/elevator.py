from elevator.people import People
from elevator.queues import Outlist, InternalQueue, ExternalQueue


# Initializing the Elevator class
class Elevator:
    def __init__(
        self,
        currentDirection: bool,
        currentFloor: int,
        lowestFloor: int,
        highestFloor: int,
        carryingCapacity: int,
        bufferCutoff: float,
        internalQueue: InternalQueue,
        externalQueueUp: ExternalQueue,
        externalQueueDown: ExternalQueue,
        outlist: Outlist,
        progression: float = 0,
        activeSpeed: float = 5,
        bufferSpeed: float = 1,
        timePerStep: float = 1
    ):
        # Properties of elevator
        self.currentDirection = (
            currentDirection  # True when going up, false when going down
        )
        self.currentFloor = currentFloor
        self.lowestFloor = lowestFloor
        self.highestFloor = highestFloor
        self.carryingCapacity = carryingCapacity
        self.progression = (
            # In the range 0 - 100 (If enters new floor, progression = 0)
            progression
        )
        self.activeSpeed = activeSpeed
        self.bufferSpeed = bufferSpeed
        self.bufferCutoff = bufferCutoff  # In the range 0 - 100
        self.timePerStep = timePerStep
        # Queues
        self.internalQueue = internalQueue
        self.externalQueueUp = externalQueueUp
        self.externalQueueDown = externalQueueDown
        self.outlist = outlist
    
    # Adding people to external queue
    def addToExternalQueue(self, *args: People):
        peopleUp, peopleDown = [], []
        [
            peopleUp.append(people) if people.direction else peopleDown.append(people)
            for people in args
        ]
        self.externalQueueUp.appendToQueue(*peopleUp)
        self.externalQueueDown.appendToQueue(*peopleDown)
    
    # Adding people to internal queue
    def addToInternalQueue(self, *args: People):
        for people in args:
            self.internalQueue.appendToQueue(people)
    
    # Unload from internal queue
    def unloadFromInternalQueue(self):
        outPeople = self.internalQueue.unloadFromFloor(self.currentFloor)
        self.outlist.appendToOutlist(*outPeople)
    
    # Load people from external queue to internal
    def loadToInternalQueue(self):
        roomLeft = self.carryingCapacity - self.internalQueue.peopleAmount
        cumulativePeopleAmount = 0
        if self.direction:
            peopleIndex = 0
            for people in self.externalQueueUp.queue[self.currentFloor]:
                cumulativePeopleAmount += people.amount
                if cumulativePeopleAmount > roomLeft:
                    break
                else:
                    self.addToInternalQueue(people)
                peopleIndex += 1
            else:
                self.externalQueueUp.queue[self.currentFloor] = (
                    self.externalQueueUp.queue[self.currentFloor][peopleIndex:]
                )
        else:
            peopleIndex = 0
            for people in self.externalQueueDown.queue[self.currentFloor]:
                cumulativePeopleAmount += people.amount
                if cumulativePeopleAmount > roomLeft:
                    break
                else:
                    self.addToInternalQueue(people)
                peopleIndex += 1
            else:
                self.externalQueueDown.queue[self.currentFloor] = (
                    self.externalQueueDown.queue[self.currentFloor][peopleIndex:]
                )
    
    # Progressing the waiting time of people
    def progressTime(self, timePassed: float):
        for floor in self.internalQueue.queue:
            for people in floor:
                setattr(people, "journeyTimer", people.journeyTimer + timePassed)
        for floor in self.externalQueueUp.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)
        for floor in self.externalQueueDown.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)
    
    # Progressing the elevator
    def progressElevator(self):
        # If at top, revert direction
        if self.currentFloor >= self.highestFloor:
            self.currentDirection = not self.currentDirection
            self.currentFloor -= 1
            self.progression = 0
        if self.currentFloor <= self.lowestFloor:
            self.direction = not self.direction
            self.currentFloor += 1
            self.progression = 0
        # If at buffer, slow down speed
        if self.progression >= self.bufferCutoff:
            speed = self.bufferSpeed
        else:
            speed = self.activeSpeed
        # Add progression to elevator
        self.progression += speed
        if self.progression > 100:
            self.progression = 0
            if self.direction:
                self.currentFloor += 1
            else:
                self.currentFloor -= 1
        self.progressTime(self.timePerStep)


# testInternalQueue = InternalQueue(floorAmount = 6)
# testExternalQueueUp = ExternalQueue(floorAmount = 6)
# testExternalQueueDown = ExternalQueue(floorAmount = 6)
# testOutlist = Outlist()

# testElevator = Elevator(
#     currentDirection = False,
#     currentFloor = 0,
#     lowestFloor = 0,
#     highestFloor = 5,
#     carryingCapacity = 10,
#     bufferCutoff = 60,
#     internalQueue = testInternalQueue,
#     externalQueueUp = testExternalQueueUp,
#     externalQueueDown = testExternalQueueDown,
#     outlist = testOutlist,
#     progression = 0,
#     activeSpeed = 5,
#     bufferSpeed = 1,
# )

# testElevator.addToInternalQueue(People(3, 4))
# print(testElevator.internalQueue.queue)
