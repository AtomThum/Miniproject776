import random

from elevator.elevator import Elevator
from elevator.people import People


# Generating people
class Generator:
    def __init__(
        self,
        initFloor: int,
        finalFloorRange: list,
        finalFloorWeight: list,
        amountRange: list,
        amountWeight: list,
        targetElevator: Elevator,
        attemptPerCall: int,
        probability: float,
    ):
        self.initFloor = initFloor
        self.targetElevator = targetElevator

        self.finalFloorRange = finalFloorRange
        self.amountRange = amountRange

        self.finalFloorWeight = finalFloorWeight
        self.amountWeight = amountWeight
        self.attemptPerCall = attemptPerCall  # The amount per attempt

        self.probability = probability

    # Generate people
    def generatePeople(self):
        generatedPeople = []
        for _ in range(self.attemptPerCall):
            if (
                random.random() < self.probability
            ):
                finalFloor = random.choices(
                    population=self.finalFloorRange, weights=self.finalFloorWeight, k=1
                )[0]  # Generate final floor

                peopleAmount = random.choices(
                    population=self.amountRange, weights=self.amountWeight, k=1
                )[0]

                generatedPeople.append(
                    People(
                        startingFloor=self.initFloor,
                        destinationFloor=finalFloor,
                        amount=peopleAmount,
                    )
                )
        return generatedPeople

    def generatePeopleToElevator(self):
        self.targetElevator.addToExternalQueue(*self.generatePeople())
