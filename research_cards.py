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
        "Craw Wurm": {
        "mana_cost": "4GG",
        "color": ["G"],
        "power": 6,
        "toughness": 4,
        "text": "",                      # vanilla
        "subtype": ["Wurm"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [],
    },
        "Aven Flock": {
        "mana_cost": "4W",
        "color": ["W"],
        "power": 2,
        "toughness": 3,
        "text": (
            "Flying (This creature can't be blocked except by creatures "
            "with flying or reach.)\n"
            "{W}: Aven Flock gets +0/+1 until end of turn."
        ),
        "subtype": ["Bird", "Soldier"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Flying],
    },

    "Guardian Lions": {
        "mana_cost": "4W",
        "color": ["W"],
        "power": 1,
        "toughness": 6,
        "text": "Vigilance (Attacking doesn't cause this creature to tap.)",
        "subtype": ["Cat"],
        "types": [cardtype.CardType.CREATURE],
        # being safe here: encode vigilance in rules text only
        "abilities": [],
    },
        "Loxodon Convert": {
        "mana_cost": "3W",
        "color": ["W"],
        "power": 4,
        "toughness": 2,
        "text": "",  # vanilla
        "subtype": ["Phyrexian", "Elephant", "Soldier"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [],
    },

    "Savannah Lions": {
        "mana_cost": "W",
        "color": ["W"],
        "power": 2,
        "toughness": 1,
        "text": "",  # vanilla
        "subtype": ["Cat"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [],
    },
    
        "Snapping Drake": {
        "mana_cost": "3U",
        "color": ["U"],
        "power": 3,
        "toughness": 2,
        "text": "Flying",
        "subtype": ["Drake"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Flying],
    },

    "Harbor Serpent": {
        "mana_cost": "4UU",
        "color": ["U"],
        "power": 5,
        "toughness": 5,
        "text": (
            "Islandwalk\n"
            "Harbor Serpent can't attack unless there are five or more Islands on the battlefield."
        ),
        "subtype": ["Serpent"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Islandwalk],
    },
        "Aven Fisher": {
        "mana_cost": "3U",
        "color": ["U"],
        "power": 2,
        "toughness": 2,
        "text": (
            "Flying\n"
            "When Aven Fisher dies, draw a card."
        ),
        "subtype": ["Bird", "Soldier"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Flying],
    },
        "Wind Drake": {
        "mana_cost": "2U",
        "color": ["U"],
        "power": 2,
        "toughness": 2,
        "text": "Flying",
        "subtype": ["Drake"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [static_abilities.StaticAbilities.Flying],
    },

    "Phantom Warrior": {
        "mana_cost": "1UU",
        "color": ["U"],
        "power": 2,
        "toughness": 2,
        "text": "Phantom Warrior can't be blocked.",
        "subtype": ["Illusion", "Warrior"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [],  # unblockable is handled in rules text only
    },

        "Giant Growth": {
        "mana_cost": "G",
        "color": ["G"],
        "power": None,          # not a creature
        "toughness": None,      # not a creature
        "text": "Target creature gets +3/+3 until end of turn.",
        "subtype": [],
        "types": [cardtype.CardType.INSTANT],
        "abilities": [],
    },
        "Feral Maaka": {
        "mana_cost": "1R",
        "color": ["R"],
        "power": 2,
        "toughness": 2,
        "text": "",
        "subtype": ["Cat"],
        "types": [cardtype.CardType.CREATURE],
        "abilities": [],
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
