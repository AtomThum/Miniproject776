# Initializing the class for peoples
class People:
    def __init__(self, startFloor: int, destinationFloor: int, amount: int = 1, elevatorBreakCount: int = 0):
        self.startFloor = startFloor
        self.destinationFloor = destinationFloor
        self.amount = amount  # Amount of people that's in a group
        self.waitingTimer = 0  # Wait time
        self.journeyTimer = 0  # Journey time
        self.direction = True if (destinationFloor - startFloor > 0) else False
        self.elevatorBreakCount = (
            0  # The amount of pauses before reaching the destination
        )
        self.description = f"[{self.amount} people. Destination: {self.destinationFloor}. Started: {self.startFloor}]"