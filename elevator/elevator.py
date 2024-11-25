from elevator.people import People
from elevator.queues import Outlist, InternalQueue, ExternalQueue
from collections import deque
import itertools as itr


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
        # Edge cases: Elevator is at the highest or lowest floor, and doesn't revert direction
        # If there is no one at that floor, revert direction.
        self.currentDirection = (
            False
            if self.currentFloor == self.highestFloor
            and (not self.externalQueueDown.queue[self.highestFloor])
            and (not self.externalQueueUp.queue[self.highestFloor])
            else self.currentDirection
        )
        self.currentDirection = (
            True
            if self.currentFloor == self.lowestFloor
            and (not self.externalQueueDown.queue[self.lowestFloor])
            and (not self.externalQueueUp.queue[self.lowestFloor])
            else self.currentDirection
        )
        # If elevator is going up
        if self.currentDirection:
            for floor in range(self.currentFloor, self.highestFloor + 1, 1):
                if self.internalQueue.queue[floor] or self.externalQueueUp.queue[floor]:
                    return floor
            for floor in range(self.highestFloor, self.lowestFloor - 1, -1):
                if (
                    self.internalQueue.queue[floor]
                    or self.externalQueueDown.queue[floor]
                ):
                    return floor
        # If self is going down
        else:
            for floor in range(self.currentFloor, self.lowestFloor - 1, -1):
                if (
                    self.internalQueue.queue[floor]
                    or self.externalQueueDown.queue[floor]
                ):
                    return floor
            for floor in range(self.lowestFloor, self.highestFloor + 1, 1):
                if self.internalQueue.queue[floor] or self.externalQueueUp.queue[floor]:
                    return floor
        return self.currentFloor

    # Updating what the next floor is
    # MUST be called every time people is added or removed
    def updateNextFloor(self):
        self.nextFloor = self.scanNextFloor()
        if self.nextFloor - self.currentFloor > 0:
            self.currentDirection = True
        elif self.nextFloor - self.currentFloor < 0:
            self.currentDirection = False
        else:
            pass

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
        # For people outside, they're waiting. Thus, waiting time is increased
        for floor in self.externalQueueUp.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)
        for floor in self.externalQueueDown.queue:
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)
    
    def progressElevatorBreakCount(self):
        for floor in self.internalQueue.queue:
            for people in floor:
                setattr(people, "elevatorBreakCount", people.elevatorBreakCount + 1)

    # Adding people to external queue
    def addToExternalQueue(self, *args: People):
        peopleUp, peopleDown = [], []
        [
            peopleUp.append(people) if people.direction else peopleDown.append(people)
            for people in args
        ]
        self.externalQueueUp.appendToQueue(*peopleUp)
        self.externalQueueDown.appendToQueue(*peopleDown)
        self.updateNextFloor()

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
            reverseCheckLimit = self.highestFloor + 1
            reverseCheckStep = 1
        else:
            reverseCheckLimit = self.lowestFloor - 1
            reverseCheckStep = -1
        # Check if the elevator should revert direction or not
        for floor in range(self.currentFloor + reverseCheckStep, reverseCheckLimit, reverseCheckStep):
            if (
                self.internalQueue.queue[floor]
                or self.externalQueueDown.queue[floor]
                or self.externalQueueUp.queue[floor]
            ):
               break
        else:
            self.currentDirection = not self.currentDirection 

        # Actually loading the people into internal queue
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
        # Setting the speed of the elevator
        speed = 0
        if nextFloorDifference > 1:  # If the elevator isn't adjacent to the next floor
            speed = self.activeSpeed  # Set the speed to be the default speed
        elif (
            nextFloorDifference == 1
        ):  # Else (If the elevator IS adjacent to the next floor)
            if (
                self.progression >= self.bufferCutoff
            ):  # Check whether the elevator is in the buffer or not
                speed = self.bufferSpeed  # If in the buffer, set equal to buffer speed
            else:  # Else
                speed = self.activeSpeed  # Set the speed to be the default speed
        else:
            speed = 0  # Otherwise, the elevator is stopping, and thus shall not move
            self.unloadFromInternalQueue()
            self.progressElevatorBreakCount()
            self.loadToInternalQueue()

        # Add progression to elevator
        self.progression += speed
        # If progression reaches 100, change floor depending on the direction.
        if self.progression > 100:
            self.progression = 0
            if self.currentDirection:
                self.currentFloor += 1
            else:
                self.currentFloor -= 1
        # Add time to all the people in the elevator
        self.progressTime(self.timePerStep)