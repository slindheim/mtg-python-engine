from MTG import game, cards
from MTG import card as card_mod
from agents.randoms import RandomAgent
from agents.heuristics import HeuristicAgent, HeuristicAgent15
from MTG.exceptions import EmptyLibraryException

from research_decks import build_mono_red_deck, build_mono_green_deck
from research_decks import build_mono_white_deck, build_mono_blue_deck

import sys
import inspect
import csv
import os
import datetime
import contextlib
from io import StringIO

# -----------------------------------------------------------
# Implement some helper functions (for stats collection)
# -----------------------------------------------------------

def make_empty_stats():
    """Per-game stats container for one agent."""
    return {
        "land_plays": 0,
        "creature_casts": 0,
        "approx_mana_spent": 0,
        "main_phase_actions": 0,
        "main_phase_passes": 0,
    }


# -----------------------------------------------------------
# Run a single game and return a stats dict for logging
# -----------------------------------------------------------


def run_one_game(game_id, agent0=None, agent1=None, test=False, debug_path=None):
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

    If test=True and debug_path is not None, all console output of this game
    will be captured and appended to the given debug file.
    """
    
    # 1) Load and parse card definitions
    cards.setup_cards()

    # 2) Build decks as lists of Card objects
    # CHANGE DECKS HERE AS NEEDED
    deck0_name, deck0 = build_mono_green_deck()
    deck1_name, deck1 = build_mono_white_deck()
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

    # grab player references BEFORE the game mutates its player list
    p0 = players[0]
    p1 = players[1]

    # add per-game stats and attach to agents
    stats0 = make_empty_stats()
    stats1 = make_empty_stats()
    agent0.stats = stats0
    agent1.stats = stats1

    p0.agent = agent0
    p1.agent = agent1

    # 5) Run the game; catch decking as a proper loss
    end_reason = "life"

    # capture console output to debug file when test=True ---
    if test and debug_path is not None:
        buffer = StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                g.run_game()
            except EmptyLibraryException:
                decking_player = g.current_player
                print(f"{decking_player.name} tried to draw from an empty library – loses by decking.")
                decking_player.lose()
                decking_player.opponent.won = True
                end_reason = "decking"
        # write captured output to debug file
        with open(debug_path, "a", encoding="utf-8") as dbg:
            dbg.write(f"=== Game {game_id} ===\n")
            dbg.write(buffer.getvalue())
            dbg.write("\n\n")
    else:
        # normal behavior: print to console

        try:
            g.run_game()
        except EmptyLibraryException:
            decking_player = g.current_player
            print(f"{decking_player.name} tried to draw from an empty library – loses by decking.")
            decking_player.lose()
            decking_player.opponent.won = True
            end_reason = "decking"

    # 6) Determine winner based on the saved p0/p1 references
    # (fix: after losing via HP reduction, player be removed from g.players)
    if p0.lost and not p1.lost:
        winner = 1      # player 1 wins
    elif p1.lost and not p0.lost:
        winner = 0      # player 0 wins
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

    # 8) Merge per-agent stats into game stats (if present)
    s0 = getattr(agent0, "stats", {})
    s1 = getattr(agent1, "stats", {})

    stats.update({
        "p0_land_plays": s0.get("land_plays", 0),
        "p0_creature_casts": s0.get("creature_casts", 0),
        "p0_approx_mana_spent": s0.get("approx_mana_spent", 0),
        "p0_main_phase_actions": s0.get("main_phase_actions", 0),
        "p0_main_phase_passes": s0.get("main_phase_passes", 0),

        "p1_land_plays": s1.get("land_plays", 0),
        "p1_creature_casts": s1.get("creature_casts", 0),
        "p1_approx_mana_spent": s1.get("approx_mana_spent", 0),
        "p1_main_phase_actions": s1.get("main_phase_actions", 0),
        "p1_main_phase_passes": s1.get("main_phase_passes", 0),
    })

    return stats

# -----------------------------------------------------------
# Run many games and write results to a CSV file
# -----------------------------------------------------------


if __name__ == "__main__":
    num_games = 20 # counter

    # Create results directory
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    # Create debug directory
    debug_dir = "debug"
    os.makedirs(debug_dir, exist_ok=True)

    # Generate timestamp first
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Filename stats format: <timestamp>_random_vs_heuristic.csv
    csv_path = os.path.join(results_dir, f"{timestamp}_random_vs_heuristic.csv")

    # Filename debug format: <timestamp>_debug.txt
    debug_path = os.path.join(debug_dir, f"{timestamp}_debug.txt")

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

        # new behavior metrics
        "p0_land_plays",
        "p0_creature_casts",
        "p0_approx_mana_spent",
        "p0_main_phase_actions",
        "p0_main_phase_passes",

        "p1_land_plays",
        "p1_creature_casts",
        "p1_approx_mana_spent",
        "p1_main_phase_actions",
        "p1_main_phase_passes",
    ]

    wins_p0 = 0
    wins_p1 = 0
    draws = 0

    # human vs human
    # run_one_game()


    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_games):
            # CHANGE AGENTS HERE AS NEEDED
            agent0 = HeuristicAgent()
            agent1 = HeuristicAgent15()  

            stats = run_one_game(
                game_id=i,
                agent0=agent0,
                agent1=agent1,
                test=True,          # debugging mode
                debug_path=debug_path
            )
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