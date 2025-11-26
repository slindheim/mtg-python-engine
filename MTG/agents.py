import random


class RandomAgent:
    """
    Baseline: choose randomly among a couple of very simple commands
    that Player.get_action() already understands.
    """

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
