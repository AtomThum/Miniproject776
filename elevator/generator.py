from elevator.elevator import Elevator
from elevator.people import People
import random


# Generating people
class Generator:
    def __init__(
        self,
        initFloorRange: list,
        initFloorWeight: list,
        finalFloorRange: list,
        finalFloorWeight: list,
        amountRange: list,
        amountWeight: list,
        targetElevator: Elevator,
        attemptPerCall: int,
        probability: float,
    ):
        self.targetElevator = targetElevator

        self.initFloorRange = initFloorRange
        self.finalFloorRange = finalFloorRange
        self.amountRange = amountRange

        self.initFloorWeight = initFloorWeight
        self.finalFloorWeight = finalFloorWeight
        self.amountWeight = amountWeight
        self.attemptPerCall = attemptPerCall

        self.probability = probability

    # Generate people
    def generatePeople(self):
        generatedPeople = []
        for _ in range(self.attemptPerCall):
            if random.random() > self.probability:
                pass
            else:
                initFloor = random.choices(
                    population=self.initFloorRange,
                    weights=self.initFloorWeight,
                )[0]
                possibleFinalFloor = self.finalFloorRange.copy()
                possibleFinalFloor.remove(initFloor)
                possibleFinalFloorWeight = self.finalFloorWeight.copy()
                del possibleFinalFloorWeight[initFloor]
                finalFloor = random.choices(
                    population=possibleFinalFloor,
                    weights=possibleFinalFloorWeight,
                )[0]
                peopleAmount = random.choices(
                    population=self.amountRange, weights=self.amountWeight
                )[0]
                generatedPeople.append(
                    People(
                        startingFloor=initFloor,
                        destinationFloor=finalFloor,
                        amount=peopleAmount,
                    )
                )
        return generatedPeople
