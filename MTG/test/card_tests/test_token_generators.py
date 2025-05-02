import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestTokenGenerators(TestGameBase):
    def test_token_creation_spells(self):
        """Test token creation spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Raise the Alarm")',
                '__self.mana.add(mana.Mana.WHITE, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Raise the Alarm', '', '',
                '__self.add_card_to_hand("Triplicate Spirits")',
                '__self.mana.add(mana.Mana.WHITE, 6)',
                'p Triplicate Spirits', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
