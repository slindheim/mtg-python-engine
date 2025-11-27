from MTG import gamesteps

import random


class RandomAgent:
    """
    Baseline: choose randomly among a couple of very simple commands
    that Player.get_action() already understands.
    """

    def _ensures_mana_for(self, player, card):
        """
        Very simple mana helper: add enough colored mana to pay this card's CMC.

        We ignore exact color requirements (fine in mono-color) and just dump
        CMC many mana symbols into the pool.
        """
        cost = getattr(card, "manacost", None)
        if not cost:
            return

        try:
            cmc = sum(cost.values())
        except Exception:
            return

        if cmc <= 0:
            return

        # Try to guess a color: R or G from characteristics, else generic
        color_char = "1"
        if hasattr(card, "characteristics"):
            colors = getattr(card.characteristics, "color", []) or []
            if "R" in colors:
                color_char = "R"
            elif "G" in colors:
                color_char = "G"

        mana_str = color_char * cmc   # e.g. "RRR" or "GG"
        try:
            player.mana.add_str(mana_str)
        except Exception:
            # If anything goes wrong, just skip; engine will reject if we still can't pay
            pass


    def select_action(self, player, game):
        """
        Return a command string like:
        - ""      -> pass / do nothing
        - "p 0"   -> play the first card in hand
        """

        # No cards in hand? Just pass.
        if not player.hand:
            return ""

        # 50% chance: pass (empty string = like pressing Enter)
        if random.random() < 0.5:
            return ""

        # Otherwise: pick a random card index in hand and try to play it.
        idx = random.randrange(len(player.hand))
        card = player.hand[idx]

        # Ensure we actually have enough mana in the pool to cast
        try:
            cmc = getattr(card, "manacost", None)
            if cmc:
                total = sum(cmc.values())
            else:
                total = 0
            if total > 0:
                # Again: very rough, just generic mana
                player.mana.add_str("1" * total)
        except Exception:
            pass

        return f"p {idx}"


    def select_choice(self, player, game, prompt_string):
        """
        Respond to generic prompts like "Choose a target" etc.
        Very dumb but *valid* answers for this engine.
        """

        # 1) Target selection (burn spell, pump spell, etc.)
        if "Choose a target" in prompt_string:
            # According to the engine docs, get_target_from_user_input
            # accepts things like:
            #   'b 2'  -> 2nd permanent on *your* battlefield
            # For your simple research setup, it's fine to
            # just always choose the first creature you control if any;
            # otherwise, aim at opponent player (p 1).
            #
            # NOTE: this is heuristic; it's just to avoid infinite prompts.
            creatures = player.battlefield.filter(filter_func=lambda p: p.is_creature)
            if creatures:
                return "b 0"   # first creature on *your* battlefield
            else:
                # 'p 1' should usually be opponent; if not, engine will reject
                return "p 1"

        # 2) Other prompts that ask "Which creature..." etc.
        if "Which creature" in prompt_string:
            return "0"

        if "Which cards would you like to discard" in prompt_string:
            # discard the first card
            return "0"

        # 3) Default: just press Enter (no choice)
        return ""


class HeuristicAgent:
    """
    Stage 1: simple rule-based 'novice' agent.

    Heuristics:
    - Only acts on its own main phases.
    - Plays a land if possible (one per turn).
    - Then plays the 'best' creature it approximately can afford:
        * prioritize higher converted mana cost (mana efficiency)
        * break ties by higher power, then higher toughness (threat priority)
    - Otherwise passes.
    """

    def _approx_cmc(self, card):
        """
        Approximate converted mana cost (CMC) from card.manacost,
        which is a dict of mana symbol -> count.

        This is a rough heuristic: we ignore color specifics and just
        sum all symbols.
        """
        cost = getattr(card, "manacost", None)
        if not cost:
            return 0
        try:
            return sum(cost.values())
        except Exception:
            return 0


    def _get_power_toughness(self, card):
        """
        Try to read power/toughness in a way that works both in hand
        and on the battlefield.
        """
        power = getattr(card, "power", None)
        toughness = getattr(card, "toughness", None)

        # Fallback to characteristics if needed
        if power is None and hasattr(card, "characteristics"):
            power = getattr(card.characteristics, "power", 0)
        if toughness is None and hasattr(card, "characteristics"):
            toughness = getattr(card.characteristics, "toughness", 0)

        if power is None:
            power = 0
        if toughness is None:
            toughness = 0

        return power, toughness


    def _approx_available_mana(self, player):
        """
        Very rough proxy for available mana:
        just count lands on the battlefield.

        This ignores summoning sickness on lands and doesn't model
        colors exactly, but in our mono-color, creatures-only setting
        it's a reasonable approximation for 'can I probably cast this?'.
        """
        return len(player.lands)
    

    def _ensure_mana_for(self, player, card):
        """
        Very simple mana helper: add enough colored mana to pay this card's CMC.

        We ignore exact color requirements (fine in mono-color) and just dump
        CMC many mana symbols into the pool.
        """
        cmc = self._approx_cmc(card)
        if cmc <= 0:
            return

        # Try to guess a color: R or G from characteristics, else generic
        color_char = "1"
        if hasattr(card, "characteristics"):
            colors = getattr(card.characteristics, "color", []) or []
            if "R" in colors:
                color_char = "R"
            elif "G" in colors:
                color_char = "G"

        mana_str = color_char * cmc   # e.g. "RRR" or "GG"
        try:
            player.mana.add_str(mana_str)
        except Exception:
            # If anything goes wrong, just skip; engine will reject if we still can't pay
            pass


    def select_action(self, player, game):
        """
        Decide on an action given the current game state.

        Interface is text-based: we return the same strings a human
        would type into the console, e.g. "p 3" or "".
        """

        # 0) If it's not this player's turn, or not a main phase, just pass
        if player is not game.current_player:
            return ""

        phase = game.step.phase
        if phase not in (gamesteps.Phase.PRECOMBAT_MAIN,
                         gamesteps.Phase.POSTCOMBAT_MAIN):
            return ""

        # 1) Try to play a land if we still have a land drop available
        if player.landPlayed < player.landPerTurn:
            land_indices = [
                i for i, c in enumerate(player.hand)
                if getattr(c, "is_land", False)
            ]
            if land_indices:
                # Simple policy: play the first land we see
                idx = land_indices[0]
                return f"p {idx}"

        # 2) Try to play the 'best' creature we can approximately afford
        approx_mana = self._approx_available_mana(player)

        candidate_indices = []
        for i, card in enumerate(player.hand):
            if not getattr(card, "is_creature", False):
                continue

            cmc = self._approx_cmc(card)
            # Basic affordability check: cost <= number of lands
            if cmc <= approx_mana:
                power, toughness = self._get_power_toughness(card)
                # Higher CMC first, then power, then toughness
                score = (100 * cmc) + (10 * power) + toughness
                candidate_indices.append((score, i))

        if candidate_indices:
            candidate_indices.sort(reverse=True)
            best_score, best_idx = candidate_indices[0]
            best_card = player.hand[best_idx]

            # Ensure we actually have enough mana in the pool to cast
            self._ensure_mana_for(player, best_card)

            return f"p {best_idx}"

        # 3) Nothing useful to do: pass
        return ""


    def select_choice(self, player, game, prompt_string):
        """
        Respond to generic prompts.

        In our current environment (no instants / no targeting),
        we only occasionally see discard-like prompts.
        """
        if "Which cards would you like to discard" in prompt_string:
            # Discard the 'worst' card: for now, just index 0
            return "0"

        if "Which creature" in prompt_string:
            return "0"

        # Default: no choice / press Enter
        return ""

# Heuristiken abbilden - siehe Notes 
# relativ simpel mal über Regeln
# ob ma das in einem Bauma abbilden kann
# priorität bedenken
# keine klare mini.max trennung - pass
# diese ausprobieren & nach Metriken evaluieren
# einlesen python präsente agenten die einfach implementiert werden können (Monte Carlo..)
# diese implementieren, ausprobieren & nach Metriken evaluieren
# noch nix RI, evtl Kleinigkeit nachschieben
# natürlich nicht mit den Heuristiken, die der Agent nutzt vergleichen beim Bewerten
# zwei bissl bessere als random, die gegeneinander antreten
# relative Bewertung der zwei Agenten mit Heuristiken
