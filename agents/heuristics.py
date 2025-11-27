from MTG import gamesteps

# ---------------------------------------------------------
# Shared helper functions
# ---------------------------------------------------------

def approx_cmc(card):
    """
    Approximate converted mana cost (CMC) from card.manacost,
    which is a dict of mana symbol -> count.
    """
    cost = getattr(card, "manacost", None)
    if not cost:
        return 0
    try:
        return sum(cost.values())
    except Exception:
        return 0


def infer_mana_symbol(card):
    """
    Infer a single mana symbol for this card, based on its color.

    For mono-colored cards, this returns 'W', 'U', 'B', 'R', or 'G'.
    For colorless or missing info, falls back to '1' (generic).

    This makes our mana hack work for any mono-color deck (including blue),
    without hard-coded if/else chains.
    """
    color_char = "1"
    if hasattr(card, "characteristics"):
        colors = getattr(card.characteristics, "color", []) or []
        # colors is typically a list like ['W'], ['G'], ['U', 'R'], etc.
        if colors:
            color_char = colors[0]
    if not color_char:
        color_char = "1"
    return color_char


# ---------------------------------------------------------
# HeuristicAgent (Stage 1: novice heuristics)
# ---------------------------------------------------------

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

    If self.stats is present (dict), we update:
      - land_plays
      - creature_casts
      - approx_mana_spent
      - main_phase_actions
      - main_phase_passes
    """

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
        Rough proxy for available mana: count lands on the battlefield.

        This ignores detailed tapping rules and colors, but in our
        mono-color limited environment it's a reasonable approximation.
        """
        return len(player.lands)

    def _ensure_mana_for(self, player, card):
        """
        Very simple mana helper: add enough colored mana to pay this card's CMC.

        We ignore exact color splits and just add CMC copies of a single color
        symbol inferred from the card. In mono-color decks this is good enough.
        """
        cmc = approx_cmc(card)
        if cmc <= 0:
            return

        color_char = infer_mana_symbol(card)
        mana_str = color_char * cmc   # e.g. "WWW" or "UUU"
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

        # Not our turn? pass
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

            cmc = approx_cmc(card)
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
                cmc = approx_cmc(best_card)
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

        For Stage 1, we keep it simple:
        - attack with all our creatures when asked about attackers
        - never block
        - basic behavior for discarding
        """
        text = prompt_string.lower()

        # 1) Declare attackers: attack with all our creatures
        if "attackers" in text or ("attack" in text and "creature" in text):
            n = len(player.creatures)
            if n == 0:
                return ""
            return " ".join(str(i) for i in range(n))

        # 2) Declare blockers: for now, we never block (very aggressive)
        if "blockers" in text or "block with" in text:
            return ""

        # 3) Discard prompts
        if "which cards would you like to discard" in text:
            if len(player.hand) == 0:
                return ""
            return "0"

        if "which creature" in text:
            return "0"

        # 4) Default: press Enter / no choice
        return ""