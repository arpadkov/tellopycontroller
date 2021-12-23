from enum import Enum


class RcControl(Enum):

    Up = 0
    Down = 1
    Left = 2
    Right = 3
    Backward = 4
    Forward = 5
    RotateLeft = 6
    RotateRight = 7
    Land = 8


class GeneralCommand(Enum):

    Connect = 0
    Takeoff = 1
    Land = 2
    Emergency = 3


class GeneralControl(Enum):

    Up = 0
    Down = 1
    Left = 2
    Right = 3
    Backward = 4
    Forward = 5
    RotateLeft = 6
    RotateRight = 7
