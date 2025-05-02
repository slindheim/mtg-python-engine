import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestDrawDiscardSpells(TestGameBase):
    def test_card_draw_spells(self):
        """Test card drawing spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Divination")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Divination', '', '',
                '__self.add_card_to_hand("Jace\'s Ingenuity")',
                '__self.mana.add(mana.Mana.BLUE, 5)',
                'p Jace\'s Ingenuity', '', '',
                '__self.tmp = True',  # Set tmp to True at the end
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_discard_spells(self):
        """Test discard spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.add_card_to_hand("Plains")',
                '__self.opponent.add_card_to_hand("Island")',
                '__self.add_card_to_hand("Mind Rot")',
                '__self.mana.add(mana.Mana.BLACK, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Mind Rot', 'op', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_mill_spells(self):
        """Test mill spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.library.clear()',
                '__[self.opponent.library.add("Plains") for _ in range(10)]',
                '__self.add_card_to_hand("Mind Sculpt")',
                '__self.mana.add(mana.Mana.BLUE, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Mind Sculpt', 'op', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
