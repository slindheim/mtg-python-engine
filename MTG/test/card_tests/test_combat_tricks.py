import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestCombatTricks(TestGameBase):
    def test_power_toughness_modifiers(self):
        """Test power/toughness modification spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Titanic Growth")',
                '__self.mana.add(mana.Mana.GREEN, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Titanic Growth', 'b 0', '', '',
                '__self.add_card_to_hand("Hydrosurge")',
                '__self.mana.add(mana.Mana.BLUE, 1)',
                'p Hydrosurge', 'b 0', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep'
                ]):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
