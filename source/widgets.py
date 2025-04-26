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

    SMALL_FONT = pygame.font.SysFont("monospace", 22, True)
    LARGE_FONT = pygame.font.SysFont("monospace", 32, True)

    def __init__(self, container, anchor, text, color, large=False, align="topleft"):
        super().__init__(container, (0, 0, 1, 1), color)

        self.font = TextWidget.LARGE_FONT if large else TextWidget.SMALL_FONT

        self.anchor = Vector(anchor)
        self.align = align
        self.text = text
        self.set_text(text)

    def set_text(self, new_text):
        self.text = new_text
        width, height = self.font.size(new_text)
        self.update(0, 0, width, height)
        setattr(self, self.align, self.anchor)

    def render(self, display):
        surface = self.font.render(self.text, True, self.color)
        display.blit(surface, self)

    @property
    def layer(self):
        return 2


class TextPairWidget(TextWidget):

    def __init__(self, container, anchor, base_text, value_text, color, align="topleft", delimiter=": "):
        self._base_text = base_text
        self._value_text = value_text
        self._delimiter = delimiter

        super().__init__(container, anchor, self.full_text, color, align=align)

    @property
    def full_text(self):
        return f"{self._base_text}{self._delimiter}{self._value_text}"

    def set_value_text(self, new_text):
        self._value_text = new_text
        super().set_text(self.full_text)

    def set_base_text(self, new_text):
        self._base_text = new_text
        super().set_text(self.full_text)

    def render(self, display):
        text_color = self.color[0]
        value_color = self.color[1]

        text_surface = self.font.render(self._base_text + self._delimiter, True, text_color[self.hovered])
        value_surface = self.font.render(self._value_text, True, value_color[self.hovered])

        display.blit(text_surface, (self.left, self.top))
        display.blit(value_surface, (self.left + self.font.size(self._base_text + self._delimiter)[0], self.top))


class Switch(TextPairWidget):

    def __init__(self, container, anchor, text, color, state=False, align="topleft"):
        self._state = state
        super().__init__(container, anchor, text, self.state_text, color, align)

    def __bool__(self):
        return self._state

    @property
    def state_text(self):
        return "On" if self._state else "Off"

    def relay(self):
        self._state = not self._state
        self.set_value_text(self.state_text)

    def events(self, mouse_pos, mouse_pressed):
        super().events(mouse_pos, mouse_pressed)

        if self.clicked:
            self.relay()


class Tuner(TextPairWidget):

    def __init__(self, container, anchor, text, color, value, step=0.1, limits=(-1, 1), decimals=1, align="topleft"):
        self._value = 0
        super().__init__(container, anchor, text, "", color, align=align)

        self._step = step
        self._limits = limits
        self._decimals = decimals

        self.set_value(value)

    @property
    def value(self):
        return self._value

    def set_value(self, new_value):
        self._value = min(max(new_value, self._limits[0]), self._limits[1])
        self._value_text = f"{self.value:.{self._decimals}f}"
        TextWidget.set_text(self, self.full_text)

    def events(self, mouse_pos, mouse_pressed):
        super().events(mouse_pos, mouse_pressed)

        if self.hovered:
            if mouse_pressed[3]:
                self.set_value(self._value + self._step * mouse_pressed[3])
            if mouse_pressed[2]:
                self.set_value(0)


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

        if limits[0] == limits[1]:
            y_scale = 0
        else:
            y_scale = y_length / (limits[1] - limits[0])

        data = y_shift - (self.data - limits[0]) * y_scale

        return numpy.column_stack((times, data))


class Plotter(Widget):

    def __init__(self, container, rect, color, signals, time_window, min_period=0, limits=None):
        super().__init__(container, rect, color)
        self.time_window = time_window
        self.min_period = min_period

        self.border = self.inflate(-LAYOUT.GAP, -LAYOUT.GAP)
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

        if self.limits is None:
            high = numpy.min(numpy.min([series.data for series in self.signals.values()]))
            low = numpy.max(numpy.max([series.data for series in self.signals.values()]))
            limits = high, low
        else:
            limits = self.limits

        pygame.draw.rect(display, self.color[0], self)
        pygame.draw.lines(display, self.color[1], False, (self.border.topleft, self.border.bottomleft, self.border.bottomright), 1)


        for index, (name, signal) in enumerate(self.signals.items()):
            if len(signal.data) > 2:
                points = signal.scale(*self.scaling, limits)
                pygame.draw.aalines(display, self.color[index + 2], False, tuple(map(tuple, points)))