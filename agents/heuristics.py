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
    Stage 1.0: simple rule-based 'novice' agent.

    - Main phase:
        * play land if possible (one per turn)
        * play best creature we can approximately afford
    - Combat:
        * attack with creatures that are not obviously suicidal into
          the opponent's best blocker (rough approximation)
        * block ONLY if not blocking would be lethal (baby blocking)

    If self.stats is present (dict), we update:
      - land_plays
      - creature_casts
      - approx_mana_spent
      - main_phase_actions
      - main_phase_passes
    """

    # ---------- helpers ----------

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
        """
        return len(player.lands)

    def _ensure_mana_for(self, player, card):
        """
        Very simple mana helper: add enough colored mana to pay this card's CMC.
        """
        cmc = approx_cmc(card)
        if cmc <= 0:
            return

        color_char = infer_mana_symbol(card)
        mana_str = color_char * cmc
        try:
            player.mana.add_str(mana_str)
        except Exception:
            pass

    # ---------- main phase decisions ----------

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

        # 1) play land if possible
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

        # 2) play best creature we can (mana-efficiency + P/T)
        approx_mana = self._approx_available_mana(player)

        candidate_indices = []
        for i, card in enumerate(player.hand):
            if not getattr(card, "is_creature", False):
                continue

            cmc = approx_cmc(card)
            # Basic affordability check: cost <= number of land
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

        # 3) nothing useful to do: pass
        if s is not None:
            s["main_phase_passes"] += 1
        return ""

    # ---------- combat & prompts ----------

    def select_choice(self, player, game, prompt_string):
        """
        Stage 1.0 combat behavior:
        - Attack:
            * if opponent has no creatures, attack with all
            * otherwise, attack only with creatures that are not
              obviously suicidal vs the opponent's best blocker
        - Block:
            * if not blocking would be lethal, block with all available creatures
            * otherwise, no blocks
        """
        text = prompt_string.lower()

        # 1) Declare attackers
        if "attackers" in text or ("attack" in text and "creature" in text):
            my_creatures = list(player.creatures)
            n = len(my_creatures)
            if n == 0:
                return ""

            opp = player.opponent
            opp_creatures = list(opp.creatures)

            # If opponent has no blockers -> full swing
            if not opp_creatures:
                return " ".join(str(i) for i in range(n))

            # Opponent's "best" blocker (worst case for us)
            opp_stats = [self._get_power_toughness(c) for c in opp_creatures]
            max_opp_power = max(p for (p, t) in opp_stats)
            max_opp_tough = max(t for (p, t) in opp_stats)

            safe_attackers = []
            for idx, c in enumerate(my_creatures):
                my_p, my_t = self._get_power_toughness(c)

                # worst case: strongest blocker blocks this attacker
                # if that blocker both kills us and survives -> skip (suicidal)
                if max_opp_power >= my_t and my_p < max_opp_tough:
                    continue
                # Otherwise, consider this attacker "acceptable":
                # it either survives, trades, or at least deals damage
                safe_attackers.append(str(idx))

            # If we found safe attackers, use them
            if safe_attackers:
                return " ".join(safe_attackers)

            # no attacker looks safe -> don't attack
            return ""

        # 2) Declare blockers (baby blocking: only vs lethal)
        if "blockers" in text or "block with" in text:
            my_creatures = list(player.creatures)
            if not my_creatures:
                return ""

            # candidates: untapped creatures
            blocker_indices = []
            for i, c in enumerate(my_creatures):
                status = getattr(c, "status", None)
                tapped = getattr(status, "tapped", False) if status is not None else False
                if not tapped:
                    blocker_indices.append(i)

            if not blocker_indices:
                return ""

            # estimate incoming damage from attacking creatures
            opp = player.opponent
            incoming_damage = 0
            for c in opp.creatures:
                status = getattr(c, "status", None)
                is_attacking = True
                if status is not None:
                    # if engine tracks this flag, use it; else assume attacking
                    is_attacking = getattr(status, "attacking", True)
                if not is_attacking:
                    continue
                power, _ = self._get_power_toughness(c)
                incoming_damage += power

            # baby rule: only block if incoming damage >= current life
            if incoming_damage >= player.life:
                # block with all available creatures (engine will assign specifics)
                return " ".join(str(i) for i in blocker_indices)

            # otherwise: no blocks
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