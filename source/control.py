from collections import deque

import pygame

from source.settings import COLORS, SETTINGS, SYSTEM
from source.system import System


class Reference:

    MARKER_SIZE = 0.1 * SETTINGS.SCALE

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

        center = self.system.center + ex * self.pos * SETTINGS.SCALE + ey * System.HANDLE_SIZE * 4
        handle = center + ey * (Reference.MARKER_SIZE * 2 + System.HANDLE_SIZE)

        return ex, ey, center, handle

    def events(self, mouse_pos, mouse_pressed):
        ex, ey, center, handle = self.locate()

        self.hovered = (mouse_pos - handle).length() < System.HANDLE_SIZE * 2

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
            radius = System.HANDLE_SIZE + SETTINGS.HANDLE_HIGHLIGHT
        else:
            color = COLORS.HANDLE_INACTIVE
            radius = System.HANDLE_SIZE

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

        if self.ki == 0:
            self.zoh = 0

        control_p = error * self.kp
        control_i = self.zoh * self.ki
        control_d = (error - self.last_error) / dt * self.kd

        self.last_error = error

        return control_p + control_i + control_d


class Delay:

    def __init__(self, delay):
        self.queue = deque()
        self.delay = delay
        self.timestamp = 0
        self._value = 0

    def add(self, value):
        self.queue.append((value, self.timestamp))

    def update(self, time):
        self.timestamp = time

        while self.queue:
            next_value, next_time = self.queue[0]
            if self.timestamp - next_time >= self.delay:
                self._value, _ = self.queue.popleft()
            else:
                break

    @property
    def value(self):
        return self._value