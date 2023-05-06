import random
from typing import Optional
import pytest
from cardio import Card, CardList, gg, GridPos, skills, Grid
from cardio.computer_strategies import Round0OnlyStrategy
from cardio.humanstrategyvnc import HumanStrategyVnC
from cardio.states_logger import StatesLogger


@pytest.fixture(autouse=True)
def common_setup(mocker, request, gg_setup):
    if "skip_common_setup" in request.keywords:
        return
    # Do not reset cards  so we can verify the effects of fights:
    mocker.patch("cardio.Deck.reset_cards")


def do_the_fight(humancards: CardList, computercard: Optional[Card]) -> StatesLogger:
    """Note that the assumption here is that `HumanStrategyVnC` will place new cards on
    the first free slot from the left, i.e., the very first human card gets placed on
    (2,0).
    """
    gg.humanplayer.deck.cards = humancards
    # Reset grid for good measure in case we run several fights in one test:
    gg.grid = Grid(4)
    cs = Round0OnlyStrategy(grid=gg.grid, cards=[(GridPos(1, 0), computercard)])
    gg.vnc = HumanStrategyVnC(grid=gg.grid, computerstrategy=cs, whichrounds=[0])
    gg.vnc.handle_fight()
    return gg.vnc.stateslogger


def test_vanilla_fight():
    hc = Card("Human Card", 3, 10, 1)
    cc = Card("Computer Card", 2, 5, 1)
    do_the_fight([hc], cc)
    assert hc.power == 3
    assert hc.health == 8
    assert cc.power == 2
    assert cc.health == 0
    assert gg.humanplayer.gems == 2
    assert gg.grid[1][0] is None


def test_vanilla_with_power_0():
    """Should fail immediately bc human has no chance to win bc all her cards are
    powerless.
    """
    hc = Card("Human Card", 0, 10, 1)
    cc = Card("Computer Card", 2, 3, 1)
    do_the_fight([hc], cc)
    assert hc.health == 10  # full health remaining
    assert cc.health == 3
    assert gg.humanplayer.lives == 0
    assert gg.grid[2][0] is hc  # card remains in grid


@pytest.mark.skip("Causes (expected) never-ending loop.")
def test_vanilla_with_power_0_and_additional_card_in_hand():
    """In contrast to  to `test_vanilla_with_power_0`, here the human has an additional
    card w power in her hand, therefore the fight should take place and the card in the
    grid suffer damage and vanish. BUT: The fight will never end bc the `HC2` never gets
    placed by this particular strategy, resulting in a never-ending loop.
    """
    hc = Card("Human Card", 0, 10, 1)
    hc2 = Card("HC2", 1, 10, 1)
    cc = Card("Computer Card", 2, 3, 1)
    do_the_fight([hc, hc2], cc)
    assert hc.health == 0  # health depleted
    assert cc.health == 3
    assert gg.humanplayer.lives == 0
    assert gg.grid[2][0] is None  # human card removed from grid


def test_vanilla_with_no_opponent():
    hc = Card("Human Card", 1, 10, 1)
    do_the_fight([hc], None)
    assert hc.health == 10


def test_instant_death():
    hc = Card("Human Card", 1, 10, 1, skills=[skills.InstantDeath])
    cc = Card("Computer Card", 2, 3, 1)
    do_the_fight([hc], cc)
    assert hc.health == 10
    assert cc.health == 0
    assert gg.grid[1][0] is None


def test_soaring():
    hc = Card("Human Card", 1, 20, 1, skills=[skills.Soaring])
    cc = Card("Computer Card", 2, 3, 1)
    do_the_fight([hc], cc)
    # 12 not 10, bc fight-over conditions are checked after each line gets activated:
    assert hc.health == 12
    assert cc.health == 3
    assert gg.grid[1][0] is cc


def test_soaring_vs_airdefense():
    hc = Card("Human Card", 1, 20, 1, skills=[skills.Soaring])
    cc = Card("Computer Card", 2, 3, 1, skills=[skills.Airdefense])
    do_the_fight([hc], cc)
    assert hc.health == 16
    assert cc.health == 0
    assert gg.grid[1][0] is None


def test_soaring_and_instantdeath_vs_airdefense():
    hc = Card("Human Card", 1, 20, 1, skills=[skills.Soaring, skills.InstantDeath])
    cc = Card("Computer Card", 2, 3, 1, skills=[skills.Airdefense])
    do_the_fight([hc], cc)
    assert hc.health == 20
    assert cc.health == 0
    assert gg.grid[1][0] is None


def test_soaring_and_instantdeath_vs_no_airdefense():
    """INSTANTDEATH should have no effect and computer card should not suffer any damage
    at all bc of SOARING.
    """
    hc = Card("Human Card", 1, 20, 1, skills=[skills.Soaring, skills.InstantDeath])
    cc = Card("Computer Card", 2, 3, 1)
    do_the_fight([hc], cc)
    # 12 not 10, bc fight-over conditions are checked after each line gets activated:
    assert hc.health == 12
    assert cc.health == 3
    assert gg.grid[1][0] is cc


def test_spines():
    hc = Card("Human Card", 2, 10, 1)
    cc = Card("Computer Card", 2, 3, 1, skills=[skills.Spines])
    do_the_fight([hc], cc)
    assert hc.health == 6
    assert cc.health == 0
    assert gg.grid[1][0] is None


def test_spines_resulting_in_both_cards_dying_simultaneously():
    hc = Card("Human Card", 1, 1, 1)
    cc = Card("Computer Card", 0, 1, 1, skills=[skills.Spines])
    do_the_fight([hc], cc)
    assert hc.health == 0
    assert cc.health == 0
    assert gg.grid[1][0] is None
    assert gg.grid[2][0] is None
    assert gg.humanplayer.lives == 0


def test_fertility():
    hc = Card("Human Card", 1, 1, 0, skills=[skills.Fertility])
    cc = Card("Computer Card", 1, 2, 1)
    do_the_fight([hc], cc)
    # The original card must be used:
    assert hc in gg.vnc.decks.used.cards
    # The copy should be in the hand deck and it should be flagged as temporary:
    non_hamsters_on_hand = [c for c in gg.vnc.decks.hand.cards if c.name != "Hamster"]
    assert len(non_hamsters_on_hand) == 1
    copy = non_hamsters_on_hand[0]
    assert copy.name == "Human Card"
    assert copy.health == 1  # Make sure the health was reset
    assert copy.skills.get_types() == [skills.Fertility]
    assert copy.is_temporary
    # The copy should _not_ be in the player's main deck, since it is a temporary card:
    assert copy not in gg.humanplayer.deck.cards


def test_shield():
    # FIXME Once we have skills that break the shield, add that as a test case.

    # With shield:
    # The human card will survive bc the shield absorbs 1 damage in each round.
    hc = Card("Human Card", 2, 4, 1, skills=[skills.Shield])
    cc = Card("Computer Card", 2, 7, 1)
    do_the_fight([hc], cc)
    assert hc.health == 1
    assert cc.health == 0
    assert gg.grid[1][0] is None
    assert gg.grid[2][0] is hc
    assert hc.skills.get(skills.Shield).turns_used == [0, 1, 2]

    # Without shield:
    # The human card will die bc it no longer has the shield and therefore takes 2
    # damage per round.
    hc = Card("Human Card", 2, 4, 1)
    cc = Card("Computer Card", 2, 7, 1)
    do_the_fight([hc], cc)
    assert hc.health == 0
    assert cc.health == 3
    assert gg.grid[1][0] is cc
    assert gg.grid[2][0] is None

    # With shield and spines:
    # The human card will die bc while the shield absorbs 1 damage in each round, the
    # spines deal another damage, which will not be absorbed.
    hc = Card("Human Card", 2, 4, 1, skills=[skills.Shield])
    cc = Card("Computer Card", 2, 7, 1, skills=[skills.Spines])
    do_the_fight([hc], cc)
    assert hc.health == 0
    assert cc.health == 3
    assert gg.grid[1][0] is cc
    assert gg.grid[2][0] is None


@pytest.mark.skip_common_setup
def test_shield_resets_state_after_fight():
    hc = Card("Human Card", 2, 4, 1, skills=[skills.Shield])
    cc = Card("Computer Card", 2, 7, 1)
    do_the_fight([hc], cc)
    assert hc.skills.get(skills.Shield).turns_used == []


@pytest.mark.skip("Causes a Shield deadlock.")
def test_shield_deadlock():
    # FIXME Will produce a deadloop. What is the approach to fix this?
    hc = Card("Procupine", 1, 2, 1, skills=[skills.Airdefense, skills.Shield])
    cc = hc.clone()
    do_the_fight([hc], cc)


def test_underdog():
    # With Underdog:
    hc = Card("Human Card", 1, 1, 1, skills=[skills.Underdog])
    cc = Card("Computer Card", 2, 2, 1)
    do_the_fight([hc], cc)
    assert hc.health == 1  # hc wins bc it gets +1 power from Underdog
    assert cc.health == 0

    # Without Underdog:
    hc = Card("Human Card", 1, 1, 1)
    cc = Card("Computer Card", 2, 2, 1)
    do_the_fight([hc], cc)
    assert hc.health == 0
    assert cc.health == 1  # cc wins bc it has more power


def test_packrat():
    # With Packrat:
    hc = Card("Human Card", 1, 1, 1, skills=[skills.Packrat])
    xc = Card("X", 1, 1, 1)
    cc = Card("Computer Card", 1, 2, 1)
    # 3 cards will get drawn at the beginning of the fight:
    log = do_the_fight([hc, hc.clone(), hc.clone(), xc], cc)
    assert "Draw: Xp1h1" in log.log.split("Starting round")[1]
    # `xc` gets drawn ealier:
    assert "Draw: Xp1h1" not in log.log.split("Starting round")[2]

    # Without Packrat:
    hc = Card("Human Card", 1, 1, 1)
    xc = Card("X", 1, 1, 1)
    cc = Card("Computer Card", 1, 2, 1)
    log = do_the_fight([hc, hc.clone(), hc.clone(), xc], cc)
    assert "Draw: Xp1h1" in log.log.split("Starting round")[1]
    assert "Draw: Xp1h1" in log.log.split("Starting round")[2]
    # `xc` gets drawn one round later:
    assert "Draw: Xp1h1" not in log.log.split("Starting round")[3]


def test_luckystrike():
    # LuckyStrike gets unlucky and kills itself:
    random.seed(0)
    hc = Card("Human Card", 10, 10, 1, skills=[skills.LuckyStrike])
    cc = Card("Computer Card", 1, 1, 1)
    do_the_fight([hc], cc)
    assert hc.health == 0  # `hc` should have died immediately

    # LuckyStrike gets lucky and kills the opponent:
    random.seed(1)
    hc = Card("Human Card", 1, 1, 1, skills=[skills.LuckyStrike])
    cc = Card("Computer Card", 10, 10, 1)
    do_the_fight([hc], cc)
    assert cc.health == 0  # `cc` should have died immediately

    # LuckyStrike gets lucky, but no opposing card:
    # (Computer will be defeated immediately bc `hc` has 3 power, which will get
    # doubled, for a power of 6.)
    random.seed(1)
    hc = Card("Human Card", 3, 1, 1, skills=[skills.LuckyStrike])
    log = do_the_fight([hc], None)
    assert hc.health == 1  # `hc` should have survived
    assert "-6 damage," in log.log.split("Starting round")[1]



# TODO Add tests that directly test the more complex classes such as Shield and
# LuckyStrike. -- Also, add this step to the checklist in skills.py