from elevator.elevator import Elevator
from elevator.queues import Outlist, InternalQueue, ExternalQueue
from elevator.people import People
from elevator.generator import Generator

testInternalQueue = InternalQueue(floorAmount=6)
testExternalQueueUp = ExternalQueue(floorAmount=6)
testExternalQueueDown = ExternalQueue(floorAmount=6)
testOutlist = Outlist()

testElevator = Elevator(
    currentDirection=False,
    currentFloor=0,
    lowestFloor=0,
    highestFloor=5,
    carryingCapacity=10,
    bufferCutoff=60,
    internalQueue=testInternalQueue,
    externalQueueUp=testExternalQueueUp,
    externalQueueDown=testExternalQueueDown,
    outlist=testOutlist,
    progression=0,
    activeSpeed=5,
    bufferSpeed=1,
)

floorRange = list(range(6))
generator = Generator(
    initFloorRange = floorRange,
    initFloorWeight = [0.5, 0.25, 0.25, 0, 0, 0],
    finalFloorRange = floorRange,
    finalFloorWeight = [0.16, 0.16, 0.16, 0.16, 0.16],
    amountRange = [1, 2, 3, 4, 5],
    amountWeight = [0.2, 0.2, 0.2, 0.2, 0.2],
    targetElevator = testElevator,
    attemptPerCall = 30,
    probability = 0.2
)

generated = generator.generatePeople()
[print(f"{i.startingFloor}, {i.destinationFloor}") for i in generated]
