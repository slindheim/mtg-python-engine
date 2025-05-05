import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana
from MTG import token
from MTG.gamesteps import Step

class TestETBTriggers(TestGameBase):
    def test_etb_token_creators(self):
        """Test ETB token creator cards."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',
                '__self.hand.clear()',
                '__self.mana.clear()',
                '__self.tmp = True',  # Initialize tmp to True
                
                '__self.token_count_before_barrier = len(self.battlefield)',
                '__self.battlefield.add("Coral Barrier")',
                
                '', '',  # Empty inputs to let the stack resolve
                
                '__self.tmp = self.tmp and any(c.name == "Coral Barrier" for c in self.battlefield)',
                '__self.squid_token = next((c for c in self.battlefield if c.is_token and "Squid" in c.name), None)',
                '__self.tmp = self.tmp and self.squid_token is not None',
                '__self.tmp = self.tmp and self.squid_token.power == 1',
                '__self.tmp = self.tmp and self.squid_token.toughness == 1',
                '__self.tmp = self.tmp and self.squid_token.has_ability("Islandwalk")',
                
                's end', 's end',
                's upkeep', 's upkeep',
                
                '__self.token_count_before_splicer = len(self.battlefield)',
                '__self.battlefield.add("Blade Splicer")',
                
                '', '',  # Empty inputs to let the stack resolve
                
                '__self.tmp = self.tmp and any(c.name == "Blade Splicer" for c in self.battlefield)',
                '__self.golem_token = next((c for c in self.battlefield if c.is_token and "Golem" in c.name), None)',
                '__self.tmp = self.tmp and self.golem_token is not None',
                '__self.tmp = self.tmp and self.golem_token.power == 3',
                '__self.tmp = self.tmp and self.golem_token.toughness == 3',
                '__self.tmp = self.tmp and self.golem_token.has_ability("First_Strike")',
                '__self.tmp = self.tmp and len(self.battlefield) == self.token_count_before_splicer + 2',
                
                's end', 's end',
                's upkeep', 's upkeep'
                ]):
            
            self.GAME.handle_turn()
            
            self.assertTrue(self.player.tmp, "ETB token creator test failed")

    def test_etb_card_draw(self):
        """Test ETB card draw effects."""
        with mock.patch('builtins.input', side_effect=[
                '__self.hand.clear()',
                '__self.battlefield.clear()',
                '__self.library.clear()',
                '__[self.library.add("Plains") for _ in range(10)]',
                '__self.initial_library_size = len(self.library)',
                '__self.initial_hand_size = len(self.hand)',
                '__self.tmp = True',  # Initialize tmp to True
                
                '__self.battlefield.add("Wall of Omens")',
                
                '', '',  # Empty inputs to let the stack resolve
                
                '__self.tmp = self.tmp and any(c.name == "Wall of Omens" for c in self.battlefield)',
                '__self.tmp = self.tmp and len(self.library) == self.initial_library_size - 1',
                '__self.tmp = self.tmp and len(self.hand) == self.initial_hand_size + 1',
                
                's end', 's end',
                's upkeep', 's upkeep',
                
                '__self.life_before_missionaries = self.life',
                '__self.battlefield.add("Tireless Missionaries")',
                
                '', '',  # Empty inputs to let the stack resolve
                
                '__self.tmp = self.tmp and any(c.name == "Tireless Missionaries" for c in self.battlefield)',
                '__self.tmp = self.tmp and self.life == self.life_before_missionaries + 3',
                
                's end', 's end',
                's upkeep', 's upkeep'
                ]):
            
            self.GAME.handle_turn()
            
            self.assertTrue(self.player.tmp, "ETB card draw and life gain test failed")


if __name__ == '__main__':
    unittest.main()
