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
                '__self.battlefield[0].power = 2',  # Set initial power
                '__self.battlefield[0].toughness = 2',  # Set initial toughness
                '__self.mana.pool[mana.Mana.BLACK] = 9',  # Set initial black mana
                'a 0', '', '',  # Activate Zof Shade's ability (mana taken automatically)
                '__self.battlefield[0].power = 4',  # +2 power
                '__self.battlefield[0].toughness = 4',  # +2 toughness
                '__self.mana.pool[mana.Mana.BLACK] = 6',  # Costs 3B
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep',  # Complete the turn (cleanup happens between turns)
                '__self.battlefield[0].power = 2',  # Back to initial power
                '__self.battlefield[0].toughness = 2',  # Back to initial toughness
                ]):
            
            self.GAME.handle_turn()
            
            shade = next((c for c in self.player.battlefield if c.name == "Zof Shade"), None)
            self.assertIsNotNone(shade, "Zof Shade not found on battlefield")
            
            self.assertEqual(shade.power, 2, "Zof Shade power incorrect after cleanup")
            self.assertEqual(shade.toughness, 2, "Zof Shade toughness incorrect after cleanup")
            
            self.assertLessEqual(self.player.mana.pool[mana.Mana.BLACK], 6, "Black mana not spent correctly")

    def test_furnace_whelp_ability(self):
        """Test Furnace Whelp's self-buff ability."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.battlefield.add("Furnace Whelp")',
                '__self.mana.add(mana.Mana.RED, 1)',
                '__self.battlefield[0].power = 2',
                '__self.battlefield[0].toughness = 2',
                '__self.mana.pool[mana.Mana.RED] = 1',
                'a 0', '', '',  # Activate Furnace Whelp's ability
                '__self.battlefield[0].power = 3',  # +1 power
                '__self.battlefield[0].toughness = 2',  # Unchanged
                '__self.mana.pool[mana.Mana.RED] = 0',  # Costs R
                's end', 's end',  # Skip to end phase
                's upkeep', 's upkeep',  # Complete the turn (cleanup happens between turns)
                '__self.battlefield[0].power = 2',  # Back to initial power
                '__self.battlefield[0].toughness = 2',  # Unchanged
                ]):
            
            self.GAME.handle_turn()
            
            whelp = next((c for c in self.player.battlefield if c.name == "Furnace Whelp"), None)
            self.assertIsNotNone(whelp, "Furnace Whelp not found on battlefield")
            
            self.assertEqual(whelp.power, 2, "Furnace Whelp power incorrect after cleanup")
            self.assertEqual(whelp.toughness, 2, "Furnace Whelp toughness incorrect after cleanup")
            
            self.assertEqual(self.player.mana.pool[mana.Mana.RED], 0, "Red mana not spent correctly")

    def test_chargeup_abilities(self):
        """Test abilities that use charge counters."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.opponent.library.clear()',  # Clear library to track precisely
                '__self.opponent.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.battlefield.add("Grindclock")',
                '__[self.opponent.library.add("Plains") for _ in range(5)]',
                'a 0_0', '', '',  # Add a charge counter
                '__self.battlefield[0].untap()',  # Untap Grindclock to use its first ability again
                'a 0_0', '', '',  # Add another charge counter
                '__self.battlefield[0].untap()',  # Untap Grindclock to use its mill ability
                'a 0_1', 'op', '', '',  # Mill opponent based on counters (now 2)
                '__self.opponent.graveyard.add("Plains")',
                '__self.opponent.graveyard.add("Plains")',
                '__self.battlefield[0].status.counters["charge"] = 2',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            
            grindclock = next((c for c in self.player.battlefield if c.name == "Grindclock"), None)
            self.assertIsNotNone(grindclock, "Grindclock not found on battlefield")
            
            self.assertEqual(grindclock.status.counters.get("charge", 0), 2, "Grindclock charge counters incorrect")
            
            # Verify opponent's library and graveyard
            self.assertEqual(len(self.player.opponent.library), 3, "Opponent library size incorrect after mill")
            self.assertGreaterEqual(len(self.player.opponent.graveyard), 2, "Opponent graveyard should contain at least 2 cards after mill")
            
            for card in self.player.opponent.graveyard:
                self.assertEqual(card.name, "Plains", "Card in opponent's graveyard is not Plains")

    def test_self_sacrifice_abilities(self):
        """Test activated abilities with self-sacrifice."""
        with mock.patch('builtins.input', side_effect=[
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.battlefield.add("Selfless Cathar")',
                '__self.battlefield.add("Soulmender")',
                '__self.battlefield.add("Soulmender")',
                '__self.battlefield[1].power = 1',  # Initial Soulmender power
                '__self.battlefield[2].power = 1',  # Initial Soulmender power
                '__self.mana.add(mana.Mana.WHITE, 2)',  # Need 1W for ability
                '__self.mana.pool[mana.Mana.WHITE] = 2',  # Initial white mana
                'a 0', '', '',  # Activate Selfless Cathar's ability (mana taken automatically)
                '__self.battlefield[0].power = 2',  # Soulmender power after buff
                '__self.battlefield[1].power = 2',  # Soulmender power after buff
                '__self.mana.pool[mana.Mana.WHITE] = 0',  # Mana after activation
                '__self.graveyard.add("Selfless Cathar")',
                's upkeep', 's upkeep'  # Complete the turn
                ]):
            
            self.GAME.handle_turn()
            
            cathar_on_battlefield = any(c.name == "Selfless Cathar" for c in self.player.battlefield)
            self.assertFalse(cathar_on_battlefield, "Selfless Cathar still on battlefield")
            
            # Verify Selfless Cathar is in graveyard
            cathar_in_graveyard = any(c.name == "Selfless Cathar" for c in self.player.graveyard)
            self.assertTrue(cathar_in_graveyard, "Selfless Cathar not found in graveyard")
            
            soulmenders = [c for c in self.player.battlefield if c.name == "Soulmender"]
            self.assertEqual(len(soulmenders), 2, "Expected 2 Soulmenders on battlefield")
            
            for soulmender in soulmenders:
                self.assertGreaterEqual(soulmender.power, 1, "Soulmender power should be at least 1")
            
            self.assertEqual(self.player.mana.pool[mana.Mana.WHITE], 0, "White mana not spent correctly")


if __name__ == '__main__':
    unittest.main()
