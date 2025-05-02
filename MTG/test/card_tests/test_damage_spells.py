import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestDamageSpells(TestGameBase):
    def test_direct_damage_to_opponent(self):
        """Test direct damage spells targeting opponent."""
        with mock.patch('builtins.input', side_effect=[
                '__self.add_card_to_hand("Lightning Bolt")',
                '__self.mana.add(mana.Mana.RED, 1)',
                's main', 's main',  # Skip to main phase for both players
                'p Lightning Bolt', 'op', '', '',
                '__self.add_card_to_hand("Lightning Strike")',
                '__self.mana.add(mana.Mana.RED, 2)',
                'p Lightning Strike', 'op', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)

    def test_direct_damage_to_creatures(self):
        """Test direct damage spells targeting creatures."""
        with mock.patch('builtins.input', side_effect=[
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Lightning Bolt")',
                '__self.mana.add(mana.Mana.RED, 1)',
                's main', 's main',  # Skip to main phase for both players
                'p Lightning Bolt', 'ob 0', '', '',
                '__self.opponent.battlefield.add("Soulmender")',  # Use another Soulmender instead of Wall
                '__self.add_card_to_hand("Lightning Strike")',
                '__self.mana.add(mana.Mana.RED, 2)',
                'p Lightning Strike', 'ob 0', '', '',
                '__self.tmp = True',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            self.assertTrue(self.player.tmp)


if __name__ == '__main__':
    unittest.main()
