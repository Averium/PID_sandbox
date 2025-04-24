import pygame
from openai import project

from source.settings import COLORS, SETTINGS, SYSTEM
from math import pi

Vector = pygame.math.Vector2


class Reference:

    MARKER_SIZE = 20
    MARKER_DISTANCE = SYSTEM.MASS_HEIGHT / 2 * 1.5

    def __init__(self, system):
        self.system = system
        self.pos = 0

        self.hovered = False
        self.held = False

    def move(self, velocity, dt):
        self.move_to(self.pos + velocity * dt)

    def move_to(self, pos):
        self.pos = min(max(pos, -SYSTEM.RAIL_LENGTH / 2), SYSTEM.RAIL_LENGTH / 2)

    def locate(self):
        ex = self.system.ray
        ey = ex.rotate(90)

        center = self.system.center + ex * self.pos * SETTINGS.SCALE + ey * Reference.MARKER_DISTANCE * SETTINGS.SCALE
        handle = center + ey * (Reference.MARKER_SIZE * 2 + Reference.MARKER_DISTANCE)

        return ex, ey, center, handle

    def events(self, mouse_pos, mouse_pressed):
        ex, ey, center, handle = self.locate()

        self.hovered = (mouse_pos - handle).length() < SETTINGS.HANDLE_SIZE * 2

        if mouse_pressed[0] and self.hovered:
            self.held = True
        if not mouse_pressed[0]:
            self.held = False

        if self.held:
            ray = mouse_pos - self.system.center
            self.move_to(ray.dot(ex) / SETTINGS.SCALE)

    def render(self, display):
        ex, ey, center, handle = self.locate()

        arrow = (
            center,
            center + ex * Reference.MARKER_SIZE / 3 + ey * Reference.MARKER_SIZE,
            center - ex * Reference.MARKER_SIZE / 3 + ey * Reference.MARKER_SIZE
        )

        if self.hovered or self.held:
            color = COLORS.HANDLE_ACTIVE
            radius = SETTINGS.HANDLE_SIZE + SETTINGS.HANDLE_HIGHLIGHT
        else:
            color = COLORS.HANDLE_INACTIVE
            radius = SETTINGS.HANDLE_SIZE

        pygame.draw.polygon(display, COLORS.REFERENCE, arrow)
        pygame.draw.circle(display, color, handle, radius)


class PID:

    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.zoh = 0
        self.last_error = 0

    def tune(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def control(self, reference, measurement, dt):
        error = reference - measurement

        self.zoh = self.zoh + error * dt

        control_p = error * self.kp
        control_i = self.zoh * self.ki
        control_d = (error - self.last_error) / dt * self.kd

        self.last_error = error

        return control_p + control_i + control_d