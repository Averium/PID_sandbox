import pygame


pygame.font.init()
Vector = pygame.math.Vector2


class Widget(pygame.Rect):

    SMALL_FONT = pygame.font.SysFont("monospace", 20, True)
    LARGE_FONT = pygame.font.SysFont("monospace", 32, True)

    def __init__(self, anchor, text, color, large=False, align="topleft"):
        super().__init__(0, 0, 1, 1)

        self.font = Widget.LARGE_FONT if large else Widget.SMALL_FONT
        self.anchor = Vector(anchor)

        self.text = text
        self.color = color

        self.align = align

        self.set_text(text)

        self.hovered = False
        self.clicked = False
        self.held = False

        self.last_pressed = pygame.mouse.get_pressed()

    def events(self, mouse_pos, mouse_pressed):
        self.hovered = self.collidepoint(mouse_pos)
        self.clicked = self.hovered and (mouse_pressed[0] and not self.last_pressed[0])

        if self.clicked:
            self.held = True
        if not mouse_pressed[0]:
            self.held = False

        self.last_pressed = mouse_pressed

    def set_text(self, text):
        self.text = text
        width, height = self.font.size(text)
        self.update(0, 0, width, height)
        setattr(self, self.align, self.anchor)

    def render(self, display):
        surface = self.font.render(self.text, False, self.color)
        display.blit(surface, self)


class Tuner(Widget):

    def __init__(self, anchor, text, color, value, step=0.1, limits=(-1, 1), align="topleft"):
        self._value = 0
        super().__init__(anchor, text, color, align=align)

        self._limits = limits
        self._step = step
        self._base_text = text
        self.set_value(value)

    @property
    def value(self):
        return self._value

    @property
    def full_text(self):
        return f"{self._base_text}: {self._value:.2f}"

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
        surface = self.font.render(self.text, False, self.color[self.hovered]).convert()
        display.blit(surface, self)

