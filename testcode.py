from elevator.elevator import *
from elevator.queues import *

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