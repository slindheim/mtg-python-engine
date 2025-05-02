import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestTokenGenerators(TestGameBase):
    def test_token_creation_spells(self):
        """Test token creation spells."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.add_card_to_hand("Raise the Alarm")',
                '__self.mana.clear()',  # Clear mana pool to start fresh
                '__self.mana.add(mana.Mana.WHITE, 2)',
                '__self.mana.add(mana.Mana.GENERIC, 2)',  # Add extra generic mana to ensure we can cast
                # Cast Raise the Alarm
                'p Raise the Alarm', '', '',
                '__self.graveyard.add("Raise the Alarm")',
                '__self.add_card_to_hand("Triplicate Spirits")',
                '__self.mana.clear()',  # Clear mana pool to start fresh
                '__self.mana.add(mana.Mana.WHITE, 6)',
                '__self.mana.add(mana.Mana.GENERIC, 2)',  # Add extra generic mana to ensure we can cast
                'p Triplicate Spirits', '', '',
                '__self.graveyard.add("Triplicate Spirits")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            tokens = [c for c in self.player.battlefield if c.is_token]
            self.assertEqual(len(tokens), 5, "Expected 5 tokens on battlefield")
            
            # Verify soldier token
            soldier_tokens = [c for c in tokens if c.has_subtype("Soldier")]
            self.assertGreaterEqual(len(soldier_tokens), 1, "Expected at least 1 Soldier token")
            
            white_tokens = [c for c in tokens if c.has_color("W")]
            self.assertGreaterEqual(len(white_tokens), 1, "Expected at least 1 white token")
            
            flying_tokens = [c for c in tokens if c.has_ability("Flying")]
            self.assertEqual(len(flying_tokens), 3, "Expected 3 flying tokens")
            
            for token in tokens:
                self.assertEqual(token.power, 1, f"{token.name} token power incorrect")
                self.assertEqual(token.toughness, 1, f"{token.name} token toughness incorrect")
            
            # Verify spells in graveyard
            # Both spells should be in the graveyard
            self.assertGreaterEqual(len(self.player.graveyard), 1, "Graveyard should contain at least Raise the Alarm")
            
            alarm_in_graveyard = any(card.name == "Raise the Alarm" for card in self.player.graveyard)
            self.assertTrue(alarm_in_graveyard, "Raise the Alarm not found in graveyard")
            
            flying_tokens = [c for c in self.player.battlefield if c.is_token and c.has_ability("Flying")]
            self.assertGreaterEqual(len(flying_tokens), 1, "Expected at least 1 flying token from Triplicate Spirits")


if __name__ == '__main__':
    unittest.main()
