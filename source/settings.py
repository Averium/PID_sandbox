import pygame


class SETTINGS:

    FPS = 120
    DISPLAY_FLAGS = pygame.FULLSCREEN | pygame.HWACCEL

    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080

    SCALE = 300  # pixels / meter
    HANDLE_HIGHLIGHT = 3


class COLORS:

    BACKGROUND = (0, 0, 0)
    MASS = (160, 0, 0)
    RAIL = (60, 60, 60)
    HANDLE_INACTIVE = (0, 150, 0)
    HANDLE_ACTIVE = (0, 200, 0)
    REFERENCE = (60, 60, 60)

    TUNER = (((100, 100, 100), (120, 120, 120)), ((150, 0, 0), (200, 50, 50)))
    SETTING = (((100, 100, 100), (120, 120, 120)), ((0, 0, 150), (50, 50, 200)))


class SYSTEM:

    MASS = 0.5
    DAMPING = 0.5
    MAX_TORQUE = 1
    G = 9.81

    MASS_WIDTH = 0.4
    MASS_HEIGHT = 0.2
    RAIL_LENGTH = 3
    RAIL_WIDTH = 0.02

    HANDLE_SIZE = 0.05

    KP = 0
    KI = 0
    KD = 0