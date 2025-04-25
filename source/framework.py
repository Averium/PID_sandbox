from typing import Optional

import pygame
from pygame.math import Vector2 as Vector

from source.control import Reference, PID, Delay
from source.settings import SETTINGS, COLORS, SYSTEM
from source.system import System
from source.widgets import Tuner, WidgetContainer


class Framework:

    MS_TO_S = 0.001

    def __init__(self):
        self.display = pygame.display.set_mode((SETTINGS.WINDOW_WIDTH, SETTINGS.WINDOW_HEIGHT), SETTINGS.DISPLAY_FLAGS)
        self.clock = pygame.time.Clock()

        self.dt = 0

        self.paused = False
        self.running = False

        self.event_list = None

        self.system: Optional[System] = None
        self.reference: Optional[Reference] = None
        self.controller: Optional[PID] = None
        self.delay: Optional[Delay] = None

        self.widgets = WidgetContainer()

        self.kp_tuner = Tuner(self.widgets, (20, 20), "KP", COLORS.TUNER, 0, limits=[0, 100])
        self.ki_tuner = Tuner(self.widgets, (20, 50), "KI", COLORS.TUNER, 0, limits=[0, 100])
        self.kd_tuner = Tuner(self.widgets, (20, 80), "KD", COLORS.TUNER, 0, limits=[0, 100])
        self.delay_tuner = Tuner(self.widgets, (20, 110), "delay", COLORS.TUNER, 0, limits=[0, 1000], step=10)

        self.reset()

    def reset(self):
        self.system = System(SYSTEM.MASS, SYSTEM.DAMPING, 0)
        self.reference = Reference(self.system)
        self.controller = PID(SYSTEM.KP, SYSTEM.KI, SYSTEM.KD)
        self.delay = Delay(0)

    def start(self):
        if not self.running:
            self.running = True
            self.loop()

    def events(self):
        event_list = pygame.event.get()

        key_pressed = pygame.key.get_pressed()
        mouse_pressed = [*pygame.mouse.get_pressed(num_buttons=3), 0]
        mouse_pos = Vector(pygame.mouse.get_pos())

        if key_pressed[pygame.K_ESCAPE]:
            self.running = False

        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            self.reference.move(-2, self.dt)
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.reference.move( 2, self.dt)

        for event in event_list:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_r:
                    self.reset()
                if event.key == pygame.K_s:
                    self.reference.pos = -self.reference.pos
            if event.type == pygame.MOUSEWHEEL:
                mouse_pressed[3] = event.y

        self.widgets.events(mouse_pos, mouse_pressed)

        self.delay.delay = self.delay_tuner.value

        self.system.events(mouse_pos, mouse_pressed)
        self.reference.events(mouse_pos, mouse_pressed)

    def update(self):

        self.delay.update(pygame.time.get_ticks())

        if not self.paused:
            self.delay.add(self.controller.control(self.reference.pos, self.system.pos, self.dt))
            self.system.apply_force(self.delay.value)
            self.system.update(self.dt)
            self.controller.tune(self.kp_tuner.value, self.ki_tuner.value, self.kd_tuner.value)

    def render(self):
        self.display.fill(COLORS.BACKGROUND)

        self.reference.render(self.display)
        self.system.render(self.display)

        self.widgets.render(self.display)

        pygame.display.flip()

    def loop(self):

        while self.running:
            self.dt = self.clock.tick_busy_loop(SETTINGS.FPS) * Framework.MS_TO_S

            self.events()
            self.update()
            self.render()
