import random

# Ultra-minimal version (guaranteed not to crash parsing):
# class RandomAgent:
#     def select_action(self, player, game):
#         # 50% chance to do nothing
#         import random
#         if random.random() < 0.5:
#             return ""
#         # otherwise, try "p 0" and hope card 0 exists / is playable
#         return "p 0"


class RandomAgent:
    """
    Baseline: choose randomly among a small set of possible text commands
    that the existing Player.get_action() understands.
    """

    def select_action(self, player, game):
        # 1) Sometimes just pass (empty string)
        #    (assuming blank input is "do nothing / pass")
        if random.random() < 0.2:
            return ""   # you saw that 'pass' breaks; empty is safer

        # 2) Try to randomly play a card from hand
        #    Assuming player.hand is a list of Card objects
        playable_indices = []
        for i, card in enumerate(player.hand):
            if card.can_be_played(game, player):   # if such helper doesn't exist, skip this heuristic
                playable_indices.append(i)

        if playable_indices:
            idx = random.choice(playable_indices)
            # "p N" is the pattern you triggered accidentally
            return f"p {idx}"

        # 3) If nothing to play, just pass
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
