from MTG import gamesteps

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

        We ignore exact color splits and just add CMC copies of one color symbol.
        In a mono-color deck, this is usually sufficient for paying costs.
        """
        cmc = self._approx_cmc(card)
        if cmc <= 0:
            return

        # Try to infer color from card.characteristics.color
        color_char = "1"
        if hasattr(card, "characteristics"):
            colors = getattr(card.characteristics, "color", []) or []
            # colors might be a list like ['W'] or ['G', 'U']
            if colors:
                # take the first color symbol (e.g. 'W', 'G', 'R', 'U', 'B')
                color_char = colors[0]
        # Fallback: generic, if no color info is present
        if not color_char:
            color_char = "1"

        mana_str = color_char * cmc   # e.g. "WWW" or "GG"
        try:
            player.mana.add_str(mana_str)
        except Exception:
            pass

    def select_action(self, player, game):
        """
        Decide on an action given the current game state.

        Interface is text-based: we return the same strings a human
        would type into the console, e.g. "p 3" or "".
        """

        # 0) If it's not this player's turn, or not a main phase, or no hand just pass
        if player is not game.current_player:
            return ""

        phase = game.step.phase
        if phase not in (gamesteps.Phase.PRECOMBAT_MAIN,
                         gamesteps.Phase.POSTCOMBAT_MAIN):
            return ""

        if not player.hand:
            return ""

        s = getattr(self, "stats", None)
        if s is not None:
            s["main_phase_actions"] += 1

        # 1) Try to play a land if we still have a land drop available
        if player.landPlayed < player.landPerTurn:
            land_indices = [
                i for i, c in enumerate(player.hand)
                if getattr(c, "is_land", False)
            ]
            if land_indices:
                # Simple policy: play the first land we see
                idx = land_indices[0]
                if s is not None:
                    s["land_plays"] += 1
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

            if s is not None:
                cmc = self._approx_cmc(best_card)
                s["creature_casts"] += 1
                s["approx_mana_spent"] += cmc

            # ensure we actually have enough mana in the pool
            self._ensure_mana_for(player, best_card)

            return f"p {best_idx}"

        # 3) Nothing useful to do: pass
        if s is not None:
            s["main_phase_passes"] += 1
        return ""

    def select_choice(self, player, game, prompt_string):
        """
        Respond to generic prompts.

        We try to detect:
        - attacker selection prompts
        - (later) blocker / discard prompts

        For Stage 1, we keep it simple:
        - attack with all our creatures when asked about attackers
        - never block
        - basic behavior for discarding
        """
        text = prompt_string.lower()

        # 1) Declare attackers: attack with all our creatures
        # The exact wording depends on the engine, but common patterns
        # include "attackers", "attack with", "creatures that can attack".
        if "attackers" in text or ("attack" in text and "creature" in text):
            # Attack with all creatures we control (indices 0..n-1).
            n = len(player.creatures)
            if n == 0:
                return ""
            # e.g. "0 1 2 3"
            return " ".join(str(i) for i in range(n))

        # 2) Declare blockers: for now, we never block (very aggressive)
        if "blockers" in text or "block with" in text:
            return ""  # no blocks

        # 3) Discard prompts
        if "which cards would you like to discard" in text:
            # Discard the first card by index
            return "0"

        if "which creature" in text:
            return "0"

        # 4) Default: press Enter / no choice
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
