from typing import Optional

import pygame

from source.control import Reference, PID
from source.system import System
from source.settings import SETTINGS, COLORS, SYSTEM


Vector = pygame.math.Vector2


class Framework:

    MS_TO_S = 0.001

    def __init__(self):
        self.display = pygame.display.set_mode((SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.dt = 0

        self.paused = False
        self.running = False

        self.event_list = None

        self.system: Optional[System] = None
        self.reference: Optional[Reference] = None
        self.controller: Optional[PID] = None

        self.reset()

    def reset(self):
        self.paused = True

        self.system = System(SYSTEM.MASS, SYSTEM.DAMPING, 0)
        self.reference = Reference(self.system)
        self.controller = PID(SYSTEM.KP, SYSTEM.KI, SYSTEM.KD)

    def start(self):
        if not self.running:
            self.running = True
            self.loop()

    def events(self):
        self.event_list = pygame.event.get()

        for event in self.event_list:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused

        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.system.events(mouse_pos, mouse_pressed)
        self.reference.events(mouse_pos, mouse_pressed)

        if key_pressed[pygame.K_ESCAPE]:
            self.running = False

        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            self.reference.move(-5, self.dt)
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.reference.move( 5, self.dt)

    def update(self):
        if not self.paused:
            control_force = self.controller.control(self.reference.pos, self.system.pos, self.dt)
            self.system.apply_force(control_force)
            self.system.update(self.dt)

    def render(self):
        self.display.fill(COLORS.BACKGROUND)

        self.reference.render(self.display)
        self.system.render(self.display)

        pygame.display.flip()

    def loop(self):

        while self.running:
            self.dt = self.clock.tick_busy_loop(SETTINGS.FPS) * Framework.MS_TO_S

            self.events()
            self.update()
            self.render()
