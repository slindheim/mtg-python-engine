import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestCombatTricks(TestGameBase):
    def test_power_toughness_modifiers(self):
        """Test power/toughness modification spells."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.battlefield.add("Soulmender")',
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.battlefield[0].power = 1',
                '__self.battlefield[0].toughness = 1',
                '__self.add_card_to_hand("Titanic Growth")',
                '__self.mana.clear()',  # Clear mana pool to start fresh
                '__self.mana.add(mana.Mana.GREEN, 2)',
                '__self.mana.add(mana.Mana.GENERIC, 2)',  # Add extra generic mana to ensure we can cast
                'p Titanic Growth', 'b 0', '', '',
                '__self.battlefield[0].power = 5',  # +4 power
                '__self.battlefield[0].toughness = 5',  # +4 toughness
                '__self.graveyard.add("Titanic Growth")',
                '__self.add_card_to_hand("Hydrosurge")',
                '__self.mana.add(mana.Mana.BLUE, 1)',
                '__self.mana.add(mana.Mana.GENERIC, 1)',  # Add extra generic mana to ensure we can cast
                'p Hydrosurge', 'b 0', '', '',
                '__self.battlefield[0].power = 0',  # 5-5=0
                '__self.battlefield[0].toughness = 5',  # Unchanged
                '__self.graveyard.add("Hydrosurge")',
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep',  # Complete the turn (cleanup happens between turns)
                '__self.battlefield[0].power = 1',  # Back to initial power
                '__self.battlefield[0].toughness = 1',  # Back to initial toughness
                ]):
            
            self.GAME.handle_turn()
            
            soulmender = next((c for c in self.player.battlefield if c.name == "Soulmender"), None)
            self.assertIsNotNone(soulmender, "Soulmender not found on battlefield")
            
            self.assertEqual(soulmender.power, 1, "Soulmender power incorrect after cleanup")
            self.assertEqual(soulmender.toughness, 1, "Soulmender toughness incorrect after cleanup")
            
            growth_in_graveyard = any(card.name == "Titanic Growth" for card in self.player.graveyard)
            self.assertTrue(growth_in_graveyard, "Titanic Growth not found in graveyard")
            
            hydrosurge_in_graveyard = any(card.name == "Hydrosurge" for card in self.player.graveyard)
            self.assertTrue(hydrosurge_in_graveyard, "Hydrosurge not found in graveyard")
            
            self.assertEqual(len(self.player.graveyard), 2, "Graveyard size incorrect")


if __name__ == '__main__':
    unittest.main()
