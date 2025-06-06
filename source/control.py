from collections import deque
from math import pi
from random import random

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

    def __init__(self, kp, ki, kd, nd=0, limit=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.nd = nd

        self.i_term = 0
        self.d_term = 0

        self.error = 0
        self.last_error = 0

        self.output = 0

        self.anti_windup = False
        self.limit = limit

    def update_integral(self, dt):
        saturated = (self.output == -self.limit and self.error < 0) or (self.output == self.limit and self.error > 0)

        if not (self.anti_windup and saturated):
            self.i_term = self.i_term + self.error * dt

        if self.ki == 0:
            self.i_term = 0

    def update_derivative(self, dt):
        rc = 1 / (2 * pi * self.nd)
        alpha = dt / (rc + dt)

        self.d_term = self.d_term + alpha * ((self.error - self.last_error) / dt - self.d_term)
        self.last_error = self.error

    def update(self, reference, measurement, dt):
        self.error = reference - measurement

        self.update_integral(dt)
        self.update_derivative(dt)

        control_p = self.error * self.kp
        control_i = self.i_term * self.ki
        control_d = self.d_term * self.kd

        if self.limit > 0:
            self.output = min(max(control_p + control_i + control_d, -self.limit), self.limit)
        else:
            self.output = control_p + control_i + control_d

class Delay:

    def __init__(self, delay):
        self.queue = deque()
        self.delay = delay
        self.timestamp = 0
        self._value = 0

    def request(self, value):
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


class Actuator(Delay):

    def __init__(self, delay=0, limit=0):
        super().__init__(delay)
        self.limit = limit

    @property
    def value(self):
        return min(max(self._value, -self.limit), self.limit) if self.limit > 0 else self._value


class Sensor(Delay):

    def __init__(self, delay=0, noise_amplitude=0, noise_filter=1):
        super().__init__(delay)
        self.noise_amplitude = noise_amplitude
        self.noise_filter = noise_filter

    def update(self, time):
        temp = self._value
        super().update(time)

        noisy_value = self._value + (random() * 2 - 1) * self.noise_amplitude
        if self.noise_filter > 0:
            self._value = noisy_value * self.noise_filter + temp * (1.0 - self.noise_filter)
