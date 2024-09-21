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

generator = Generator(
    initFloorRange=list(range(0, 6)),
    initFloorWeight=[1 / 6] * 6,
    finalFloorRange=list(range(0, 6)),
    finalFloorWeight=[1 / 6] * 6,
    amountRange=list(range(1, 4)),
    amountWeight=[1 / 3] * 3,
    targetElevator=elevator,
    attemptPerCall=3,
    probability=0.05,
)

generator.generatePeopleToElevator()
print(elevator.externalQueueUp.queue)
print(elevator.externalQueueDown.queue)

tickAmount = 1000
for tick in range(tickAmount):
    generator.generatePeopleToElevator()
    elevator.progressElevator()
    if elevator.progression == 0:
        elevator.unloadFromInternalQueue()
        elevator.loadToInternalQueue()
    else:
        pass
