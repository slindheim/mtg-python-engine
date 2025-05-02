import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestETBTriggers(TestGameBase):
    def test_etb_token_creators(self):
        """Test ETB token creator cards."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Coral Barrier")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Coral Barrier', '', '',
                '__self.add_card_to_hand("Blade Splicer")',
                '__self.mana.add(mana.Mana.WHITE, 3)',
                'p Blade Splicer', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_etb_card_draw(self):
        """Test ETB card draw effects."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Wall of Omens")',
                '__self.mana.add(mana.Mana.WHITE, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Wall of Omens', '', '',
                '__self.add_card_to_hand("Tireless Missionaries")',
                '__self.mana.add(mana.Mana.WHITE, 3)',
                'p Tireless Missionaries', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
