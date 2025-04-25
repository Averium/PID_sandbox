import pygame
from pygame.math import Vector2 as Vector


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

    def __init__(self, container: WidgetContainer, rect, anchor, color, align="topleft"):
        super().__init__(rect)

        container.add(self)

        self.anchor = Vector(anchor)
        self.align = align
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
        super().__init__(container, (0, 0, 1, 1), anchor, color, align)

        self.font = TextWidget.LARGE_FONT if large else TextWidget.SMALL_FONT
        self.text = text
        self.set_text(text)

    def set_text(self, text):
        self.text = text
        width, height = self.font.size(text)
        self.update(0, 0, width, height)
        setattr(self, self.align, self.anchor)

    def render(self, display):
        surface = self.font.render(self.text, False, self.color)
        display.blit(surface, self)


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

        text_surface = self.font.render(self._base_text, False, text_color[self.hovered])
        value_surface = self.font.render(f"{self._value:.1f}", False, value_color[self.hovered])

        display.blit(text_surface, (self.left, self.top))
        display.blit(value_surface, (self.left + self.font.size(self._base_text + " ")[0], self.top))

