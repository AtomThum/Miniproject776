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
        timePerStep: float = 1,
        loadTimePerPeople: float = 2,
        unloadTimePerPeople: float = 2,
    ):
        # Properties of elevator
        self.currentDirection = currentDirection  # True if elevator is going up, false if elevator is going down
        self.currentFloor = currentFloor
        self.nextFloor = currentFloor  # When initialized, set equal to current floor. Will be updated later in self.updateNextFloor()
        self.lowestFloor = lowestFloor
        self.highestFloor = highestFloor
        self.carryingCapacity = carryingCapacity
        self.progression = (
            # Acts like percentage, range from 1-100. Is an integer to avoid floating points arithmetic.
            progression
        )
        self.activeSpeed = (
            activeSpeed  # Increments progression when the elevator is not accelerating
        )
        self.bufferSpeed = (
            bufferSpeed  # Increments progression when the elevator is decelerating
        )
        self.bufferCutoff = bufferCutoff  # If progression is higher than bufferCutoff, the speed will be set to bufferSpeed
        self.timePerStep = (
            timePerStep  # Time increment when self.progressElevator() is called
        )
        self.loadTimePerPeople = loadTimePerPeople  # Time increment when self.loadToInternalQueue() is called
        self.unloadTimePerPeople = unloadTimePerPeople  # Time increment when self.unloadFromInternalQueue() is called
        # Queues
        self.internalQueue = internalQueue
        self.externalQueueUp = externalQueueUp
        self.externalQueueDown = externalQueueDown
        self.outlist = outlist

    # Finding the next floor that the elevator should go
    def scanNextFloor(self):
        if self.currentDirection:  # When the elevator goes up
            # Check the internal queue and the external queue up
            for i in range(self.currentFloor + 1, self.highestFloor + 1):
                if self.internalQueue.queue[i] or self.externalQueueUp.queue[i]:
                    return i
            # If there's no people, check the external queue down.
            # If the next floor is lower than the current floor, revert the elevator's direction
            for i in range(self.lowestFloor, self.highestFloor + 1):
                if self.externalQueueDown.queue[i]:
                    self.currentDirection = (
                        not self.currentDirection
                        if i < self.currentFloor
                        else self.currentDirection
                    )
                    return i
        else:  # When the elevator goes down
            # Check the internal queue and the external queue down
            for i in range(self.currentFloor - 1, self.lowestFloor - 1, -1):
                if self.internalQueue.queue[i] or self.externalQueueDown.queue[i]:
                    return i
            # If there's no people, check the external queue up
            # If the next floor is higher than the current floor, revert the elevator's direction
            for i in range(self.lowestFloor, self.highestFloor + 1):
                if self.externalQueueUp.queue[i]:
                    self.currentDirection = (
                        not self.currentDirection
                        if i > self.currentFloor
                        else self.currentDirection
                    )
                    return i
        # If there is literally no person, return the elevator's current floor
        return self.currentFloor

    # Updating what the next floor is
    # MUST be called every time people is added or removed
    def updateNextFloor(self):
        self.nextFloor = self.scanNextFloor()

    # Progresses the time of people.
    # Will be called when
    # 1. Mainloop is reached
    # 2. People is unloaded
    # 3. People is loaded
    def progressTime(self, timePassed: float):
        # For people inside, they're journeying. Thus, journey time is increased
        for floor in self.internalQueue.queue:
            for people in floor:
                setattr(people, "journeyTimer", people.journeyTimer + timePassed)
        # For people outside, they're waiting. Thus, waiting time is incremented
        for floor in self.externalQueueUp.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)
        for floor in self.externalQueueDown.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)

    # Adding people to external queue
    def addToExternalQueue(self, *args: People):
        peopleUp, peopleDown = [], []
        [
            peopleUp.append(people) if people.direction else peopleDown.append(people)
            for people in args
        ]
        self.externalQueueUp.appendToQueue(*peopleUp)
        self.externalQueueDown.appendToQueue(*peopleDown)
        # self.updateNextFloor()

    # Adding people to internal queue
    def addToInternalQueue(self, *args: People):
        for people in args:
            self.internalQueue.appendToQueue(people)
        self.updateNextFloor()

    # Unload from internal queue
    # Used in mainloop. Will increment time
    def unloadFromInternalQueue(self):
        outPeople = self.internalQueue.unloadFromFloor(self.currentFloor)
        self.outlist.appendToOutlist(*outPeople)
        self.updateNextFloor()
        self.progressTime(len(outPeople) * self.unloadTimePerPeople)

    # Used in mainloop. Will increment time
    # Load people from external queue to internal
    def loadToInternalQueue(self):
        roomLeft = self.carryingCapacity - self.internalQueue.peopleAmount
        cumulativePeopleAmount = 0
        peopleIndex = 0
        if self.currentDirection:
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
        self.updateNextFloor()
        self.progressTime(peopleIndex * self.unloadTimePerPeople)

    # Progressing the elevator
    def progressElevator(self):
        nextFloorDifference = abs(self.nextFloor - self.currentFloor)
        speed = 0
        if nextFloorDifference > 1:
            speed = self.activeSpeed
        elif nextFloorDifference == 1:
            if self.progression >= self.bufferCutoff:
                speed = self.bufferSpeed
            else:
                speed = self.activeSpeed
        else:
            speed = 0
        # Add progression to elevator
        self.progression += speed
        # If progression reaches 100, change floor depending on the direction.
        if self.progression > 100:
            self.progression = 0
            if self.currentDirection:
                self.currentFloor += 1
            else:
                self.currentFloor -= 1
        self.progressTime(self.timePerStep)
