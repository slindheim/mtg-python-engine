from MTG import game, player, cards

import sys
import inspect
from MTG import card as card_mod

from MTG.agents import RandomAgent


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
        # *["Lightning Bolt"] * 4,
        # *["Lightning Strike"] * 4,
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
        # *["Titanic Growth"] * 4,

        # Bigger creatures
        *["Charging Rhino"] * 2,
    ]
    return _cards_from_names(names)



def run_one_game(agent0=None, agent1=None, test=False):
    """
    Run a single game between two decks.

    If agent0/agent1 are None, default to RandomAgent for both.
    """
    # 1) Load and parse card definitions
    cards.setup_cards()

    # 2) Build decks as lists of Card objects
    deck0 = build_mono_red_deck()
    deck1 = build_mono_green_deck()
    decks = [deck0, deck1]

    # 3) Create Game with the decks
    g = game.Game(decks=decks, test=test)

    # 4) Attach agents to the two players
    #    Depending on how Game is implemented, this is usually either
    #    g.players or g.players_list. Check game.py if needed.
    if agent0 is None:
        agent0 = RandomAgent()
    if agent1 is None:
        agent1 = RandomAgent()

    # >>> IMPORTANT: one of these will work, the other will raise AttributeError.
    # Try the first; if Python says "Game object has no attribute 'players_list'",
    # comment that out and uncomment the second.
    try:
        g.players_list[0].agent = agent0
        g.players_list[1].agent = agent1
        players = g.players_list
    except AttributeError:
        # Fallback if Game uses a different attribute name
        g.players[0].agent = agent0
        g.players[1].agent = agent1
        players = g.players

    # 5) Run the full loop
    g.run_game()

    # figure out winner/loser
    p0, p1 = players
    if p0.lost and not p1.lost:
        return 1   # player1 wins
    elif p1.lost and not p0.lost:
        return 0   # player0 wins
    else:
        return -1  # draw / weird state



if __name__ == "__main__":
    result = run_one_game(test=True)
    print("Game result:", result)



# human vs human
# if __name__ == "__main__":
#     run_one_game()


# future implementation
# if __name__ == "__main__":
#     from MTG.agents import RandomAgent, HeuristicAgent
#     run_one_game(agent0=HeuristicAgent(), agent1=RandomAgent(), test=False)
