import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestCardCombinations(TestGameBase):
    def test_mentor_token_combo(self):
        """Test Mentor of the Meek with token generators."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Mentor of the Meek")',
                '__self.add_card_to_hand("Raise the Alarm")',
                '__self.mana.add(mana.Mana.WHITE, 5)',
                's main', 's main',  # Skip to main phase for both players
                'p Mentor of the Meek', '', '',
                'p Raise the Alarm', '', '',
                'yes',  # Pay to draw for first token
                'W',    # Pay white mana
                'yes',  # Pay to draw for second token
                'W',    # Pay white mana
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_restoration_angel_etb_combo(self):
        """Test Restoration Angel with ETB effect creatures."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Blade Splicer")',
                '__self.add_card_to_hand("Restoration Angel")',
                '__self.mana.add(mana.Mana.WHITE, 7)',
                's main', 's main',  # Skip to main phase for both players
                'p Blade Splicer', '', '',
                'p Restoration Angel', '', '',
                'yes',  # Choose to flicker
                'b 0',  # Target Blade Splicer
                '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_simple_counter(self):
        """Test simple counter spell interaction."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Cancel")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
