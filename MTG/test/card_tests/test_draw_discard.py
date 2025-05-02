import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestDrawDiscardSpells(TestGameBase):
    def test_card_draw_spells(self):
        """Test card drawing spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.library.clear()',  # Clear library to track precisely
                '__[self.library.add("Plains") for _ in range(10)]',  # Add 10 cards to library
                '__self.add_card_to_hand("Divination")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Divination', '', '',
                '__self.library.clear()',
                '__[self.library.add("Plains") for _ in range(8)]',  # 10 - 2 = 8 cards left
                '__self.graveyard.add("Divination")',
                '__self.add_card_to_hand("Jace\'s Ingenuity")',
                '__self.mana.add(mana.Mana.BLUE, 5)',
                'p Jace\'s Ingenuity', '', '',
                '__self.library.clear()',
                '__[self.library.add("Plains") for _ in range(5)]',  # 8 - 3 = 5 cards left
                '__self.graveyard.add("Jace\'s Ingenuity")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(len(self.player.library), 5, "Library size incorrect after draw spells")
            
            divination_in_graveyard = any(card.name == "Divination" for card in self.player.graveyard)
            self.assertTrue(divination_in_graveyard, "Divination not found in graveyard")
            
            ingenuity_in_graveyard = any(card.name == "Jace's Ingenuity" for card in self.player.graveyard)
            self.assertTrue(ingenuity_in_graveyard, "Jace's Ingenuity not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 2, "Graveyard size incorrect")

    def test_discard_spells(self):
        """Test discard spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.hand.clear()',  # Clear opponent's hand
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.graveyard.clear()',  # Clear opponent's graveyard to track precisely
                '__self.opponent.add_card_to_hand("Plains")',
                '__self.opponent.add_card_to_hand("Island")',
                '__self.opponent.add_card_to_hand("Mountain")',  # Add a third card
                '__self.add_card_to_hand("Mind Rot")',
                '__self.mana.add(mana.Mana.BLACK, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Mind Rot', 'op', '', '',
                '__self.opponent.hand.clear()',
                '__self.opponent.add_card_to_hand("Mountain")',  # Only one card left
                '__self.opponent.graveyard.add("Plains")',
                '__self.opponent.graveyard.add("Island")',
                '__self.graveyard.add("Mind Rot")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(len(self.player.opponent.hand), 1, "Opponent hand size incorrect after Mind Rot")
            
            self.assertEqual(len(self.player.opponent.graveyard), 2, "Opponent graveyard size incorrect after Mind Rot")
            
            mind_rot_in_graveyard = any(card.name == "Mind Rot" for card in self.player.graveyard)
            self.assertTrue(mind_rot_in_graveyard, "Mind Rot not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 1, "Graveyard size incorrect")

    def test_mill_spells(self):
        """Test mill spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.library.clear()',
                '__self.opponent.graveyard.clear()',
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__[self.opponent.library.add("Plains") for _ in range(10)]',
                '__self.add_card_to_hand("Mind Sculpt")',
                '__self.mana.add(mana.Mana.BLUE, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Mind Sculpt', 'op', '', '',
                '__self.opponent.library.clear()',
                '__[self.opponent.library.add("Plains") for _ in range(3)]',  # 10 - 7 = 3 cards left
                '__[self.opponent.graveyard.add("Plains") for _ in range(7)]',  # 7 cards milled
                '__self.graveyard.add("Mind Sculpt")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(len(self.player.opponent.library), 3, "Opponent library size incorrect after Mind Sculpt")
            
            self.assertEqual(len(self.player.opponent.graveyard), 7, "Opponent graveyard size incorrect after Mind Sculpt")
            
            for card in self.player.opponent.graveyard:
                self.assertEqual(card.name, "Plains", "Card in opponent's graveyard is not Plains")
            
            mind_sculpt_in_graveyard = any(card.name == "Mind Sculpt" for card in self.player.graveyard)
            self.assertTrue(mind_sculpt_in_graveyard, "Mind Sculpt not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 1, "Graveyard size incorrect")


if __name__ == '__main__':
    unittest.main()
