from elevator.elevator import Elevator

# Generating people
class Generator():
    def __init__(self,
            initFloorRange: list,
            finalFloorRange: list,
            targetElevator: Elevator
        ):
        self.initFloorRange = initFloorRange
        self.finalFloorRange = finalFloorRange
        self.targetElevator = targetElevator