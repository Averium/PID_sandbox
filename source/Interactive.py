from abc import ABC, abstractmethod


class Interactive(ABC):

    def __init__(self):
        self.hovered = False
        self.held = False

    @abstractmethod
    def events(self, mouse_pos, mouse_pressed):
        pass
