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

    SMALL_FONT = pygame.font.SysFont("monospace", 22, True)
    LARGE_FONT = pygame.font.SysFont("monospace", 32, True)

    def __init__(self, container: WidgetContainer, rect, color):
        super().__init__(rect)

        container.add(self)

        self.font = Widget.SMALL_FONT
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

    def __init__(self, container, anchor, text, color, large=False, align="topleft"):
        super().__init__(container, (0, 0, 1, 1), color)

        self.font = Widget.LARGE_FONT if large else Widget.SMALL_FONT

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
