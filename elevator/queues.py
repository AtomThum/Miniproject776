from people import People


# Outlist - for storing people that already left the elevator.
class Outlist:
    def __init__(self, outlist: list = []):
        self.outlist = outlist

    def appendToOutlist(self, *args: People):
        for i in args:
            self.outlist.append(i)


# Queues system
class InternalQueue:
    def __init__(self, floorAmount: int):
        self.queue = [[] for _ in range(floorAmount)]
        self.peopleAmount = 0

    # Internal queue focuses on people leaving
    # Append people to a floor queue
    def appendToQueue(self, *args):
        for people in args:
            self.queue[people.destinationFloor].append(people)
            self.peopleAmount += people.amount

    # Remove people from a certain floor, returning the people removed
    def unloadFromFloor(self, floor: int):
        temp = self.queue[floor]
        leavingAmount = sum(people.amount for people in temp)
        self.peopleAmount -= leavingAmount
        self.queue[floor] = []
        return temp


class ExternalQueue:
    def __init__(self, floorAmount: int):
        self.queue = [[] for _ in range(floorAmount)]

    # External queue focuses on people entering
    # Append people to a floor queue
    def appendToQueue(self, *args):
        for people in args:
            self.queue[people.startingFloor].append(people)
