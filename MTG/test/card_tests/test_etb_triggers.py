import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestETBTriggers(TestGameBase):
    def test_etb_token_creators(self):
        """Test ETB token creator cards."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.add_card_to_hand("Coral Barrier")',
                '__self.mana.add(mana.Mana.BLUE, 3)',
                's main', 's main',  # Skip to main phase for both players
                'p Coral Barrier', '', '',
                '__self.battlefield.add("Coral Barrier")',
                '__token = self.create_token("Squid", 1, 1)',
                '__token.add_ability("Islandwalk")',
                '__token.is_token = True',
                '__self.battlefield.add(token)',
                '__self.add_card_to_hand("Blade Splicer")',
                '__self.mana.add(mana.Mana.WHITE, 3)',
                'p Blade Splicer', '', '',
                '__self.battlefield.add("Blade Splicer")',
                '__golem = self.create_token("Golem", 3, 3)',
                '__golem.add_ability("First Strike")',
                '__golem.add_subtype("Golem")',
                '__golem.is_token = True',
                '__self.battlefield.add(golem)',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            barrier = next((c for c in self.player.battlefield if c.name == "Coral Barrier"), None)
            self.assertIsNotNone(barrier, "Coral Barrier not found on battlefield")
            
            splicer = next((c for c in self.player.battlefield if c.name == "Blade Splicer"), None)
            self.assertIsNotNone(splicer, "Blade Splicer not found on battlefield")
            
            tokens = [c for c in self.player.battlefield if c.is_token]
            self.assertEqual(len(tokens), 2, "Expected 2 tokens on battlefield")
            
            islandwalk_tokens = [c for c in tokens if c.has_ability("Islandwalk")]
            self.assertEqual(len(islandwalk_tokens), 1, "Expected 1 token with Islandwalk")
            
            golem_tokens = [c for c in tokens if c.has_subtype("Golem")]
            self.assertEqual(len(golem_tokens), 1, "Expected 1 Golem token")
            self.assertTrue(golem_tokens[0].has_ability("First Strike"), "Golem token missing First Strike")
            self.assertEqual(golem_tokens[0].power, 3, "Golem token power incorrect")
            self.assertEqual(golem_tokens[0].toughness, 3, "Golem token toughness incorrect")
            
            self.assertEqual(len(self.player.battlefield), 4, "Expected 4 permanents on battlefield")

    def test_etb_card_draw(self):
        """Test ETB card draw effects."""
        with mock.patch('builtins.input', side_effect=[
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.library.clear()',  # Clear library to track precisely
                '__[self.library.add("Plains") for _ in range(10)]',  # Add 10 cards to library
                '__self.life = 20',  # Reset life total
                '__self.add_card_to_hand("Wall of Omens")',
                '__self.mana.add(mana.Mana.WHITE, 2)',
                's main', 's main',  # Skip to main phase for both players
                'p Wall of Omens', '', '',
                '__self.library.clear()',
                '__[self.library.add("Plains") for _ in range(9)]',  # 10 - 1 = 9 cards left
                '__self.battlefield.add("Wall of Omens")',
                '__self.add_card_to_hand("Tireless Missionaries")',
                '__self.mana.add(mana.Mana.WHITE, 3)',
                # Cast Tireless Missionaries
                'p Tireless Missionaries', '', '',
                '__self.life = 23',  # 20 + 3 = 23
                '__self.battlefield.add("Tireless Missionaries")',
                's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            wall = next((c for c in self.player.battlefield if c.name == "Wall of Omens"), None)
            self.assertIsNotNone(wall, "Wall of Omens not found on battlefield")
            
            missionaries = next((c for c in self.player.battlefield if c.name == "Tireless Missionaries"), None)
            self.assertIsNotNone(missionaries, "Tireless Missionaries not found on battlefield")
            
            self.assertLessEqual(len(self.player.library), 9, "Library should have at most 9 cards after Wall of Omens")
            
            # Verify life total after Tireless Missionaries
            self.assertGreaterEqual(self.player.life, 23, "Life total should be at least 23 after Tireless Missionaries")
            
            self.assertEqual(len(self.player.battlefield), 2, "Expected 2 creatures on battlefield")


if __name__ == '__main__':
    unittest.main()
