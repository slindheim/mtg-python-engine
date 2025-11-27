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
        Random baseline agent:
        - randomly decides attackers
        - never blocks (stage 0 baseline)
        - picks random targets
        - discards random card
        """

        text = prompt_string.lower()

        # --------------------------------------------------
        # 1) Declare attackers: choose a random subset
        # --------------------------------------------------
        if "attackers" in text or ("attack" in text and "creature" in text):
            creatures = list(player.creatures)
            n = len(creatures)
            if n == 0:
                return ""

            # choose a random subset: each creature attacks with p=0.5
            chosen = []
            for i in range(n):
                if random.random() < 0.5:
                    chosen.append(str(i))

            # ensure at least *some* damage occurs occasionally:
            if not chosen and n > 0 and random.random() < 0.3:
                chosen = [str(random.randrange(n))]

            return " ".join(chosen)

        # --------------------------------------------------
        # 2) Declare blockers (baseline 0: no blocks)
        # --------------------------------------------------
        if "blockers" in text or "block with" in text:
            return ""

        # --------------------------------------------------
        # 3) Target selection (Instant, Sorcery, Buff)
        # --------------------------------------------------
        if "choose a target" in text or "select a target" in text:
            # list opponent creatures
            opp = player.opponent
            opp_creatures = opp.battlefield.filter(filter_func=lambda p: p.is_creature)

            # 50% chance target creature, 50% target opponent
            if opp_creatures and random.random() < 0.5:
                idx = random.randrange(len(opp_creatures))
                return f"b {idx}"   # "b X" = opponent battlefield X
            else:
                return "p 1"       # target opponent player

        # --------------------------------------------------
        # 4) Discard prompt → discard random card
        # --------------------------------------------------
        if "which cards would you like to discard" in text:
            if len(player.hand) == 0:
                return ""
            return str(random.randrange(len(player.hand)))

        # --------------------------------------------------
        # 5) Fallback for prompts like “Which creature…?”
        # --------------------------------------------------
        if "which creature" in text:
            if len(player.creatures) == 0:
                return ""
            return str(random.randrange(len(player.creatures)))

        # --------------------------------------------------
        # 6) Default: press Enter
        # --------------------------------------------------
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
