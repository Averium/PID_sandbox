from math import cos, sin, radians

import pygame
from pygame.math import Vector2 as Vector

from source.settings import COLORS, SETTINGS, SYSTEM


class System:

    RAIL_WIDTH = SYSTEM.RAIL_WIDTH * SETTINGS.SCALE
    HANDLE_SIZE = SYSTEM.HANDLE_SIZE * SETTINGS.SCALE

    def __init__(self, mass, damping, angle, alpha=0.1):
        self.center = Vector(SETTINGS.WINDOW_WIDTH / 2, SETTINGS.WINDOW_HEIGHT / 2)

        self.mass = mass
        self.damping = damping

        self._target_angle = angle
        self._angle = angle
        self._angle_filter = alpha

        self._ray = None
        self._shape = None
        self._left_end = None
        self._right_end = None

        self.tilt(angle)
        self.update_angle()

        self.pos = 0
        self.vel = 0
        self.acc = 0

        self.force = 0

        self.hovered_left = False
        self.hovered_right = False
        self.held_left = False
        self.held_right = False

    @property
    def ray(self):
        return self._ray

    def apply_force(self, force):
        self.force += force

    def events(self, mouse_pos, mouse_pressed):
        self.hovered_left = (mouse_pos - self._left_end).length() < System.HANDLE_SIZE * 2
        self.hovered_right = (mouse_pos - self._right_end).length() < System.HANDLE_SIZE * 2

        if mouse_pressed[0]:
            if self.hovered_left:
                self.held_left = True
            if self.hovered_right:
                self.held_right = True
        else:
            self.held_left = False
            self.held_right = False
        if mouse_pressed[2]:
            self.tilt(0)

        if self.held_left or self.held_right:
            if self.held_left:
                ray = (self.center - mouse_pos).normalize()
            else:
                ray = (mouse_pos - self.center).normalize()

            angle = radians(Vector(1, 0).angle_to(ray))
            self.tilt(angle)

    def update(self, dt):
        self.update_angle()
        self.apply_force(SYSTEM.G * sin(self._angle))
        self.apply_force(-self.vel * self.damping)

        self.acc = self.force / self.mass
        self.vel = self.vel + self.acc * dt
        self.pos = self.pos + self.vel * dt

        if self.pos > SYSTEM.RAIL_LENGTH / 2:
            self.pos = SYSTEM.RAIL_LENGTH / 2
            self.vel = 0
        if self.pos < -SYSTEM.RAIL_LENGTH / 2:
            self.pos = -SYSTEM.RAIL_LENGTH / 2
            self.vel = 0

        self.force = 0

    def tilt(self, angle):
        self._target_angle = angle

    def update_angle(self):
        self._angle = self._target_angle * self._angle_filter + self._angle * (1 - self._angle_filter)

        self._ray = Vector(cos(self._angle), sin(self._angle))

        self._left_end = self.center - self._ray * SYSTEM.RAIL_LENGTH / 2 * SETTINGS.SCALE
        self._right_end = self.center + self._ray * SYSTEM.RAIL_LENGTH / 2 * SETTINGS.SCALE

        dx = SYSTEM.MASS_WIDTH * SETTINGS.SCALE / 2
        dy = SYSTEM.MASS_HEIGHT * SETTINGS.SCALE / 2

        norm = self._ray.rotate(90)

        self._shape = (
            self._ray * dx + norm * dy,
            -self._ray * dx + norm * dy,
            -self._ray * dx - norm * dy,
            self._ray * dx - norm * dy,
        )

    def render(self, display):

        center = self.center + self._ray * self.pos * SETTINGS.SCALE
        points = tuple(point + center for point in self._shape)

        if self.hovered_left or self.held_left:
            left_color = COLORS.HANDLE_ACTIVE
            left_radius = System.HANDLE_SIZE + SETTINGS.HANDLE_HIGHLIGHT
        else:
            left_color = COLORS.HANDLE_INACTIVE
            left_radius = System.HANDLE_SIZE

        if self.hovered_right or self.held_right:
            right_color = COLORS.HANDLE_ACTIVE
            right_radius = System.HANDLE_SIZE + SETTINGS.HANDLE_HIGHLIGHT
        else:
            right_color = COLORS.HANDLE_INACTIVE
            right_radius = System.HANDLE_SIZE

        pygame.draw.line(display, COLORS.RAIL, self._left_end, self._right_end, int(System.RAIL_WIDTH))
        pygame.draw.circle(display, left_color, self._left_end, left_radius)
        pygame.draw.circle(display, right_color, self._right_end, right_radius)
        pygame.draw.polygon(display, COLORS.MASS, points)