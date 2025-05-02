import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestRemovalSpells(TestGameBase):
    def test_exile_effects(self):
        """Test exile removal spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Path to Exile")',
                '__self.mana.add(mana.Mana.WHITE, 1)',
                's main', 's main',  # Skip to main phase for both players
                'p Path to Exile', 'ob 0', '', '',
                'no',  # Don't search for a basic land
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_bounce_effects(self):
        """Test bounce removal spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Void Snare")',
                '__self.add_card_to_hand("Peel from Reality")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Void Snare', 'ob 0', '', '',
                'p Peel from Reality', 'b 0', 'ob 0', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
