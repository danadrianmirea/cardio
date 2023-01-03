"""Using asciimatics only for rendering and doing everything else manually."""

from typing import Union, List
import sys
import copy
import time
from asciimatics.screen import Screen
from asciimatics.effects import Print, Effect
from asciimatics import particles
from asciimatics.renderers import StaticRenderer, Box
from asciimatics.paths import Path
from asciimatics.utilities import BoxTool

from cardio.tui.cards_renderer import (
    render_card_in_grid,
    clear_card_in_grid,
    render_card_at,
    clear_card_at,
)
from cardio import Card, card_blueprints, GridPos


class ExtendedBox(BoxTool):
    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        self._style = style
        if style == 7:
            self.down_right = "*"
            self.down_left = "*"
            self.up_right = "*"
            self.up_left = "*"
            self.h = "*"
            self.h_inside = "*"
            self.v = "*"
            self.v_inside = "*"
            self.v_left = "*"
            self.v_right = "*"
            self.h_up = "*"
            self.h_down = "*"
            self.cross = "*"
        else:
            super().style(style)  # FIXME This doesn't work yet


class SmallExplosionFlames(particles.ExplosionFlames):
    def _next_particle(self):
        from math import pi, sin, cos
        from random import uniform

        direction = uniform(0, 2 * pi)
        r = 0.8
        return particles.Particle(
            "#",  # or: █
            self._x + sin(direction) * r * 2.0,
            self._y + cos(direction) * r,
            sin(direction) / 2.0,
            cos(direction) / 4.0,
            [
                (Screen.COLOUR_BLACK, 0, 0),
                (Screen.COLOUR_RED, 0, 0),
                (Screen.COLOUR_RED, Screen.A_BOLD, 0),
                (Screen.COLOUR_YELLOW, Screen.A_BOLD, 0),
                (Screen.COLOUR_WHITE, Screen.A_BOLD, 0),
            ],
            5,
            self._burn,
            next_colour=self._colour,
        )


def show_explosion(screen, small: bool = False):
    if small:
        e = SmallExplosionFlames(screen, 10, 30, 22)
        loopfor = 22
    else:
        e = particles.ExplosionFlames(screen, 10, 30, 22)
        loopfor = 30
    buffer = copy.deepcopy(screen._buffer._double_buffer)
    for i in range(loopfor):
        e.update()  # No parameter here b/c ExplosionFlames are no Effects
        screen.refresh()
        screen._buffer._double_buffer = copy.deepcopy(buffer)


def shake_card(screen):
    card = card_blueprints.create_card_from_blueprint("Hamster")
    carde = render_card_in_grid(screen, card, GridPos(3, 3))
    for _ in range(4):
        show_effects(screen, carde, 0.03)
        clear_card_in_grid(screen, GridPos(3, 3))
        card2 = render_card_in_grid(screen, card, GridPos(3, 3), xoffset=-1)
        show_effects(screen, card2, 0.03)
        clear_card_in_grid(screen, GridPos(3, 3), xoffset=-1)

    show_effects(screen, carde)


def show_move():
    show_effects(screen, render_card_at(screen, card, 10, 10))
    time.sleep(1)
    p = Path()
    p.jump_to(10, 10)
    p.move_straight_to(120, 30, 20)

    clear_card_at(screen, 10, 10)
    buffer = copy.deepcopy(screen._buffer._double_buffer)

    for x, y in p._steps:
        clear_card_at(screen, x, y)
        show_effects(screen, render_card_at(screen, card, x, y), 0.03)
        clear_card_at(screen, x, y)
        screen._buffer._double_buffer = copy.deepcopy(buffer)


def flash_card(screen):
    # Flashing the border:
    # FIXME Try also w/ different colors and/or stars...
    highlight = True
    for i in range(10):
        xx = render_card_in_grid(screen, None, GridPos(3, 3), highlight=highlight)
        for e in xx:
            e.update(0)
            screen.refresh()
        time.sleep(0.05)
        highlight = not highlight


def show_shoot(screen):
    HIT = "🌟"
    buffer = copy.deepcopy(screen._buffer._double_buffer)
    show_effects(
        screen, Print(screen=screen, renderer=StaticRenderer(images=[HIT]), y=30, x=60)
    )
    p = Path()
    p.jump_to(60, 30)
    p.move_straight_to(3, 3, 40)
    for x, y in p._steps:
        screen.clear_buffer(Screen.COLOUR_WHITE, 0, 0, x=x, y=y, w=1, h=1)
        show_effects(
            screen, Print(screen=screen, renderer=StaticRenderer(images=[HIT]), y=y, x=x)
        )
        screen._buffer._double_buffer = copy.deepcopy(buffer)


def show_effects(screen, effects: Union[Effect, List[Effect]], pause: float = 0):
    if not isinstance(effects, list):
        effects = [effects]
    for e in effects:
        e.update(0)
    screen.refresh()
    if pause > 0:
        time.sleep(pause)


# --------------------

screen = Screen.open(unicode_aware=True)

card = card_blueprints.create_card_from_blueprint("Hamster")


show_effects(screen, render_card_in_grid(screen, card, GridPos(3, 4)))
show_effects(screen, render_card_in_grid(screen, card, GridPos(3, 3)))
show_effects(screen, render_card_in_grid(screen, card, GridPos(3, 2)))
show_effects(screen, render_card_in_grid(screen, card, GridPos(3, 1)))
show_effects(screen, render_card_in_grid(screen, card, GridPos(3, 0)))

show_explosion(screen, True)

time.sleep(1)

show_shoot(screen)

show_move()

flash_card(screen)

time.sleep(1)

show_explosion(screen)

time.sleep(1)
screen.close()


# FIXME:
# - Can I draw an "*" that moves from the attacker to the target?
# - Can I activate cards by moving them towards opponent and back?
# - Can I encapsulate the code better?
# - Can I remove health by blinking it first? Or just blink to whole line?
#       💓💓💓💓💓+7
