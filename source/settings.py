
class SETTINGS:

    FPS = 120

    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768

    SCALE = 200  # pixels / meter

    HANDLE_SIZE = 8
    HANDLE_HIGHLIGHT = 2


class COLORS:

    BACKGROUND = (0, 0, 0)
    MASS = (160, 0, 0)
    RAIL = (60, 60, 60)
    HANDLE_INACTIVE = (0, 150, 0)
    HANDLE_ACTIVE = (0, 200, 0)
    REFERENCE = (50, 50, 200)


class SYSTEM:

    MASS = 0.5
    DAMPING = 2
    MAX_TORQUE = 1
    G = 9.81

    MASS_WIDTH = 0.4
    MASS_HEIGHT = 0.2
    RAIL_LENGTH = 3
    ANGLE_LIMIT_DEG = 45

    KP = 6
    KI = 10
    KD = 4