from MTG import game, player, cards

import sys
import inspect
from MTG import card as card_mod


# -----------------------------------------------------------
# Load data/M15_cards.py so we can instantiate card classes
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
        *["Lightning Bolt"] * 4,
        *["Lightning Strike"] * 4,
    ]
    return _cards_from_names(names)


# -------------------------------------------------------------------
# Mono-Green Midrange (big dumb creatures + one combat trick)
# -------------------------------------------------------------------
def build_mono_green_deck():
    names = [
        # 16 Forests
        *["Forest"] * 16,

        # Vanilla creatures (we already know these exist for you)
        *["Runeclaw Bear"] * 1,
        *["Centaur Courser"] * 8,

        # Simple combat trick
        *["Titanic Growth"] * 4,

        # Bigger creatures
        *["Charging Rhino"] * 2,
    ]
    return _cards_from_names(names)



def run_one_game(agent0=None, agent1=None, test=False):
    """
    Run a single game between two decks.

    agent0 / agent1 are placeholders for future AI agents.
    Right now the engine still drives everything via Player.get_action()
    and console input, so these are not wired in yet.
    """
    # 1) Load and parse card definitions (must happen before using name_to_id_dict)
    cards.setup_cards()

    # 2) Build decks as lists of card IDs
    deck0 = build_mono_red_deck()
    deck1 = build_mono_green_deck()
    decks = [deck0, deck1]

    # 3) Create Game with the decks (see Game.__init__ in game.py)
    g = game.Game(decks=decks, test=test)

    # 4) If/when you have agents, you’ll likely attach them to players here, e.g.:
    # if agent0 is not None:
    #     g.players_list[0].agent = agent0
    # if agent1 is not None:
    #     g.players_list[1].agent = agent1

    # 5) Run the full loop (see Game.run_game in game.py)
    g.run_game()


if __name__ == "__main__":
    run_one_game(test=True)