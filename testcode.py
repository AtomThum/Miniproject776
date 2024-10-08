from elevator.elevator import Elevator
from elevator.queues import Outlist, InternalQueue, ExternalQueue
from elevator.people import People
from elevator.generator import Generator

internalQ = InternalQueue(floorAmount=6)
externalQUp = ExternalQueue(floorAmount=6)
externalQDown = ExternalQueue(floorAmount=6)
outlist = Outlist()

elevator = Elevator(
    currentDirection=True,
    currentFloor=1,
    lowestFloor=0,
    highestFloor=5,
    carryingCapacity=10,
    bufferCutoff=60,
    internalQueue=internalQ,
    externalQueueUp=externalQUp,
    externalQueueDown=externalQDown,
    outlist=outlist,
    progression=0,
    activeSpeed=5,
    bufferSpeed=1,
)

elevator.addToExternalQueue(People(4, 1))
print(elevator.externalQueueUp.queue)
print(elevator.externalQueueDown.queue)

print(f"Next Floor is: {elevator.scanNextFloor()}")
print(f"Current elevator direction: {elevator.currentDirection}")
