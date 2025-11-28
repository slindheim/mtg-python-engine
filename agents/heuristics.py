from MTG import gamesteps

from agents.helpers import *

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
    def __init__(self):
        # stats will be overwritten by research_main, that's fine
        self.stats = None
        self._pending_spell_role = None

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
        
        # 3) If no creature play, consider simple spells (burn / pump / pacifism)
        #    We only do this in main phases to avoid complexity of combat tricks for now.
        opp = player.opponent

        # First: removal-style spells: Pacifism or burn as removal
        for i, card in enumerate(player.hand):
            role = classify_spell_role(card)
            if role == "pacifism":
                opp_creatures = list(opp.creatures)
                if not opp_creatures:
                    continue
                # target the largest power creature
                opp_creatures_sorted = sorted(
                    opp_creatures,
                    key=lambda c: self._get_power_toughness(c)[0],  # sort by power
                    reverse=True,
                )
                # if there is at least one creature worth pacifying, cast it
                self._pending_spell_role = "pacifism"
                if s is not None:
                    # count as "spell" for now using approx_mana_spent
                    cmc = approx_cmc(card)
                    s["approx_mana_spent"] += cmc
                self._ensure_mana_for(player, card)
                return f"p {i}"

        # Second: burn as removal or finisher (Lightning Bolt / Strike)
        for i, card in enumerate(player.hand):
            role = classify_spell_role(card)
            if role == "burn":
                # try to kill an opposing creature if possible
                opp_creatures = list(opp.creatures)
                burn_damage = 3  # both Bolt and Strike deal 3 in our pool
                killable = [
                    c for c in opp_creatures
                    if self._get_power_toughness(c)[1] <= burn_damage
                ]
                if killable or opp.life <= burn_damage:
                    self._pending_spell_role = "burn"
                    if s is not None:
                        cmc = approx_cmc(card)
                        s["approx_mana_spent"] += cmc
                    self._ensure_mana_for(player, card)
                    return f"p {i}"
                # else: hold burn spell for now (could extend later)

        # Third: pump spell (Giant/Titanic Growth) – simple usage:
        # precombat pump on our biggest creature to increase pressure.
        for i, card in enumerate(player.hand):
            role = classify_spell_role(card)
            if role == "pump":
                my_creatures = list(player.creatures)
                if not my_creatures:
                    continue
                # target our highest power creature
                my_sorted = sorted(
                    my_creatures,
                    key=lambda c: self._get_power_toughness(c)[0],
                    reverse=True,
                )
                self._pending_spell_role = "pump"
                if s is not None:
                    cmc = approx_cmc(card)
                    s["approx_mana_spent"] += cmc
                self._ensure_mana_for(player, card)
                return f"p {i}"

        # 4) Nothing useful to do: pass
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

        # 0) Handle "Choose a target" for spells we just cast
        if "choose a target" in text or "select a target" in text:
            role = getattr(self, "_pending_spell_role", None)
            opp = player.opponent

            # ---- Burn: Lightning Bolt / Lightning Strike ----
            if role == "burn":
                burn_damage = 3
                # we choose among *opponent's battlefield permanents*
                opp_battlefield = list(opp.battlefield)

                # filter creatures that are killable by 3 damage
                killable = [
                    c for c in opp_battlefield
                    if getattr(c, "is_creature", False)
                    and self._get_power_toughness(c)[1] <= burn_damage
                ]

                if killable:
                    # pick highest-power killable creature
                    killable_sorted = sorted(
                        killable,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = killable_sorted[0]
                    idx = opp_battlefield.index(target)
                    # 'ob N' = Nth permanent on opponent's battlefield
                    self._pending_spell_role = None
                    return f"ob {idx}"

                # safety fallback
                self._pending_spell_role = None
                return ""

            # ---- Pump: Giant/Titanic Growth-style effects ----
            if role == "pump":
                my_battlefield = list(player.battlefield)

                my_creatures = [
                    c for c in my_battlefield
                    if getattr(c, "is_creature", False)
                ]
                if my_creatures:
                    # buff our biggest creature
                    my_sorted = sorted(
                        my_creatures,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = my_sorted[0]
                    idx = my_battlefield.index(target)
                    # 'b N' = Nth permanent on your battlefield
                    self._pending_spell_role = None
                    return f"b {idx}"

                self._pending_spell_role = None
                return ""

            # ---- Pacifism / other auras (future) ----
            if role == "pacifism":
                opp_battlefield = list(opp.battlefield)
                opp_creatures = [
                    c for c in opp_battlefield
                    if getattr(c, "is_creature", False)
                ]
                if opp_creatures:
                    opp_sorted = sorted(
                        opp_creatures,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = opp_sorted[0]
                    idx = opp_battlefield.index(target)
                    self._pending_spell_role = None
                    return f"ob {idx}"

                self._pending_spell_role = None
                return ""

            # unknown role -> do nothing
            self._pending_spell_role = None
            return ""


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

            # easy blocking rule: only block if incoming damage >= current life
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
    

# ---------------------------------------------------------
# HeuristicAgent (Stage 1: novice heuristics)
# ---------------------------------------------------------

class HeuristicAgent15(HeuristicAgent):
    """
    Stage 1.5: improved blocking on top of Stage 1.0 HeuristicAgent.

    - Main phase: SAME as HeuristicAgent (land + best creature).
    - Attacks: SAME non-suicidal logic as HeuristicAgent.
    - Blocking:
        * If incoming damage >= current life -> block with all available creatures (baby blocking).
        * Otherwise:
            - Use blockers that can make favorable trades (kill attacker and survive).
            - Optionally add "chump" blockers when incoming damage is large.
    """

    def select_choice(self, player, game, prompt_string):
        text = prompt_string.lower()

        # ============================================================
        # 0) Handle targeting for spells (burn, pump, pacifism later)
        # ============================================================
        if "choose a target" in text or "select a target" in text:
            role = getattr(self, "_pending_spell_role", None)
            opp = player.opponent

            # ---- Burn: Lightning Bolt / Strike ----
            if role == "burn":
                burn_damage = 3
                opp_battlefield = list(opp.battlefield)

                killable = [
                    c for c in opp_battlefield
                    if getattr(c, "is_creature", False)
                    and self._get_power_toughness(c)[1] <= burn_damage
                ]
                if killable:
                    killable_sorted = sorted(
                        killable,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = killable_sorted[0]
                    idx = opp_battlefield.index(target)
                    self._pending_spell_role = None
                    return f"ob {idx}"

                self._pending_spell_role = None
                return ""

            # ---- Pump ----
            if role == "pump":
                my_battlefield = list(player.battlefield)
                my_creatures = [
                    c for c in my_battlefield
                    if getattr(c, "is_creature", False)
                ]
                if my_creatures:
                    my_sorted = sorted(
                        my_creatures,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = my_sorted[0]
                    idx = my_battlefield.index(target)
                    self._pending_spell_role = None
                    return f"b {idx}"

                self._pending_spell_role = None
                return ""

            # ---- Pacifism / aura-style removal (future) ----
            if role == "pacifism":
                opp_battlefield = list(opp.battlefield)
                opp_creatures = [
                    c for c in opp_battlefield
                    if getattr(c, "is_creature", False)
                ]
                if opp_creatures:
                    opp_sorted = sorted(
                        opp_creatures,
                        key=lambda c: self._get_power_toughness(c)[0],
                        reverse=True,
                    )
                    target = opp_sorted[0]
                    idx = opp_battlefield.index(target)
                    self._pending_spell_role = None
                    return f"ob {idx}"

                self._pending_spell_role = None
                return ""

            self._pending_spell_role = None
            return ""

        # ---------- 1) Declare attackers (reuse Stage 1.0 logic) ----------
        if "attackers" in text or ("attack" in text and "creature" in text):
            my_creatures = list(player.creatures)
            n = len(my_creatures)
            if n == 0:
                return ""

            opp = player.opponent
            opp_creatures = list(opp.creatures)

            # If opponent has no blockers -> attack with everything
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
                # if that blocker both kills us AND survives -> skip (suicidal)
                if max_opp_power >= my_t and my_p < max_opp_tough:
                    continue

                safe_attackers.append(str(idx))

            if safe_attackers:
                return " ".join(safe_attackers)

            # no attacker looks safe -> don't attack
            return ""

        # ---------- 2) Declare blockers (Stage 1.5 blocking) ----------
        if "blockers" in text or "block with" in text:
            my_creatures = list(player.creatures)
            if not my_creatures:
                return ""

            # Collect indices of available (untapped) blockers
            candidate_blockers = []
            for i, c in enumerate(my_creatures):
                status = getattr(c, "status", None)
                tapped = getattr(status, "tapped", False) if status is not None else False
                if not tapped:
                    candidate_blockers.append((i, c))

            if not candidate_blockers:
                return ""

            # Determine attacking creatures
            opp = player.opponent
            attackers = []
            for c in opp.creatures:
                status = getattr(c, "status", None)
                is_attacking = True
                if status is not None:
                    # if engine tracks this flag, use it; else assume attacking
                    is_attacking = getattr(status, "attacking", True)
                if is_attacking:
                    attackers.append(c)

            if not attackers:
                return ""

            # Estimate incoming damage
            incoming_damage = 0
            attacker_stats = []
            for a in attackers:
                ap, at = self._get_power_toughness(a)
                attacker_stats.append((ap, at))
                incoming_damage += ap

            # (A) Baby rule: if lethal, block with all available
            if incoming_damage >= player.life:
                return " ".join(str(i) for (i, c) in candidate_blockers)

            # (B) Medium blocking:
            #   - use blockers that can kill some attacker and survive
            good_blockers = set()
            for idx, b in candidate_blockers:
                bp, bt = self._get_power_toughness(b)
                for ap, at in attacker_stats:
                    # favorable trade: we kill attacker and survive
                    if bp >= at and bt > ap:
                        good_blockers.add(idx)
                        break

            chosen_blockers = set(good_blockers)

            # (C) Optional chump-blocking when damage is big
            # If incoming damage is more than half our life, we may chump with small creatures
            if incoming_damage > player.life / 2:
                for idx, b in candidate_blockers:
                    if idx in chosen_blockers:
                        continue
                    bp, bt = self._get_power_toughness(b)
                    # small / low-impact creatures as chumps
                    if bp <= 2:
                        chosen_blockers.add(idx)

            if not chosen_blockers:
                # No beneficial or necessary blocks -> no blocks
                return ""

            # Return indices of chosen blockers (engine decides assignment)
            return " ".join(str(i) for i in sorted(chosen_blockers))

        # ---------- 3) Discard prompts ----------
        if "which cards would you like to discard" in text:
            if len(player.hand) == 0:
                return ""
            return "0"

        if "which creature" in text:
            return "0"

        # ---------- 4) Default: no choice ----------
        return ""