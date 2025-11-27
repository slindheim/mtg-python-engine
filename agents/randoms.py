import random
from MTG import gamesteps


class RandomAgent:
    """
    Stage 0 baseline agent:

    - Only acts on its own main phases.
    - Sometimes plays a random land (if available).
    - Sometimes plays a random creature from hand, after stuffing enough mana
      into the pool so the engine will accept the cast.
    - Otherwise passes.
    - Combat / other choices handled by select_choice (random-ish attackers,
      no blocks, random discards / targets).
    """

    # ---------- helpers ----------

    def _approx_cmc(self, card):
        cost = getattr(card, "manacost", None)
        if not cost:
            return 0
        try:
            return sum(cost.values())
        except Exception:
            return 0

    def _ensure_mana_for(self, player, card):
        cmc = self._approx_cmc(card)
        if cmc <= 0:
            return

        color_char = "1"
        if hasattr(card, "characteristics"):
            colors = getattr(card.characteristics, "color", []) or []
            if colors:
                color_char = colors[0]
        if not color_char:
            color_char = "1"

        mana_str = color_char * cmc
        try:
            player.mana.add_str(mana_str)
        except Exception:
            pass


    # ---------- main action decision ----------

    def select_action(self, player, game):
        """
        Return a command string for Player.get_action(), e.g.:
        - ""      -> pass / do nothing
        - "p 3"   -> play the card at index 3 in hand
        """

        # Not our turn? pass.
        if player is not game.current_player:
            return ""

        # Only do stuff in main phases.
        phase = game.step.phase
        if phase not in (gamesteps.Phase.PRECOMBAT_MAIN,
                         gamesteps.Phase.POSTCOMBAT_MAIN):
            return ""

        # Hand empty: nothing to do.
        if not player.hand:
            return ""

        # stats handle (may not exist if not in experiment context)
        s = getattr(self, "stats", None)
        if s is not None:
            s["main_phase_actions"] += 1

        # With some probability, just do nothing (pure randomness).
        if random.random() < 0.2:
            if s is not None:
                s["main_phase_passes"] += 1
            return ""

        # 1) Sometimes play a random land, if land drop available.
        if player.landPlayed < player.landPerTurn:
            land_indices = [
                i for i, c in enumerate(player.hand)
                if getattr(c, "is_land", False)
            ]
            if land_indices and random.random() < 0.7:
                idx = random.choice(land_indices)
                if s is not None:
                    s["land_plays"] += 1
                return f"p {idx}"

        # 2) Sometimes play a random creature from hand.
        creature_indices = [
            i for i, c in enumerate(player.hand)
            if getattr(c, "is_creature", False)
        ]
        if creature_indices and random.random() < 0.8:
            idx = random.choice(creature_indices)
            card = player.hand[idx]
            if s is not None:
                cmc = self._approx_cmc(card)
                s["creature_casts"] += 1
                s["approx_mana_spent"] += cmc
            self._ensure_mana_for(player, card)
            return f"p {idx}"

    # ---------- reply to prompts ----------

    def select_choice(self, player, game, prompt_string):
        """
        Random baseline agent:
        - randomly decides attackers
        - never blocks (stage 0 baseline)
        - picks random targets
        - discards random cards
        """

        text = prompt_string.lower()

        # 1) Declare attackers: choose a random subset
        if "attackers" in text or ("attack" in text and "creature" in text):
            creatures = list(player.creatures)
            n = len(creatures)
            if n == 0:
                return ""

            chosen = []
            for i in range(n):
                if random.random() < 0.5:
                    chosen.append(str(i))

            # ensure at least some damage occasionally
            if not chosen and n > 0 and random.random() < 0.3:
                chosen = [str(random.randrange(n))]

            return " ".join(chosen)

        # 2) Declare blockers: no blocks
        if "blockers" in text or "block with" in text:
            return ""

        # 3) Target selection (for instants and ETB [Enters the Battefield] effects)
        if "choose a target" in text or "select a target" in text:
            # collect ALL creatures on the battlefield (ours + opponent's)
            my_creatures = list(player.battlefield.filter(filter_func=lambda p: p.is_creature))
            opp_creatures = list(player.opponent.battlefield.filter(filter_func=lambda p: p.is_creature))
            all_creatures = my_creatures + opp_creatures

            if all_creatures:
                # pick one at random; we assume engine maps "b i" to
                # "i-th permanent on your side of battlefield" per docs,
                # but our decks are very simple and Forge Devil can
                # always target *a* creature we control (including itself).
                #
                # To keep it simple & safe for now, just target our own
                # first creature: index 0 on our battlefield.
                return "b 0"

            # no creatures anywhere – just press Enter and let the engine handle it
            return ""

        # 4) Discard prompts → discard random hand card
        if "which cards would you like to discard" in text:
            if len(player.hand) == 0:
                return ""
            return str(random.randrange(len(player.hand)))

        # 5) Generic "which creature..." prompts
        if "which creature" in text:
            if len(player.creatures) == 0:
                return ""
            return str(random.randrange(len(player.creatures)))

        # 6) Default: press Enter
        return ""
