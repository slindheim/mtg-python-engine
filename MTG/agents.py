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
        if "Choose a target" in prompt_string:
            return "b 0"
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
