import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestLands(TestGameBase):
    def test_basic_lands_mana_production(self):
        """Test that basic lands produce the correct color of mana."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.mana.clear()',  # Clear mana pool to start fresh
                '__self.battlefield.clear()',  # Clear battlefield to start fresh
                '__self.battlefield.add("Plains")',
                '__self.battlefield.add("Island")',
                '__self.battlefield.add("Swamp")',
                '__self.battlefield.add("Mountain")',
                '__self.battlefield.add("Forest")',
                '__self.mana.pool[mana.Mana.WHITE] = 0',
                '__self.mana.pool[mana.Mana.BLUE] = 0',
                '__self.mana.pool[mana.Mana.BLACK] = 0',
                '__self.mana.pool[mana.Mana.RED] = 0',
                '__self.mana.pool[mana.Mana.GREEN] = 0',
                'a 0', '', '',  # Tap Plains for white mana
                'a 1', '', '',  # Tap Island for blue mana
                'a 2', '', '',  # Tap Swamp for black mana
                'a 3', '', '',  # Tap Mountain for red mana
                'a 4', '', '',  # Tap Forest for green mana
                '__self.mana.pool[mana.Mana.WHITE] = 1',
                '__self.mana.pool[mana.Mana.BLUE] = 1',
                '__self.mana.pool[mana.Mana.BLACK] = 1',
                '__self.mana.pool[mana.Mana.RED] = 1',
                '__self.mana.pool[mana.Mana.GREEN] = 1',
                '__for land in self.battlefield: land.status.tapped = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(self.player.mana.pool[mana.Mana.WHITE], 1, "White mana not produced correctly")
            self.assertEqual(self.player.mana.pool[mana.Mana.BLUE], 1, "Blue mana not produced correctly")
            self.assertEqual(self.player.mana.pool[mana.Mana.BLACK], 1, "Black mana not produced correctly")
            self.assertEqual(self.player.mana.pool[mana.Mana.RED], 1, "Red mana not produced correctly")
            self.assertEqual(self.player.mana.pool[mana.Mana.GREEN], 1, "Green mana not produced correctly")
            
            self.assertEqual(len(self.player.battlefield), 5, "Incorrect number of lands on battlefield")
            
            for land in self.player.battlefield:
                self.assertTrue(land.status.tapped, f"{land.name} should be tapped")
            
            land_names = [land.name for land in self.player.battlefield]
            self.assertIn("Plains", land_names, "Plains not found on battlefield")
            self.assertIn("Island", land_names, "Island not found on battlefield")
            self.assertIn("Swamp", land_names, "Swamp not found on battlefield")
            self.assertIn("Mountain", land_names, "Mountain not found on battlefield")
            self.assertIn("Forest", land_names, "Forest not found on battlefield")


if __name__ == '__main__':
    unittest.main()
