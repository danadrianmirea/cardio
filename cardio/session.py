from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # Functional imports will happen later to prevent circular dependencies.
    from . import Grid, FightVnC, HumanPlayer


grid: Grid
vnc: FightVnC
humanplayer: HumanPlayer

# QQ: Should this rather be Game instead of session? Or should there be a Game class?


def get_starterdeck_names() -> List[str]:
    return ["Church Mouse", "Weasel", "Lynx", "Porcupine"]


def setup() -> None:
    # TODO Is setup only required for tests in the end and could be replaced by a
    # fixture in conftest?
    from . import Grid, HumanPlayer, FightVnC
    from cardio.card_blueprints import create_cards_from_blueprints

    global grid, vnc, humanplayer
    grid = Grid(4)
    vnc = FightVnC(grid, None)

    humanplayer = HumanPlayer(name="Schnuzgi", lives=1)
    humanplayer.deck.cards = create_cards_from_blueprints(get_starterdeck_names())
