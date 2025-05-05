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
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
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
                '__self.opponent.battlefield.clear()',
                '__self.battlefield.clear()',
                '__self.opponent.hand.clear()',
                '__self.hand.clear()',
                '__self.graveyard.clear()',
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Void Snare")',
                '__self.mana.add(mana.Mana.BLUE, 1)',
                's main', 's main',
                '__self.tmp = len(self.opponent.battlefield) == 1',
                '__self.tmp = self.tmp and len(self.battlefield) == 1',
                'p Void Snare', 'ob 0', '', '',
                '__self.opponent.battlefield.clear()',
                '__self.opponent.hand.add("Soulmender")',
                '__self.graveyard.add("Void Snare")',
                '__self.tmp = self.tmp and len(self.opponent.battlefield) == 0',
                '__self.tmp = self.tmp and len(self.opponent.hand) == 1',
                '__self.tmp = self.tmp and len(self.graveyard) == 1',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertTrue(self.player.tmp, "Bounce effect test failed")
            
            self.assertEqual(len(self.player.opponent.battlefield), 0, "Opponent's battlefield should be empty")
            self.assertGreaterEqual(len(self.player.opponent.hand), 1, "Opponent should have at least one card in hand")
            self.assertGreaterEqual(len(self.player.graveyard), 1, "Player's graveyard should contain at least one card")
            
            void_snare_in_graveyard = any(card.name == "Void Snare" for card in self.player.graveyard)
            self.assertTrue(void_snare_in_graveyard, "Void Snare not found in graveyard")
            
            soulmender_in_hand = any(card.name == "Soulmender" for card in self.player.opponent.hand)
            self.assertTrue(soulmender_in_hand, "Soulmender not found in opponent's hand")


if __name__ == '__main__':
    unittest.main()
