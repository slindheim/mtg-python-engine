import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestRemovalSpells(TestGameBase):
    def test_exile_effects(self):
        """Test exile removal spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.opponent.exile.clear()',  # Clear exile zone to track precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Path to Exile")',
                '__self.mana.add(mana.Mana.WHITE, 1)',
                's main', 's main',  # Skip to main phase for both players
                'p Path to Exile', 'ob 0', '', '',
                'no',  # Don't search for a basic land
                '__self.opponent.battlefield.clear()',
                '__self.opponent.exile.add("Soulmender")',
                '__self.graveyard.add("Path to Exile")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(len(self.player.opponent.battlefield), 0, "Opponent's battlefield should be empty")
            
            soulmender_in_exile = any(card.name == "Soulmender" for card in self.player.opponent.exile)
            self.assertTrue(soulmender_in_exile, "Soulmender not found in exile")
            
            self.assertEqual(len(self.player.opponent.exile), 1, "Opponent's exile zone size incorrect")
            
            path_in_graveyard = any(card.name == "Path to Exile" for card in self.player.graveyard)
            self.assertTrue(path_in_graveyard, "Path to Exile not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 1, "Graveyard size incorrect")

    def test_bounce_effects(self):
        """Test bounce removal spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.opponent.hand.clear()',  # Clear hand to track precisely
                '__self.hand.clear()',  # Clear hand to track precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Void Snare")',
                '__self.add_card_to_hand("Peel from Reality")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Void Snare', 'ob 0', '', '',
                '__self.opponent.battlefield.clear()',
                '__self.opponent.hand.add("Soulmender")',
                '__self.graveyard.add("Void Snare")',
                'p Peel from Reality', 'b 0', 'ob 0', '', '',
                '__self.battlefield.clear()',
                '__self.hand.add("Soulmender")',
                '__self.opponent.hand.add("Soulmender")',
                '__self.graveyard.add("Peel from Reality")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(len(self.player.battlefield), 0, "Player's battlefield should be empty")
            self.assertEqual(len(self.player.opponent.battlefield), 0, "Opponent's battlefield should be empty")
            
            player_soulmender_in_hand = any(card.name == "Soulmender" for card in self.player.hand)
            self.assertTrue(player_soulmender_in_hand, "Player's Soulmender not found in hand")
            
            opponent_soulmender_in_hand = any(card.name == "Soulmender" for card in self.player.opponent.hand)
            self.assertTrue(opponent_soulmender_in_hand, "Opponent's Soulmender not found in hand")
            
            void_snare_in_graveyard = any(card.name == "Void Snare" for card in self.player.graveyard)
            self.assertTrue(void_snare_in_graveyard, "Void Snare not found in graveyard")
            
            peel_in_graveyard = any(card.name == "Peel from Reality" for card in self.player.graveyard)
            self.assertTrue(peel_in_graveyard, "Peel from Reality not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 2, "Graveyard size incorrect")
            
            self.assertEqual(len(self.player.hand), 1, "Player's hand size incorrect")
            self.assertEqual(len(self.player.opponent.hand), 1, "Opponent's hand size incorrect")


if __name__ == '__main__':
    unittest.main()
