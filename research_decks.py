from MTG import cards
from MTG import card as card_mod

import sys
import inspect

from research_cards import SIMPLE_CARDS, SimpleCard


# -----------------------------------------------------------
# Helpers to construct card objects from names
# -----------------------------------------------------------

def _find_card_cls(card_id):
    """
    Find the class object for a given internal card id, e.g. 'c383181'.

    We search all loaded modules for an attribute with that name that is
    a subclass of card.Card.
    """
    for module in list(sys.modules.values()):
        if module is None:
            continue

        cls = getattr(module, card_id, None)
        if cls is None:
            continue

        # Make sure it's actually a card class
        try:
            if inspect.isclass(cls) and issubclass(cls, card_mod.Card):
                return cls
        except TypeError:
            # cls wasn't a class, ignore
            continue

    # If we get here, no matching class was found anywhere
    raise KeyError(f"Card class '{card_id}' not found in any loaded module.")


def _cards_from_names(names):
    """
    Convert display names (e.g. 'Lightning Bolt') into *card objects*.

    Normal path:
      - Use cards.name_to_id_dict to get the internal id (e.g. 'c234704'),
      - Find a matching card class via _find_card_cls,
      - Instantiate that class.

    Fallback path (research-only):
      - If no engine class is found, but the name exists in SIMPLE_CARDS,
        construct a SimpleCard from the spec.

    If neither path works, collect the missing names and raise KeyError.
    """
    objs = []
    missing = []

    for name in names:
        # First, try normal engine path via name_to_id_dict
        card_id = cards.name_to_id_dict.get(name)

        if card_id is not None:
            try:
                cls = _find_card_cls(card_id)
                objs.append(cls())
                continue  # done with this name
            except KeyError:
                # Engine knows the id, but no class is loaded. Fall through
                # to simple-card fallback below.
                pass

        # Second, research-only fallback: use SIMPLE_CARDS
        spec = SIMPLE_CARDS.get(name)
        if spec is not None:
            objs.append(SimpleCard(name, spec))
            continue

        # If neither engine class nor SIMPLE_CARDS spec exists, record as missing
        missing.append(f"{name} (no engine class and no SIMPLE_CARDS spec)")

    if missing:
        raise KeyError(
            "These cards could not be constructed:\n  " + "\n  ".join(missing)
        )

    return objs


# -------------------------------------------------------------------
# Tiny research pool (union of both decks)
#
# Design constraints:
# - Only simple card types: creatures / instants / sorceries
# - Keywords used: Haste, Flying (red); none in green except buff spell
# - One red instant burn, one green combat trick
# -------------------------------------------------------------------


# -----------------------------------------------------------
# MONO RED AGGRO — *only confirmed-existing cards*
# -----------------------------------------------------------
def build_mono_red_deck():
    deck_name = "mono_red_aggro"
    names = [
        # Lands
        *["Mountain"] * 20,

        # One-drops
        *["Raging Goblin"] * 4,  # Haste, simple

        # Two-drops
        *["Borderland Marauder"] * 4,
        *["Valley Dasher"] * 4,  # Haste 2/2 that must attack

        # Three-drops
        *["Goblin Roughrider"] * 4,

        # Four-drops
        *["Krenko's Enforcer"] * 2,  # Intimidate
        *["Furnace Whelp"] * 2,      # Flying, simple firebreathing

        # Five-drops (small top-end)
        *["Thundering Giant"] * 2,   # Haste 4/4

        # Burn
        # *["Lightning Bolt"] * 4,
        # *["Lightning Strike"] * 4,
    ]
    return deck_name, _cards_from_names(names)


# -------------------------------------------------------------------
# Mono-Green Midrange (big dumb creatures + one combat trick)
# -------------------------------------------------------------------
def build_mono_green_deck():
    deck_name = "mono_green_midrange"
    names = [
        # Lands
        *["Forest"] * 23,

        # Efficient creatures
        *["Runeclaw Bear"] * 4,
        *["Centaur Courser"] * 8,

        # Larger creatures
        *["Charging Rhino"] * 4,

        # Top-end
        *["Craw Wurm"] * 2,          # classic 6/4 vanilla

        # Removal / tricks
        # *["Prey Upon"] * 4,        # fight spell
        *["Giant Growth"] * 2,
    ]
    return deck_name, _cards_from_names(names)


# -------------------------------------------------------------------
# Mono-White Control-Lite (one big finisher, stabilizers, wide board creation but no tokens)
# -------------------------------------------------------------------
def build_mono_white_deck():
    deck_name = "mono_white_control"
    names = [
        *["Plains"] * 24,

        # Early blockers
        *["Savannah Lions"] * 4,
        *["Loxodon Convert"] * 4,   # vanilla 3/3 for 3

        # Flyers (defensive or offensive)
        *["Aven Flock"] * 4,        # Flying, simple pump ability

        # Midgame bodies
        *["Guardian Lions"] * 4,    # Vigilance 1/6 (simple board stabilizer)

        # Finishers
        *["Serra Angel"] * 2,       # Flying, vigilance

        # Removal
        # *["Pacifism"] * 4,
        # simple, but still aura...
        # *["Smite"] * 2,
    ]
    return deck_name, _cards_from_names(names)



# -------------------------------------------------------------------
# Mono-Blue Tempo-Light Low Complex (no looting/scry/bounce, evasive creatures + counterspell)
# -------------------------------------------------------------------
def build_mono_blue_deck():
    deck_name = "mono_blue_tempo"
    names = [
        *["Island"] * 22,

        # Evasive creatures
        *["Wind Drake"] * 4,
        *["Phantom Warrior"] * 4,    # Unblockable, simple
        *["Aven Fisher"] * 4,        # Flying

        # Larger flyers
        *["Snapping Drake"] * 4,

        # Big but simple
        *["Harbor Serpent"] * 2,     # Islandwalk, simple restriction

        # Interaction (commented)
        # *["Cancel"] * 2,
    ]
    return deck_name, _cards_from_names(names)
