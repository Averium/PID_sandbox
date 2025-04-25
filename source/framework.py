from typing import Optional

import pygame
from pygame.math import Vector2 as Vector

from source.control import Reference, PID, Delay, Actuator, Sensor
from source.settings import SETTINGS, COLORS, SYSTEM, LAYOUT
from source.system import System
from source.widgets import Tuner, WidgetContainer, Widget, TextWidget, Plotter


class Framework:

    MS_TO_S = 0.001

    def __init__(self):
        self.display = pygame.display.set_mode((LAYOUT.WINDOW_WIDTH, LAYOUT.WINDOW_HEIGHT), SETTINGS.DISPLAY_FLAGS)
        self.clock = pygame.time.Clock()

        self.dt = 0

        self.paused = False
        self.running = False

        self.event_list = None

        self.system: Optional[System] = None
        self.reference: Optional[Reference] = None
        self.controller: Optional[PID] = None
        self.actuator: Optional[Actuator] = None
        self.sensor: Optional[Sensor] = None

        self.widgets = WidgetContainer()


        Widget(self.widgets, LAYOUT.LEFT_FIELD, COLORS.FIELD)
        Widget(self.widgets, LAYOUT.RIGHT_FIELD, COLORS.FIELD)
        Widget(self.widgets, LAYOUT.BOTTOM_FIELD, COLORS.FIELD)

        TextWidget(self.widgets, LAYOUT.CONTROLLER_TEXT, "Controller", COLORS.LABEL, align="topleft")
        self.kp_tuner = Tuner(self.widgets, LAYOUT.KP_TUNER, "P gain", COLORS.TUNER, 0, limits=[0, 100], align="bottomleft")
        self.ki_tuner = Tuner(self.widgets, LAYOUT.KI_TUNER, "I gain", COLORS.TUNER, 0, limits=[0, 100], align="bottomleft")
        self.kd_tuner = Tuner(self.widgets, LAYOUT.KD_TUNER, "D gain", COLORS.TUNER, 0, limits=[0, 100], align="bottomleft")

        TextWidget(self.widgets, LAYOUT.ACTUATOR_TEXT, "Actuator", COLORS.LABEL, align="topleft")
        self.act_delay_tuner = Tuner(self.widgets, LAYOUT.ACT_DELAY, "delay [ms]", COLORS.SETTING, 0, limits=[0, 100], step=10, align="bottomleft")
        self.act_lim_tuner = Tuner(self.widgets, LAYOUT.ACT_LIMIT,   "limit [N] ", COLORS.SETTING, 0, limits=[0, 100], step=1, align="bottomleft")

        TextWidget(self.widgets, LAYOUT.SENSOR_TEXT, "Sensor", COLORS.LABEL, align="topleft")
        self.sensor_delay_tuner = Tuner(self.widgets, LAYOUT.SENSOR_DELAY, "delay [ms]", COLORS.SETTING, 0, limits=[0, 100], step=10, align="bottomleft")
        self.sensor_amplitude_tuner = Tuner(self.widgets, LAYOUT.SENSOR_NOISE,   "Noise [mm]", COLORS.SETTING, 0, limits=[0, 100], step=1, align="bottomleft")

        self.top_plotter = Plotter(self.widgets, LAYOUT.TOP_PLOT, COLORS.PLOTTER, ("Reference", "Measurement"), 5000, 0, limits=(-SYSTEM.RAIL_LENGTH/2, SYSTEM.RAIL_LENGTH/2))

        self.debug = TextWidget(self.widgets, (LAYOUT.GAP * 2, LAYOUT.GAP * 2), " ", COLORS.LABEL, align="topleft")

        self.reset()

    def reset(self):
        self.system = System(LAYOUT.SYSTEM_CENTER, SYSTEM.MASS, SYSTEM.DAMPING, 0)
        self.reference = Reference(self.system)
        self.controller = PID(SYSTEM.KP, SYSTEM.KI, SYSTEM.KD)
        self.actuator = Actuator()
        self.sensor = Sensor()

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
            self.reference.move(-3, self.dt)
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.reference.move( 3, self.dt)

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
                mouse_pressed[3] = event.y * (1 + key_pressed[pygame.K_LCTRL] * 9)

        self.widgets.events(mouse_pos, mouse_pressed)

        self.system.events(mouse_pos, mouse_pressed)
        self.reference.events(mouse_pos, mouse_pressed)

        self.actuator.delay = self.act_delay_tuner.value
        self.actuator.limit = self.act_lim_tuner.value

        self.sensor.delay = self.sensor_delay_tuner.value
        self.sensor.amplitude = self.sensor_amplitude_tuner.value

        self.controller.tune(self.kp_tuner.value, self.ki_tuner.value, self.kd_tuner.value)

    def update(self):

        now = pygame.time.get_ticks()
        self.actuator.update(now)
        self.sensor.update(now)

        if not self.paused:

            self.sensor.request(self.system.pos)

            integrator_ena = not self.actuator.saturated()
            control_signal = self.controller.control(self.reference.pos, self.sensor.value, self.dt, integrator_ena)

            self.actuator.request(control_signal)
            self.system.apply_force(self.actuator.value)
            self.system.update(self.dt)

            self.top_plotter.register("Reference", self.reference.pos, now)
            self.top_plotter.register("Measurement", self.sensor.value, now)
            self.top_plotter.filter(now)

    def render(self):
        self.display.fill(COLORS.BACKGROUND)

        self.widgets.render(self.display)

        self.reference.render(self.display)
        self.system.render(self.display)

        pygame.display.flip()

    def loop(self):

        while self.running:
            self.dt = self.clock.tick_busy_loop(SETTINGS.FPS) * Framework.MS_TO_S

            self.events()
            self.update()
            self.render()
