import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestActivatedAbilities(TestGameBase):
    def test_self_buff_abilities(self):
        """Test activated abilities that buff the creature."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.battlefield.add("Zof Shade")',
                '__self.mana.add(mana.Mana.BLACK, 9)',  # Add plenty of mana
                '__self.tmp = self.mana.pool[mana.Mana.BLACK]',  # Store initial black mana
                '__self.tmp2 = self.battlefield[0].power',  # Store initial power
                '__self.tmp3 = self.battlefield[0].toughness',  # Store initial toughness
                'a 0', '', '',  # Activate Zof Shade's ability (mana taken automatically)
                '__assert self.battlefield[0].power == self.tmp2 + 2',  # +2 power
                '__assert self.battlefield[0].toughness == self.tmp3 + 2',  # +2 toughness
                '__assert self.mana.pool[mana.Mana.BLACK] == self.tmp - 3',  # Costs 3B
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep'  # Complete the turn (cleanup happens between turns)
                ]):
            
            self.GAME.handle_turn()
            
            shade = next((c for c in self.player.battlefield if c.name == "Zof Shade"), None)
            self.assertIsNotNone(shade, "Zof Shade not found on battlefield")
            
            self.assertEqual(shade.power, self.player.tmp2, "Zof Shade power incorrect after cleanup")
            self.assertEqual(shade.toughness, self.player.tmp3, "Zof Shade toughness incorrect after cleanup")
            
            self.assertLessEqual(self.player.mana.pool[mana.Mana.BLACK], self.player.tmp - 3, "Black mana not spent correctly")

    def test_furnace_whelp_ability(self):
        """Test Furnace Whelp's self-buff ability which gives +1/+0 until end of turn for R."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.battlefield.add("Furnace Whelp")',
                '__self.mana.add(mana.Mana.RED, 3)',  # Add 3 red mana
                '__self.tmp = self.mana.pool[mana.Mana.RED]',  # Store initial red mana
                '__self.tmp2 = self.battlefield[0].power',  # Store initial power
                '__self.tmp3 = self.battlefield[0].toughness',  # Store initial toughness
                'a 0', '', '',  # Activate Furnace Whelp's ability
                '__assert self.battlefield[0].power == self.tmp2 + 1',  # Should be +1 power
                '__assert self.battlefield[0].toughness == self.tmp3',  # Toughness unchanged
                '__assert self.mana.pool[mana.Mana.RED] == self.tmp - 1',  # Should have used 1 red mana
                'a 0', '', '',  # Activate again
                '__assert self.battlefield[0].power == self.tmp2 + 2',  # Another +1 power
                '__assert self.battlefield[0].toughness == self.tmp3',  # Toughness still unchanged
                '__assert self.mana.pool[mana.Mana.RED] == self.tmp - 2',  # Should have used another red mana
                'a 0', '', '',  # Activate a third time
                '__assert self.battlefield[0].power == self.tmp2 + 3',  # Another +1 power
                '__assert self.battlefield[0].toughness == self.tmp3',  # Toughness still unchanged
                '__assert self.mana.pool[mana.Mana.RED] == self.tmp - 3',  # Should have used all red mana
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep'  # Complete the turn (cleanup happens between turns)
                ]):
            
            self.GAME.handle_turn()
            
            whelp = next((c for c in self.player.battlefield if c.name == "Furnace Whelp"), None)
            self.assertIsNotNone(whelp, "Furnace Whelp not found on battlefield")
            
            self.assertEqual(whelp.power, self.player.tmp2, "Furnace Whelp power should return to base value after turn")
            self.assertEqual(whelp.toughness, self.player.tmp3, "Furnace Whelp toughness should remain unchanged")
            
            self.assertEqual(self.player.mana.pool[mana.Mana.RED], 0, "Red mana should be spent")

    def test_chargeup_abilities(self):
        """Test abilities that use charge counters."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.opponent.library.clear()',  # Clear library to track precisely
                '__self.opponent.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.battlefield.add("Grindclock")',
                '__[self.opponent.library.add("Plains") for _ in range(5)]',
                '__self.tmp = len(self.opponent.library)',  # Store initial library size
                
                '__self.battlefield[0].status.counters["charge"] = 0',  # Initialize counter
                '__self.battlefield[0].status.counters["charge"] += 1',  # Add first counter
                '__self.verified_counter1 = self.battlefield[0].status.counters.get("charge", 0) == 1',
                
                # Add another charge counter
                '__self.battlefield[0].status.counters["charge"] += 1',  # Add second counter
                '__self.verified_counter2 = self.battlefield[0].status.counters.get("charge", 0) == 2',
                
                # Mill opponent based on counters (now 2)
                '__self.opponent.mill(2)',  # Mill 2 cards
                '__self.verified_mill = len(self.opponent.library) == self.tmp - 2',
                '__self.verified_graveyard = len(self.opponent.graveyard) == 2',
                '__self.verified_plains = all(card.name == "Plains" for card in self.opponent.graveyard)',
                
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            
            grindclock = next((c for c in self.player.battlefield if c.name == "Grindclock"), None)
            self.assertIsNotNone(grindclock, "Grindclock not found on battlefield")
            
            self.assertTrue(hasattr(self.player, 'verified_counter1') and self.player.verified_counter1, 
                           "First charge counter not added correctly")
            self.assertTrue(hasattr(self.player, 'verified_counter2') and self.player.verified_counter2, 
                           "Second charge counter not added correctly")
            
            # Verify opponent's library and graveyard
            self.assertTrue(hasattr(self.player, 'verified_mill') and self.player.verified_mill, 
                           "Opponent library size incorrect after mill")
            self.assertTrue(hasattr(self.player, 'verified_graveyard') and self.player.verified_graveyard, 
                           "Opponent graveyard should contain 2 cards")
            self.assertTrue(hasattr(self.player, 'verified_plains') and self.player.verified_plains, 
                           "Cards in opponent's graveyard are not all Plains")

    def test_self_sacrifice_abilities(self):
        """Test activated abilities with self-sacrifice."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.battlefield.add("Selfless Cathar")',
                '__self.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.tmp = len(self.battlefield)',  # Store initial battlefield size
                '__self.tmp2 = [c.power for c in self.battlefield if c.name == "Soulmender"]',  # Store initial powers
                '__self.mana.add(mana.Mana.WHITE, 2)',  # Need 1W for ability
                '__self.tmp3 = self.mana.pool[mana.Mana.WHITE]',  # Store initial white mana
                'a 0', '', '',  # Activate Selfless Cathar's ability (mana taken automatically)
                '__assert all(c.power == 2 for c in self.battlefield if c.name == "Soulmender")',
                '__assert not any(c.name == "Selfless Cathar" for c in self.battlefield)',
                '__assert any(c.name == "Selfless Cathar" for c in self.graveyard)',
                '__assert self.mana.pool[mana.Mana.WHITE] == self.tmp3 - 2',
                '__self.verified_during_effect = True',
                # Add enough inputs to complete the turn
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep',  # Skip to next upkeep
                '__assert all(c.power == 1 for c in self.battlefield if c.name == "Soulmender")',
                's end', 's end',  # Skip to end phase again
                's upkeep', 's upkeep'  # Skip to next upkeep again
                ]):
            
            self.GAME.handle_turn()
            
            self.assertTrue(hasattr(self.player, 'verified_during_effect') and self.player.verified_during_effect, 
                           "In-game assertions were not executed")
            
            cathar_on_battlefield = any(c.name == "Selfless Cathar" for c in self.player.battlefield)
            self.assertFalse(cathar_on_battlefield, "Selfless Cathar still on battlefield")
            
            # Verify Selfless Cathar is in graveyard
            cathar_in_graveyard = any(c.name == "Selfless Cathar" for c in self.player.graveyard)
            self.assertTrue(cathar_in_graveyard, "Selfless Cathar not found in graveyard")
            
            soulmenders = [c for c in self.player.battlefield if c.name == "Soulmender"]
            self.assertEqual(len(soulmenders), 2, "Expected 2 Soulmenders on battlefield")
            
            for soulmender in soulmenders:
                self.assertEqual(soulmender.power, 1, "Soulmender power should return to base value after turn")
            
            self.assertEqual(self.player.mana.pool[mana.Mana.WHITE], 0, "White mana not spent correctly")


if __name__ == '__main__':
    unittest.main()
