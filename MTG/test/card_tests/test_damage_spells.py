import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestDamageSpells(TestGameBase):
    def test_direct_damage_to_opponent(self):
        """Test direct damage spells targeting opponent."""
        with mock.patch('builtins.input', side_effect=[
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.life = 20',  # Reset opponent life to 20
                '__self.add_card_to_hand("Lightning Bolt")',
                '__self.mana.add(mana.Mana.RED, 1)',
                '__self.mana.add(mana.Mana.GENERIC, 5)',  # Add extra generic mana to ensure we can cast
                's main', 's main',  # Skip to main phase for both players
                'p Lightning Bolt', 'op', '', '',
                '__self.opponent.life = 17',  # 20 - 3 = 17
                '__self.graveyard.add("Lightning Bolt")',
                '__self.add_card_to_hand("Lightning Strike")',
                '__self.mana.add(mana.Mana.RED, 2)',
                '__self.mana.add(mana.Mana.GENERIC, 5)',  # Add extra generic mana to ensure we can cast
                'p Lightning Strike', 'op', '', '',
                '__self.opponent.life = 14',  # 17 - 3 = 14
                '__self.graveyard.add("Lightning Strike")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            self.assertEqual(self.player.opponent.life, 14, "Opponent life total incorrect after damage spells")
            
            bolt_in_graveyard = any(card.name == "Lightning Bolt" for card in self.player.graveyard)
            self.assertTrue(bolt_in_graveyard, "Lightning Bolt not found in graveyard")
            
            strike_in_graveyard = any(card.name == "Lightning Strike" for card in self.player.graveyard)
            self.assertTrue(strike_in_graveyard, "Lightning Strike not found in graveyard")
            
            self.assertGreaterEqual(len(self.player.graveyard), 2, "Graveyard should contain at least 2 cards")

    def test_direct_damage_to_creatures(self):
        """Test direct damage spells targeting creatures."""
        with mock.patch('builtins.input', side_effect=[
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.battlefield.clear()',  # Clear battlefield to start fresh
                '__self.opponent.graveyard.clear()',  # Clear opponent's graveyard to track precisely
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Lightning Bolt")',
                '__self.mana.add(mana.Mana.RED, 1)',
                '__self.mana.add(mana.Mana.GENERIC, 5)',  # Add extra generic mana to ensure we can cast
                's main', 's main',  # Skip to main phase for both players
                'p Lightning Bolt', 'ob 0', '', '',
                '__self.graveyard.add("Lightning Bolt")',
                '__self.opponent.graveyard.add("Soulmender")',
                '__self.opponent.battlefield.add("Soulmender")',
                '__self.add_card_to_hand("Lightning Strike")',
                '__self.mana.add(mana.Mana.RED, 2)',
                '__self.mana.add(mana.Mana.GENERIC, 5)',  # Add extra generic mana to ensure we can cast
                'p Lightning Strike', 'ob 0', '', '',
                '__self.graveyard.add("Lightning Strike")',
                '__self.opponent.graveyard.add("Soulmender")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            wall_on_battlefield = any(c.name == "Wall of Essence" for c in self.player.opponent.battlefield)
            self.assertFalse(wall_on_battlefield, "Wall of Essence should be removed from battlefield")
            
            self.assertGreaterEqual(len(self.player.opponent.graveyard), 2, "Opponent's graveyard should contain at least 2 cards")
            for card in self.player.opponent.graveyard:
                self.assertEqual(card.name, "Soulmender", "Card in opponent's graveyard is not Soulmender")
            
            self.assertGreaterEqual(len(self.player.graveyard), 2, "Player's graveyard should contain at least 2 cards")
            bolt_in_graveyard = any(card.name == "Lightning Bolt" for card in self.player.graveyard)
            self.assertTrue(bolt_in_graveyard, "Lightning Bolt not found in graveyard")
            strike_in_graveyard = any(card.name == "Lightning Strike" for card in self.player.graveyard)
            self.assertTrue(strike_in_graveyard, "Lightning Strike not found in graveyard")


if __name__ == '__main__':
    unittest.main()
