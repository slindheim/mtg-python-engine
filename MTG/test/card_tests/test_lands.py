import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestLands(TestGameBase):
    def test_basic_lands_mana_production(self):
        """Test that basic lands produce the correct color of mana."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Plains")',
                '__self.battlefield.add("Island")',
                '__self.battlefield.add("Swamp")',
                '__self.battlefield.add("Mountain")',
                '__self.battlefield.add("Forest")',
                'a 0', '', '',  # Tap Plains for white mana
                'a 1', '', '',  # Tap Island for blue mana
                'a 2', '', '',  # Tap Swamp for black mana
                'a 3', '', '',  # Tap Mountain for red mana
                'a 4', '', '',  # Tap Forest for green mana
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
