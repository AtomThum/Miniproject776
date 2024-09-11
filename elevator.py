from people import People
from outlist import Outlist

# Initializing the Elevator class
class Elevator:
    def __init__(
        self,
        direction: bool,
        floor: int,
        minFloor: int,
        maxFloor: int,
        carryLimit: int,
        bufferCutoff: float,
        outList: Outlist,
        progression: float = 0,
        activeSpeed: float = 5,
        bufferSpeed: float = 1,
        *args: People
    ):
        # Properties of elevator
        self.direction = direction  # True -> going up, False = going down
        self.floor = floor
        self.minFloor = minFloor
        self.maxFloor = maxFloor
        self.carryLimit = carryLimit
        self.progression = (
            # In the range 0 - 100 (If enters new floor, progression = 0)
            progression
        )
        self.bufferCutoff = bufferCutoff  # In the range 0 - 100
        self.activeSpeed = activeSpeed
        self.bufferSpeed = bufferSpeed

        # Queues
        self.internalQueue = []
        self.internalQueueNum = len(self.internalQueue)
        self.outList = outList
        for i in args:
            self.peopleIn.append(i)

    # Adding people to external queue
    def addExternalQueue(self, *args: People):
        for i in args:
            self.externalQueue.append(i)

    # Adding people to internal queue
    def addInternalQueue(self, *args: People):
        for i in args:
            self.internalQueue.append(i)
        self.internalQueueNum += len(args)

    # Unload people from internal queue to outlist
    # Checks every people in internal queue. If the destination floor matches the elevator's current floor, move the people to the outlist
    def unloadFromInternalQueue(self):
        # Creating a boolean list. True if the destination floor matches the current floor, false otherwise.
        outQueueBool = [i.destinationFloor == self.floor for i in self.internalQueue]
        internalTemp = []
        # If true, move to outlist, pass otherwise.
        for people, boolean in zip(self.internalQueue, outQueueBool):
            if boolean:
                self.outList.addOutlist(people)
            else:
                internalTemp.append(people)
        self.internalQueue = internalTemp

    # Load people from external queue to internal queue
    # Checks every people in external queue. Pop if possible.
    def loadFromExternalQueue(self):
        global externalTemp
        # Creating a boolean list. True if the current floor matches the starting floor, false otherwise.
        inQueueBool = [i.startFloor == self.floor for i in externalTemp]
        self.internalQueueNum = len(self.internalQueue)
        freeSpaceNum = self.carryLimit - self.internalQueueNum
        # If true, move to temporary queues
        inQueueTemp = []
        exQueueTemp = []
        for people, boolean in zip(externalTemp, inQueueBool):
            if boolean:
                inQueueTemp.append(people)
            else:
                exQueueTemp.append(people)
        # Finding the cumulative sum of people
        cumulativeSum = 0
        loadableQueueTemp = []
        for people in inQueueTemp:
            cumulativeSum += people.amount
            if cumulativeSum > freeSpaceNum:
                exQueueTemp.append(people)
            else:
                loadableQueueTemp.append(people)
        self.internalQueue.extend(loadableQueueTemp)
        externalTemp = exQueueTemp

    # Progressing the elevator
    def progressElevator(self):
        # If at top, revert direction
        if self.floor >= self.maxFloor:
            self.direction = not self.direction
            self.floor -= 1
            self.progression = 0
        if self.floor <= self.minFloor:
            self.direction = not self.direction
            self.floor += 1
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
            if self.direction == True:
                self.floor += 1
            else:
                self.floor -= 1