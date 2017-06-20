
from tasks import *
from robots import *


def GetAvailableTasks():
    return ["blocks", "clutter", "sorting",]

def GetAvailableRobots():
    return ["jaco", "ur5_2_finger", "ur5", "ur5_robotiq"]

def GetAvailableAlgorithms():
    return [None, "ddpg", "cdqn"]


def GetTaskDefinition(task, robot, *args, **kwargs):
    '''
    Returns a particular task definition in the simulation.
    '''
    try:
        return {
            'blocks': BlocksTaskDefinition(robot, *args, **kwargs),
            'clutter': ClutterTaskDefinition(robot, *args, **kwargs),
            'sorting': SortingTaskDefinition(robot, *args, **kwargs),
            'oranges': OrangesTaskDefinition(robot, *args, **kwargs),
        }[task]
    except KeyError, e:
        raise NotImplementedError('Task %s not implemented!' % task)


def GetRobotInterface(robot, *args, **kwargs):
    '''
    Returns a simple interface representing a particular robot in the
    simulation.
    '''
    try:
        return {
            'ur5_2_finger': Ur5RobotiqInterface(*args, **kwargs),
            'ur5_robotiq': Ur5RobotiqInterface(*args, **kwargs),
            'ur5': Ur5RobotiqInterface(*args, **kwargs),
            'jaco': JacoRobotiqInterface(*args, **kwargs),
            #'iiwa_3_finger': IiwaRobotiq3FingerInterface(*args, **kwargs),
            #'iiwa': IiwaRobotiq3FingerInterface(*args, **kwargs),
        }[robot]
    except KeyError, e:
        raise NotImplementedError('Robot %s not implemented!' % robot)
