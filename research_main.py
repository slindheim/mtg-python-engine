from MTG import game, cards
from MTG import card as card_mod
from MTG.agents import RandomAgent
from MTG.exceptions import EmptyLibraryException

import sys
import inspect
import csv
import os
import datetime


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


# -----------------------------------------------------------
# Run a single game and return a stats dict for logging
# -----------------------------------------------------------


def run_one_game(game_id, agent0=None, agent1=None, test=False):
    """
    Run a single game between two decks.

    Returns:
        stats (dict) with keys:
          - game_id
          - agent0, agent1
          - deck0_name, deck1_name
          - winner (0 / 1 / -1)
          - end_reason ('life' / 'decking' / 'other')
          - p0_life, p1_life
          - p0_library_size, p1_library_size
          - p0_battlefield_creatures, p1_battlefield_creatures
    """
    
    # 1) Load and parse card definitions
    cards.setup_cards()

    # 2) Build decks as lists of Card objects
    deck0_name, deck0 = build_mono_red_deck()
    deck1_name, deck1 = build_mono_green_deck()
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

    # 5) Run the game; catch decking as a proper loss
    end_reason = "life"
    try:
        g.run_game()
    except EmptyLibraryException:
        decking_player = g.current_player
        print(f"{decking_player.name} tried to draw from an empty library – loses by decking.")
        decking_player.lose()
        decking_player.opponent.won = True
        end_reason = "decking"

    # 6) Work out winner/loser based on .lost flags
    p0, p1 = players
    if p0.lost and not p1.lost:
        winner = 1
    elif p1.lost and not p0.lost:
        winner = 0
    else:
        winner = -1
        if end_reason == "life":
            end_reason = "other"

    # 7) Collect final state metrics for logging
    p0_creatures = len(p0.battlefield.filter(filter_func=lambda c: c.is_creature))
    p1_creatures = len(p1.battlefield.filter(filter_func=lambda c: c.is_creature))

    stats = {
        "game_id": game_id,
        "agent0": type(agent0).__name__,
        "agent1": type(agent1).__name__,
        "deck0_name": deck0_name,
        "deck1_name": deck1_name,
        "winner": winner,
        "end_reason": end_reason,
        "p0_life": p0.life,
        "p1_life": p1.life,
        "p0_library_size": len(p0.library),
        "p1_library_size": len(p1.library),
        "p0_battlefield_creatures": p0_creatures,
        "p1_battlefield_creatures": p1_creatures,
    }

    return stats

# -----------------------------------------------------------
# Run many games and write results to a CSV file
# -----------------------------------------------------------


if __name__ == "__main__":
    num_games = 20

    # Create results directory
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(results_dir, f"random_vs_random_{timestamp}.csv")

    fieldnames = [
        "game_id",
        "agent0",
        "agent1",
        "deck0_name",
        "deck1_name",
        "winner",
        "end_reason",
        "p0_life",
        "p1_life",
        "p0_library_size",
        "p1_library_size",
        "p0_battlefield_creatures",
        "p1_battlefield_creatures",
    ]

    wins_p0 = 0
    wins_p1 = 0
    draws = 0

    # human vs human
#     run_one_game()


# future implementation
#     run_one_game(agent0=HeuristicAgent(), agent1=RandomAgent(), test=False)


    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_games):
            stats = run_one_game(game_id=i, test=False)
            writer.writerow(stats)

            # Update counters for console summary
            if stats["winner"] == 0:
                wins_p0 += 1
            elif stats["winner"] == 1:
                wins_p1 += 1
            else:
                draws += 1

            print(f"Game {i+1}/{num_games} finished with result {stats['winner']} (reason={stats['end_reason']})")

    print("\nSummary over", num_games, "games:")
    print("Player 0 wins:", wins_p0)
    print("Player 1 wins:", wins_p1)
    print("Draws/other :", draws)
    print("Results written to:", csv_path)