from elevator.people import People
from elevator.queues import Outlist, InternalQueue, ExternalQueue
import itertools as itr
import pprint as pp


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
        self.nextFloor = currentFloor  # Is set to current floor when initialized, but will be updated later by the self.updateNextFloor() function
        self.lowestFloor = lowestFloor  # Normally set to zero
        self.highestFloor = highestFloor
        self.carryingCapacity = carryingCapacity
        self.progression = (
            # Acts like percentage. Ranges from 1-100. Uses integers to avoid floating points arithmetic.
            progression
        )
        self.activeSpeed = activeSpeed  # Speed used to increment the elevator's progression when the elevator isn't accelerating
        self.bufferSpeed = bufferSpeed  # Speed used to increment the elevator's progression when the elevator is decelerating
        self.bufferCutoff = bufferCutoff  # When progression is higher than buffer cut-off, the buffer speed will be used
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

    def updateEdgeDirection(self):
        isAtLowestFloor = self.currentFloor == self.lowestFloor
        isAtHighestFloor = self.currentFloor == self.highestFloor
        if isAtLowestFloor:
            self.currentDirection = True
        elif isAtHighestFloor:
            self.currentDirection = False

    # Finding the next floor that the elevator should travel to
    def scanNextFloor(self):
        if self.currentDirection:  # If the elevator is going up
            for floor in range(
                self.currentFloor, self.highestFloor + 1, 1
            ):  # Check from the current floor to the highest.
                if self.internalQueue.queue[floor] or self.externalQueueUp.queue[floor]:
                    return floor
            for floor in range(
                self.highestFloor, self.lowestFloor - 1, -1
            ):  # If there is no one, then revert direction and check from the highest to the lowest
                if (
                    self.internalQueue.queue[floor]
                    or self.externalQueueDown.queue[floor]
                ):
                    return floor
        else:  # If the elevator is going down
            for floor in range(
                self.currentFloor, self.lowestFloor - 1, -1
            ):  # Check from the current floor to the lowest
                if (
                    self.internalQueue.queue[floor]
                    or self.externalQueueDown.queue[floor]
                ):
                    return floor
            for floor in range(
                self.lowestFloor, self.highestFloor + 1, 1
            ):  # If there is no one, then revert the direction and check from the lowest to highest
                if self.internalQueue.queue[floor] or self.externalQueueUp.queue[floor]:
                    return floor
        return self.currentFloor

    # Updating the next floor
    # Only changes when people are added or removed
    def updateNextFloor(self):
        self.updateEdgeDirection()
        self.nextFloor = self.scanNextFloor()
        if self.nextFloor - self.currentFloor > 0:
            self.currentDirection = True
        elif self.nextFloor - self.currentFloor < 0:
            self.currentDirection = False
        else:
            pass

    # Progresses the timer of the people.
    # Will be called when
    # 1. Running the main loop
    # 2. People is unloaded
    # 3. People is loaded
    def progressTime(self, timePassed: float):
        # Journey time is increased for people inside
        for floor in self.internalQueue.queue:
            for people in floor:
                setattr(people, "journeyTimer", people.journeyTimer + timePassed)
        # Waiting time is increased for people outside
        for floor in itr.chain(
            self.externalQueueUp.queue, self.externalQueueDown.queue
        ):
            for people in floor:
                setattr(people, "waitingTimer", people.waitingTimer + timePassed)

    # Increments the elevator break count of people inside internal queue
    # Calls after people get loaded or unloaded from the elevator.
    def progressElevatorBreakCount(self):
        for floor in self.internalQueue.queue:
            for people in floor:
                setattr(people, "elevatorBreakCount", people.elevatorBreakCount + 1)

    # Force add people to external queue
    # Automatically separates between queue up and queue down
    def addToExternalQueue(self, *args: People):
        peopleUp, peopleDown = [], []
        [
            peopleUp.append(people) if people.direction else peopleDown.append(people)
            for people in args
        ]
        self.externalQueueUp.appendToQueue(*peopleUp)
        self.externalQueueDown.appendToQueue(*peopleDown)
        self.updateNextFloor()

    # Force add people to internal queue
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
        for floor in range(
            self.currentFloor + reverseCheckStep, reverseCheckLimit, reverseCheckStep
        ):
            if (
                self.internalQueue.queue[floor]
                or self.externalQueueDown.queue[floor]
                or self.externalQueueUp.queue[floor]
            ):
                break
        else:
            if not (
                (self.currentFloor == self.highestFloor)
                or (self.currentFloor == self.lowestFloor)
            ):
                self.currentDirection = not self.currentDirection

        # Loads the people into internal queue
        if self.currentDirection:
            for people in self.externalQueueUp.queue[self.currentFloor]:
                cumulativePeopleAmount += people.amount
                if cumulativePeopleAmount > roomLeft:
                    break
                else:
                    self.addToInternalQueue(people)
                peopleIndex += 1
                self.externalQueueUp.peopleAmount -= 1
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
                self.externalQueueDown.peopleAmount -= 1
            else:
                self.externalQueueDown.queue[self.currentFloor] = (
                    self.externalQueueDown.queue[self.currentFloor][peopleIndex:]
                )
        self.updateNextFloor()
        self.progressTime(peopleIndex * self.unloadTimePerPeople)

    # Progressing the elevator
    def progressElevator(self):
        if (
            self.internalQueue.peopleAmount
            + self.externalQueueDown.peopleAmount
            + self.externalQueueUp.peopleAmount
            == 0
        ):
            return None

        nextFloorDifference = abs(self.nextFloor - self.currentFloor)
        # Setting the speed of the elevator
        speed = 0
        if nextFloorDifference > 1:  # If the elevator isn't adjacent to the next floor
            speed = self.activeSpeed  # Set the speed to be the default speed
        elif nextFloorDifference == 1:  # If the elevator is adjacent to the next floor
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

    def printElevatorInfo(self):
        print(f"Progression: {self.progression}")
        print(f"Current Floor: {self.currentFloor}")
        print(f"Next Floor: {self.nextFloor}")
        print(f"Current Direction: {self.currentDirection}")

        floorAmount = self.highestFloor - self.lowestFloor + 1
        internalQueuePrint = [[] for _ in range(floorAmount)]
        externalQueueUpPrint = [[] for _ in range(floorAmount)]
        externalQueueDownPrint = [[] for _ in range(floorAmount)]
        outlistPrint = []
        for floor in range(self.lowestFloor, self.highestFloor + 1, 1):
            [
                internalQueuePrint[floor].append(
                    (people.startingFloor, people.destinationFloor)
                )
                for people in self.internalQueue.queue[floor]
            ]
            [
                externalQueueDownPrint[floor].append(
                    (people.startingFloor, people.destinationFloor)
                )
                for people in self.externalQueueDown.queue[floor]
            ]
            [
                externalQueueUpPrint[floor].append(
                    (people.startingFloor, people.destinationFloor)
                )
                for people in self.externalQueueUp.queue[floor]
            ]
        [
            outlistPrint.append((people.startingFloor, people.destinationFloor))
            for people in self.outlist.outlist
        ]

        print(f"Internal Queue: {pp.pformat(internalQueuePrint)}")
        print(f"External Queue Up: {pp.pformat(externalQueueUpPrint)}")
        print(f"External Queue Down: {pp.pformat(externalQueueDownPrint)}")
        print(f"Outlist: {pp.pformat(outlistPrint)}")
