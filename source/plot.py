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

        self.limits = limits
        self.floating = limits is None

        self.plot_switches = [True for _ in signals]
        self.mouse_pos = Vector(0, 0)
        self.mouse_pressed = pygame.mouse.get_pressed()

        self.signals = {signal: TimeSeries(signal) for signal in signals}

        _, gap = self.font.size("X")
        self.indicators = [
            pygame.Rect(self.border.left + Plotter.GAP * 1.5, self.border.top + (gap + Plotter.GAP) * index, gap, gap)
            for index, name in enumerate(self.signals)
        ]

    def events(self, mouse_pos, mouse_pressed, key_pressed):
        super().events(mouse_pos, mouse_pressed, key_pressed)

        if mouse_pressed[0] and not self.mouse_pressed[0]:
            for index, indicator_rect in enumerate(self.indicators):
                if indicator_rect.collidepoint(mouse_pos):
                    self.plot_switches[index] = not self.plot_switches[index]

        self.mouse_pos = mouse_pos
        self.mouse_pressed = mouse_pressed

    def filter(self, now):
        for data in self.signals.values():
            data.filter(now, self.time_window)

    def register(self, key, value, now):
        signal = self.signals[key]
        if not signal or now - self.signals[key].time[-1] >= self.min_period:
            self.signals[key].append(value, now)

    def update_limits(self):
        if any(self.plot_switches):
            data = [series.data for index, series in enumerate(self.signals.values()) if self.plot_switches[index]]
            low = float(numpy.min(numpy.min(data)))
            high = float(numpy.max(numpy.max(data)))
            self.limits = min(low, 0), max(high, 0)
        else:
            self.limits = -1, 1

    def draw_axes(self, display):

        low, high = self.limits

        if low + high == 0:
            y = self.border.centery
        else:
            y = self.border.bottom + (0 - low) * -self.border.height / (high - low)
            y = min(max(y, self.border.top), self.border.bottom)

        x_start, x_end = (self.border.left, y), (self.border.right, y)

        pygame.draw.line(display, self.color[1], self.border.topleft, self.border.bottomleft, 1)
        pygame.draw.line(display, self.color[1], x_start, x_end, 1)
        pygame.draw.polygon(display, self.color[1], tuple(point + x_end for point in Plotter.ARROW_RIGHT))
        pygame.draw.polygon(display, self.color[1], tuple(point + self.border.topleft for point in Plotter.ARROW_UP))

    def draw_data(self, display):
        for signal_index, signal in enumerate(self.signals.values()):

            if len(signal.data) < 3 or not self.plot_switches[signal_index]:
                continue

            points = signal.scale(*self.scaling, self.limits)
            pygame.draw.lines(display, self.color[4][signal_index], False, tuple(map(tuple, points)), 2)

            label_surface = self.font.render(f"{signal.data[-1]:.3f}", True, self.color[4][signal_index])
            label_rect = label_surface.get_rect()
            label_rect.bottomright = points[-1]

            display.blit(label_surface, label_rect)

            if not self.hovered:
                continue

            min_distance = self.width * 2
            closest_index = None

            for point_index, point in enumerate(points):
                distance = self.mouse_pos.distance_to(point)
                if distance < min_distance:
                    min_distance = distance
                    closest_index = point_index

            if min_distance > 20:
                continue

            data_surface = self.font.render(f"y = {signal.data[closest_index]:.3f}", True, self.color[2])
            data_rect = data_surface.get_rect()
            data_rect.bottomleft = self.mouse_pos

            display.blit(data_surface, data_rect)


    def draw_legend(self, display):
        for index, name in enumerate(self.signals):
            text_surface = self.font.render(name, True, self.color[2])
            text_rect = text_surface.get_rect()

            indicator_rect = self.indicators[index]

            text_rect.top = indicator_rect.top
            text_rect.left = indicator_rect.left + indicator_rect.width + Plotter.GAP

            pygame.draw.rect(display, self.color[4][index], indicator_rect, 0 if self.plot_switches[index] else 1)
            display.blit(text_surface, text_rect)

    def render(self, display):

        pygame.draw.rect(display, self.color[0], self)

        if self.floating:
            self.update_limits()

        self.draw_axes(display)
        self.draw_data(display)
        self.draw_legend(display)

