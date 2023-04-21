"""Skills

Checklist when adding a new skill:
- Implement its logic in `Card` (and elsewhere, if necessary).
- Check for possible interdependencies with other skills and address those in the code
  accordingly.
- Add tests for skill and all interdependencies.
- Does the skill add any kind of state to the card (or other cards or other parts of the
  world) that would need to be reset (e.g., in `Card.reset`)?
- Does the skill need any new view animation that needs to be implemented and called?
- Anything that needs to be saved?
"""
from dataclasses import dataclass
from enum import Enum
from typing import List

# QQ: Maybe use a subclass such as TemporarySkill to implement things like temporary
# buffs like the power buff thanks to the Leader skill.


@dataclass(frozen=True)
class SkillSpec:
    name: str
    symbol: str
    description: str


class Skill(Enum):
    INSTANTDEATH = SkillSpec(
        name="Instant Death",
        symbol="☠️",
        description="A card with Instant Death kills a card it damages in one hit. If the attack strikes the opponent directly, the skill has no effect and the attack does damage according to its power, as usual. If a card has 0 Power, it will not attack and this skill has no effect.",
    )
    FERTILITY = SkillSpec(
        name="Fertility",
        symbol="🐭",
        description="A fertile card creates a copy of itself in your hand when it is played.",
    )
    # (QQ: Maybe FERTILITY only makes sense for cards that use spirits as costs? Or that
    # cost more than 1 fire? Otherwise you can create infinite spirits with them?))
    SOARING = SkillSpec(
        name="Soaring",
        symbol="🪁",
        description="A soaring card will ignore opposing cards and strike an opponent directly.",
    )
    SPINES = SkillSpec(
        name="Spines",
        symbol="🦔",
        description="When a card with spines is struck, the striker is dealt 1 damage.",
    )
    AIRDEFENSE = SkillSpec(
        name="Air Defense",
        symbol="🚀",
        description="A card with Air Defense blocks opposing Soaring creatures.",
        # QQ: Maybe REACHHIGH instead of AIRDEFENSE? With an arm symbol? Or
        # LONGNECK/HEADHIGH/... and the girafe emojoi?
    )


SkillList = List[Skill]

# Ideas for more skills:
#
# - Healing / Regeneration 💉 -- Itself or others around it? A card with Regeneration
#   will heal 1 damage at the end of each turn.
# - Shield 🛡️ -- Blocks the first attack? Or absorbs 1 damage per attack? Or absorbs
#   the first x damage?
# - Berserk 💢 -- A card with Berserk gains increased strength when it has taken damage.
# - Underdog -- A card with Underdog gains additional strength when fighting against
#   cards with higher power.
# - Poisonous 💊 -- Opponent (player or card?) gets poisoned and loses 1 health each
#   round.
# - Radiant 🌞 -- A card with Radiant creates 1 more spirit each time it gets brought
#   into play.
# - Mixer 🔀 -- A card with Mixer swaps one random card from your hand with another one
#   from your draw deck. (Maybe also gives me an additional hamster?)
# - Persevering / Final Blow 💥 -- Hits one more time in dying.
# - Glutton 🍔 or Insatiable 🍕 -- A card with Glutton becomes 1 unit more costly each
#   time it gets brought into play.
# - Quick ⚡ -- Strikes twice. Maybe at normal time and again after the opponent
#   attacked.
# - Hoarder -- Draw another card when this card is played. # - Echolot 🔍 -- Pick a
#   specific card from the deck.
# - Summon 🤝 -- A card with Summon can bring other cards from your deck into play.
# - Leader 👑 -- A card with Leader can buff other cards.
# - Confuse 😵 -- A card with Confuse can confuse an opponent's cards, causing them to
#   attack each other.
# - Drain 💉 -- A card with Drain can steal health from an opponent's cards.
# - Blowfish 💣 -- A card with Blowfish can explode, dealing damage to opponent and its
#   2 neighbors. Or to opponent and its prep line. But then it dies.
# - Wildcard 🃏 -- In each round, gets a random skill from the list of all skills.
# - Parry -- A card with Parry has a chance to deflect an opponent's attack back at
#   them.
# - Lucky Strike 🍀 -- Either kills the opponent or deals 1 damage to itself.
# - Firefighter 🚒🧯🧑‍🚒 -- A card with Firefighter will reduce its neighbors' fire to
#   0.
# - "Allesfresser" -- can use fire _or_ spirit (or a mix) to be placed.
# - Annihilator 💔 -- Destroys a card for good. Not just for this fight but for the
#   entire game. (Only makes sense against the human player maybe?)
# - Recruit 👥 -- Recruit one of the opponent's cards that you killed at the end of the
#   fight.
# - Hotblooded -- Can be played at any time. (Doesn't really fit the basic gameplay
#   model but might be a fun "real-time" element where you either press a key in time to
#   interrupt the game flow or you missed it.)
# - Crazy -– A card with Crazy randomly attacks either the opponent's cards or the
#   player's own cards, creating unpredictable and potentially chaotic gameplay.
# - Disrupt -- A card with Disrupt can interfere with opponent card abilities, rendering
#   them useless.
# - Bless and curse or similar? -- Affect cards negatively or positively for an entire
#   run? E.g., poisoned or so, or added strength for cards left & right for longer than
#   a fight? -- That could be a way to be more strategic around building a deck. In the
#   negative cases, the player would try to get rid of a card. Or heal it?
# - Viral -- Like poisonous, but spreads?
# - Pregnant -- One-time fertility?
