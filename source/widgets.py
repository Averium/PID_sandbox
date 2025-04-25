from collections import deque

import pygame
from pygame.math import Vector2 as Vector

import numpy

from source.settings import LAYOUT

pygame.font.init()


class WidgetContainer(list):

    def __init__(self):
        list.__init__([])

    def add(self, widget):
        if not widget in self:
            self.append(widget)
            self.sort(key=lambda w: w.layer)

    def events(self, mouse_pos, mouse_pressed):
        for widget in self:
            widget.events(mouse_pos, mouse_pressed)

    def render(self, display):
        for widget in self:
            widget.render(display)


class Widget(pygame.Rect):

    def __init__(self, container: WidgetContainer, rect, color):
        super().__init__(rect)

        container.add(self)

        self.color = color

        self.hovered = False
        self.clicked = False
        self.held = False

        self.last_pressed = pygame.mouse.get_pressed()

    @property
    def layer(self):
        return 1

    def events(self, mouse_pos, mouse_pressed):
        self.hovered = self.collidepoint(mouse_pos)
        self.clicked = self.hovered and (mouse_pressed[0] and not self.last_pressed[0])

        if self.clicked:
            self.held = True
        if not mouse_pressed[0]:
            self.held = False

        self.last_pressed = mouse_pressed

    def render(self, display):
        pygame.draw.rect(display, self.color, self)


class TextWidget(Widget):

    SMALL_FONT = pygame.font.SysFont("monospace", 20, True)
    LARGE_FONT = pygame.font.SysFont("monospace", 32, True)

    def __init__(self, container, anchor, text, color, large=False, align="topleft"):
        super().__init__(container, (0, 0, 1, 1), color)

        self.font = TextWidget.LARGE_FONT if large else TextWidget.SMALL_FONT

        self.anchor = Vector(anchor)
        self.align = align
        self.text = text
        self.set_text(text)

    def set_text(self, text):
        self.text = text
        width, height = self.font.size(text)
        self.update(0, 0, width, height)
        setattr(self, self.align, self.anchor)

    def render(self, display):
        surface = self.font.render(self.text, True, self.color)
        display.blit(surface, self)

    @property
    def layer(self):
        return 2


class Tuner(TextWidget):

    def __init__(self, container, anchor, text, color, value, step=0.1, limits=(-1, 1), align="topleft"):
        self._value = 0
        super().__init__(container, anchor, text, color, align=align)

        self._limits = limits
        self._step = step
        self._base_text = text
        self.set_value(value)

    @property
    def value(self):
        return self._value

    @property
    def full_text(self):
        return f"{self._base_text}: {self._value:.1f}"

    def set_value(self, new_value):
        self._value = min(max(new_value, self._limits[0]), self._limits[1])
        super().set_text(self.full_text)

    def set_text(self, text):
        self._base_text = text
        super().set_text(self.full_text)

    def events(self, mouse_pos, mouse_pressed):
        super().events(mouse_pos, mouse_pressed)

        if self.hovered:
            if mouse_pressed[3]:
                self.set_value(self._value + self._step * mouse_pressed[3])
            if mouse_pressed[2]:
                self.set_value(0)

    def render(self, display):
        text_color = self.color[0]
        value_color = self.color[1]

        text_surface = self.font.render(self._base_text, True, text_color[self.hovered])
        value_surface = self.font.render(f"{self._value:.1f}", True, value_color[self.hovered])

        display.blit(text_surface, (self.left, self.top))
        display.blit(value_surface, (self.left + self.font.size(self._base_text + " ")[0], self.top))


class TimeSeries:

    def __init__(self, name):
        self.name = name
        self.time = numpy.array([], dtype=numpy.float32)
        self.data = numpy.array([], dtype=numpy.float32)

    def __bool__(self):
        return len(self.data) > 0

    def append(self, value, timestamp):
        self.data = numpy.append(self.data, value)
        self.time = numpy.append(self.time, timestamp)

    def filter(self, now, time_window):
        mask = self.time > now - time_window
        self.time = self.time[mask]
        self.data = self.data[mask]

    def scale(self, x_length, x_shift, y_length, y_shift, limits):
        x_scale = x_length / (self.time[-1] - self.time[0])
        times = (self.time - self.time[0]) * x_scale + x_shift

        if limits is None:
            min_data, max_data = numpy.min(self.data), numpy.max(self.data)
            y_scale = y_length / (max_data - min_data)
            data = y_shift - (self.data - min_data) * y_scale
        else:
            y_scale = y_length / (limits[1] - limits[0])
            data = y_shift - (self.data - limits[0]) * y_scale

        return numpy.column_stack((times, data))


class Plotter(Widget):

    def __init__(self, container, rect, color, signals, time_window, min_period=0, limits=None):
        super().__init__(container, rect, color)
        self.time_window = time_window
        self.min_period = min_period

        self.border = pygame.Rect(self.left + 20, self.top + 20, self.width - 40, self.height - 40)
        self.scaling = self.border.width, self.border.left, self.border.height, self.border.bottom

        self.limits = limits

        self.signals = {signal: TimeSeries(signal) for signal in signals}

    def filter(self, now):
        for data in self.signals.values():
            data.filter(now, self.time_window)

    def register(self, key, value, now):
        signal = self.signals[key]
        if not signal or now - self.signals[key].time[-1] >= self.min_period:
            self.signals[key].append(value, now)

    def render(self, display):
        pygame.draw.rect(display, self.color[0], self)
        pygame.draw.rect(display, self.color[1], self.border, 1)

        for index, (name, signal) in enumerate(self.signals.items()):
            if len(signal.data) > 2:
                points = signal.scale(*self.scaling, self.limits)
                pygame.draw.lines(display, self.color[index + 2], False, tuple(map(tuple, points)))