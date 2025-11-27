from MTG import card as card_mod
from MTG import gameobject
from MTG import cardtype
from MTG import static_abilities  # if needed elsewhere

import sys
import inspect

# -------------------------------------------------------------------
# Simple research-only card specs (fallback if engine has no class)
# -------------------------------------------------------------------
SIMPLE_CARDS = {
    "Raging Goblin": {
        "mana_cost": "R",
        "color": ["R"],
        "power": 1,
        "toughness": 1,
        "text": "Haste",
        "subtype": ["Goblin"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Haste],
    },
    "Valley Dasher": {
        "mana_cost": "1R",
        "color": ["R"],
        "power": 2,
        "toughness": 2,
        "text": "Haste\nValley Dasher attacks each combat if able.",
        "subtype": ["Human", "Warrior"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Haste],
    },

    # placeholder for more simple cards
}



class SimpleCard(card_mod.Card):
    """
    Generic card used only for research decks when the engine
    has a card name but no corresponding Python class.

    NOTE: We mirror the pattern used in the real card files:
    - super() is called with a single Characteristics object.
    """
    def __init__(self, name: str, spec: dict):
        # Build Characteristics like the engine cards do
        characteristics = gameobject.Characteristics(
            **{
                "name": name,
                "mana_cost": spec["mana_cost"],
                "color": spec["color"],
                "power": spec.get("power"),
                "toughness": spec.get("toughness"),
                "text": spec["text"],
                "subtype": spec.get("subtype", []),
            },
            supertype=spec.get("supertype", []),
            types=spec.get("types", []),
            abilities=spec.get("abilities", []),
        )

        # Calls engine Card.__init__ with a single Characteristics object
        super(SimpleCard, self).__init__(characteristics)
