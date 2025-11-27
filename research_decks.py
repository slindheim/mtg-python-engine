from MTG import cards
from MTG import card as card_mod

import sys
import inspect


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

    Uses cards.name_to_id_dict to get the internal id (e.g. 'c234704'),
    then searches all loaded modules for a matching card class.
    """
    objs = []
    missing = []

    for name in names:
        card_id = cards.name_to_id_dict.get(name)
        if card_id is None:
            missing.append(f"{name} (no entry in name_to_id_dict)")
            continue

        try:
            cls = _find_card_cls(card_id)
        except KeyError as e:
            missing.append(f"{name} (id {card_id} not found as a class)")
            continue

        objs.append(cls())

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
    deck_name = "mono_red_creatures"
    names = [
        # 16 Mountains
        *["Mountain"] * 16,

        # 2-drops / small dudes
        *["Borderland Marauder"] * 4,
        *["Forge Devil"] * 2,

        # 3-drops
        *["Goblin Roughrider"] * 4,

        # 4-drops
        *["Krenko's Enforcer"] * 2,
        *["Furnace Whelp"] * 2,

        # 5-drops
        *["Thundering Giant"] * 2,

        # Burn (instants)
        # *["Lightning Bolt"] * 4,
        # *["Lightning Strike"] * 4,
    ]
    return deck_name, _cards_from_names(names)


# -------------------------------------------------------------------
# Mono-Green Midrange (big dumb creatures + one combat trick)
# -------------------------------------------------------------------
def build_mono_green_deck():
    deck_name = "mono_green_creatures"
    names = [
        # 16 Forests
        *["Forest"] * 16,

        # Vanilla creatures (we already know these exist for you)
        *["Runeclaw Bear"] * 1,
        *["Centaur Courser"] * 8,

        # Simple combat trick
        # *["Titanic Growth"] * 4,

        # Bigger creatures
        *["Charging Rhino"] * 2,
    ]
    return deck_name, _cards_from_names(names)

