from typing import Optional

import pygame

from source.control import Reference, PID
from source.system import System
from source.settings import SETTINGS, COLORS, SYSTEM
from source.widgets import Widget, Tuner

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

        self.kp_tuner: Optional[Tuner] = None
        self.ki_tuner: Optional[Tuner] = None
        self.kd_tuner: Optional[Tuner] = None

        self.reset()

    def reset(self):
        self.system = System(SYSTEM.MASS, SYSTEM.DAMPING, 0)
        self.reference = Reference(self.system)
        self.controller = PID(SYSTEM.KP, SYSTEM.KI, SYSTEM.KD)

        self.kp_tuner = Tuner((20, 20), "KP", COLORS.TUNER, 0, limits=[0, 100])
        self.ki_tuner = Tuner((20, 50), "KI", COLORS.TUNER, 0, limits=[0, 100])
        self.kd_tuner = Tuner((20, 80), "KD", COLORS.TUNER, 0, limits=[0, 100])

    def start(self):
        if not self.running:
            self.running = True
            self.loop()

    def events(self):
        event_list = pygame.event.get()

        key_pressed = pygame.key.get_pressed()
        mouse_pressed = [*pygame.mouse.get_pressed(num_buttons=3), 0]
        mouse_pos = pygame.mouse.get_pos()

        if key_pressed[pygame.K_ESCAPE]:
            self.running = False

        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            self.reference.move(-5, self.dt)
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.reference.move( 5, self.dt)

        for event in event_list:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_r:
                    self.reset()
            if event.type == pygame.MOUSEWHEEL:
                mouse_pressed[3] = event.y

        self.kp_tuner.events(mouse_pos, mouse_pressed)
        self.ki_tuner.events(mouse_pos, mouse_pressed)
        self.kd_tuner.events(mouse_pos, mouse_pressed)

        self.system.events(mouse_pos, mouse_pressed)
        self.reference.events(mouse_pos, mouse_pressed)

    def update(self):
        if not self.paused:
            control_force = self.controller.control(self.reference.pos, self.system.pos, self.dt)
            self.system.apply_force(control_force)
            self.system.update(self.dt)

            self.controller.tune(self.kp_tuner.value, self.ki_tuner.value, self.kd_tuner.value)

    def render(self):
        self.display.fill(COLORS.BACKGROUND)

        self.reference.render(self.display)
        self.system.render(self.display)

        self.kp_tuner.render(self.display)
        self.ki_tuner.render(self.display)
        self.kd_tuner.render(self.display)

        pygame.display.flip()

    def loop(self):

        while self.running:
            self.dt = self.clock.tick_busy_loop(SETTINGS.FPS) * Framework.MS_TO_S

            self.events()
            self.update()
            self.render()
