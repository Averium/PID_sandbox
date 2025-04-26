import numpy
import pygame
from pygame.math import Vector2 as Vector

from source.settings import LAYOUT
from source.widgets import Widget


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

    GAP = 16
    ARROW_UP = (Vector(0, 0), Vector(-6, 20), Vector(8, 20))
    ARROW_RIGHT = (Vector(0, 0), Vector(-20, -6), Vector(-20, 6))

    def __init__(self, container, rect, color, signals, time_window, min_period=0, limits=None):
        super().__init__(container, rect, color)
        self.time_window = time_window
        self.min_period = min_period

        self.border = self.inflate(-LAYOUT.GAP, -LAYOUT.GAP)
        self.scaling = self.border.width, self.border.left, self.border.height, self.border.bottom

        self._limits = limits

        self.signals = {signal: TimeSeries(signal) for signal in signals}

    def filter(self, now):
        for data in self.signals.values():
            data.filter(now, self.time_window)

    def register(self, key, value, now):
        signal = self.signals[key]
        if not signal or now - self.signals[key].time[-1] >= self.min_period:
            self.signals[key].append(value, now)

    def update_limits(self):
        if self._limits is None:
            high = numpy.min(numpy.min([series.data for series in self.signals.values()]))
            low = numpy.max(numpy.max([series.data for series in self.signals.values()]))
            return high, low
        else:
            return self._limits

    def draw_axes(self, display):
        pygame.draw.lines(display, self.color[1], False, (self.border.topleft, self.border.bottomleft, self.border.bottomright), 1)
        pygame.draw.polygon(display, self.color[1], tuple(point + self.border.bottomright for point in Plotter.ARROW_RIGHT))
        pygame.draw.polygon(display, self.color[1], tuple(point + self.border.topleft for point in Plotter.ARROW_UP))

    def draw_data(self, display):
        limits = self.update_limits()

        for index, signal in enumerate(self.signals.values()):
            if len(signal.data) > 2:
                points = signal.scale(*self.scaling, limits)
                pygame.draw.lines(display, self.color[3][index], False, tuple(map(tuple, points)))

                label_surface = self.font.render(f"{signal.data[-1]:.3f}", True, self.color[3][index])
                label_rect = label_surface.get_rect()
                label_rect.bottomright = points[-1]

                display.blit(label_surface, label_rect)

    def draw_legend(self, display):
        for index, name in enumerate(self.signals):
            text_surface = self.font.render(name, True, self.color[2])
            text_rect = text_surface.get_rect()

            position = self.border.left + Plotter.GAP * 1.5, self.border.top + (text_rect.height + Plotter.GAP) * index
            indicator_rect = pygame.Rect(*position, text_rect.height, text_rect.height)

            text_rect.topleft = position[0] + indicator_rect.width + Plotter.GAP, position[1]

            pygame.draw.rect(display, self.color[3][index], indicator_rect)
            display.blit(text_surface, text_rect)

    def render(self, display):

        pygame.draw.rect(display, self.color[0], self)
        self.draw_axes(display)
        self.draw_data(display)
        self.draw_legend(display)

