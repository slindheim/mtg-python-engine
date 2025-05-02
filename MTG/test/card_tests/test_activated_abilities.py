import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestActivatedAbilities(TestGameBase):
    def test_self_buff_abilities(self):
        """Test activated abilities that buff the creature."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Zof Shade")',
                '__self.mana.add(mana.Mana.BLACK, 9)',  # Add plenty of mana
                'a 0', '', '',  # Activate Zof Shade's ability (mana taken automatically)
                'a 0', '', '',  # Activate Zof Shade's ability again
                'a 0', '', '',  # Activate Zof Shade's ability a third time
                's end', 's end',  # Skip to end phase to check if effects wear off
                '__self.tmp = True',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)
            self.assertEqual(self.player.battlefield[0].power, 2)

    def test_furnace_whelp_ability(self):
        """Test Furnace Whelp's self-buff ability."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Furnace Whelp")',
                '__self.mana.add(mana.Mana.RED, 1)',
                'a 0', '', '',  # Activate Furnace Whelp's ability
                's end', 's end',  # Skip to end phase
                '__self.tmp = True',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)
            self.assertEqual(self.player.battlefield[0].power, 2)

    def test_chargeup_abilities(self):
        """Test abilities that use charge counters."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Grindclock")',
                '__self.opponent.library.clear()',
                '__[self.opponent.library.add("Plains") for _ in range(5)]',
                'a 0_0', '', '',  # Add a charge counter
                '__self.battlefield[0].untap()',  # Untap Grindclock to use its first ability again
                'a 0_0', '', '',  # Add another charge counter
                '__self.battlefield[0].untap()',  # Untap Grindclock to use its mill ability
                'a 0_1', 'op', '', '',  # Mill opponent based on counters (now 2)
                '__self.tmp = True',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_self_sacrifice_abilities(self):
        """Test activated abilities with self-sacrifice."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.add("Selfless Cathar")',
                '__self.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.mana.add(mana.Mana.WHITE, 2)',  # Need 1W for ability
                'a 0', '', '',  # Activate Selfless Cathar's ability (mana taken automatically)
                '__self.tmp = True',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
