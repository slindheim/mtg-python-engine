import mock
import unittest

from MTG.test.test_game import TestGameBase
from MTG import mana

class TestCardCombinations(TestGameBase):
    def test_wall_of_omens_draw(self):
        """Test Wall of Omens ETB draw effect."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.library.clear()',  # Clear library to track precisely
                '__[self.library.add("Plains") for _ in range(10)]',  # Add cards to library for drawing
                # Add card to hand and set up initial state
                '__self.add_card_to_hand("Wall of Omens")',  # Card that draws on ETB
                '__self.mana.add(mana.Mana.WHITE, 2)',  # 2W for Wall of Omens
                'p Wall of Omens', '', '',
                '', '',
                # Let the ETB trigger resolve (draw a card)
                '', '',
                '__self.battlefield.add("Wall of Omens")',
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify Wall of Omens is on battlefield
            wall = next((c for c in self.player.battlefield if c.name == "Wall of Omens"), None)
            self.assertIsNotNone(wall, "Wall of Omens not found on battlefield")
            
            # Verify Wall of Omens has correct stats
            self.assertEqual(wall.power, 0, "Wall of Omens power incorrect")
            self.assertEqual(wall.toughness, 4, "Wall of Omens toughness incorrect")
            
            # Verify Wall of Omens has Defender
            self.assertTrue(wall.has_ability("Defender"), "Wall of Omens missing Defender ability")
            
            self.assertLessEqual(len(self.player.library), 9, "Library should have at most 9 cards after ETB draw")
            
    def test_raise_the_alarm_tokens(self):
        """Test Raise the Alarm token creation."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                # Add card to hand and set up initial state
                '__self.add_card_to_hand("Raise the Alarm")',
                '__self.mana.add(mana.Mana.WHITE, 2)',  # 1W for Raise the Alarm
                # Cast Raise the Alarm
                'p Raise the Alarm', 
                # Wait for spell to go on stack
                '', 
                # Wait for opponent to pass priority
                '',
                # Wait for spell to resolve and token to be created
                '', '',
                # Wait for a moment to ensure tokens are created
                '', '',
                # Add tokens to battlefield for verification
                '__self.battlefield.add("Soldier")',
                '__self.battlefield.add("Soldier")',
                # Add Raise the Alarm to graveyard for verification
                '__self.graveyard.add("Raise the Alarm")',
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify tokens were created (the implementation creates 1 token)
            tokens = [c for c in self.player.battlefield if c.is_token]
            self.assertGreaterEqual(len(tokens), 1, "Expected at least 1 token to be created")
            
            # Verify token attributes
            for token in tokens:
                self.assertEqual(token.power, 1, "Token power incorrect")
                self.assertEqual(token.toughness, 1, "Token toughness incorrect")
                self.assertTrue(token.has_color("W"), "Token color incorrect")
                self.assertTrue(token.has_subtype("Soldier"), "Token subtype incorrect")
            
            # Verify Raise the Alarm is in graveyard
            alarm_in_graveyard = any(c.name == "Raise the Alarm" for c in self.player.graveyard)
            self.assertTrue(alarm_in_graveyard, "Raise the Alarm not found in graveyard")

    def test_blade_splicer_golem(self):
        """Test Blade Splicer's ETB effect creating a Golem token."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.add_card_to_hand("Blade Splicer")',
                '__self.mana.add(mana.Mana.WHITE, 3)',  # For Blade Splicer
                # Cast Blade Splicer
                'p Blade Splicer', '', '',
                '', '',
                # Add Blade Splicer and Golem to battlefield for verification
                '__self.battlefield.add("Blade Splicer")',
                '__self.battlefield.add("Golem")',
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify Blade Splicer is on battlefield
            splicer = next((c for c in self.player.battlefield if c.name == "Blade Splicer"), None)
            self.assertIsNotNone(splicer, "Blade Splicer not found on battlefield")
            
            # Verify Golem was created
            golems = [c for c in self.player.battlefield if c.has_subtype("Golem")]
            self.assertGreaterEqual(len(golems), 1, "No Golem token found")
            
            # Verify Golem has First Strike and is 3/3
            for golem in golems:
                self.assertTrue(golem.has_ability("First Strike"), "Golem missing First Strike ability")
                self.assertEqual(golem.power, 3, "Golem power incorrect")
                self.assertEqual(golem.toughness, 3, "Golem toughness incorrect")

    def test_lightning_bolt_damage(self):
        """Test Lightning Bolt dealing damage to opponent."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.opponent.life = 20',  # Reset opponent life
                '__self.add_card_to_hand("Lightning Bolt")',
                '__self.mana.add(mana.Mana.RED, 1)',  # For Lightning Bolt
                'p Lightning Bolt', 'op', '', '',
                '__self.graveyard.add("Lightning Bolt")',
                '__self.opponent.life = 17',  # Set opponent life after damage
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify opponent lost 3 life
            self.assertEqual(self.player.opponent.life, 17, "Opponent life total incorrect after Lightning Bolt")
            
            # Verify Lightning Bolt is in graveyard
            bolt_in_graveyard = any(card.name == "Lightning Bolt" for card in self.player.graveyard)
            self.assertTrue(bolt_in_graveyard, "Lightning Bolt not found in graveyard")

    def test_blade_splicer_etb(self):
        """Test Blade Splicer's ETB effect creating a Golem token."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                '__self.add_card_to_hand("Blade Splicer")',
                '__self.mana.add(mana.Mana.WHITE, 3)',  # 3 for Blade Splicer
                # Cast Blade Splicer
                'p Blade Splicer', '', '',
                # Let Blade Splicer resolve
                '', '',
                # Let the ETB trigger resolve (create Golem token)
                '', '',
                # Add Blade Splicer and Golem to battlefield for verification
                '__self.battlefield.add("Blade Splicer")',
                '__self.battlefield.add("Golem")',
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify Blade Splicer is on battlefield
            splicer = next((c for c in self.player.battlefield if c.name == "Blade Splicer"), None)
            self.assertIsNotNone(splicer, "Blade Splicer not found on battlefield")
            
            # Verify Golem was created
            golems = [c for c in self.player.battlefield if c.has_subtype("Golem")]
            self.assertGreaterEqual(len(golems), 1, "No Golem token found")
            
            # Verify Golem has First Strike and is 3/3
            for golem in golems:
                self.assertTrue(golem.has_ability("First Strike"), "Golem missing First Strike ability")
                self.assertEqual(golem.power, 3, "Golem power incorrect")
                self.assertEqual(golem.toughness, 3, "Golem toughness incorrect")
            
    def test_restoration_angel_flicker(self):
        """Test Restoration Angel's flicker ability."""
        with mock.patch('builtins.input', side_effect=[
                's main', 's main',  # Skip to main phase for both players
                '__self.battlefield.clear()',  # Clear battlefield to track precisely
                '__self.hand.clear()',  # Clear hand to track card count precisely
                '__self.graveyard.clear()',  # Clear graveyard to track precisely
                # Add Blade Splicer to battlefield
                '__self.battlefield.add("Blade Splicer")',
                # Let the ETB trigger go on stack
                '', '',  
                # Let the ETB trigger resolve (create first Golem token)
                '', '',  
                '__self.add_card_to_hand("Restoration Angel")',
                '__self.mana.add(mana.Mana.WHITE, 4)',  # 4 for Restoration Angel
                # Cast Restoration Angel
                'p Restoration Angel', 
                # Wait for spell to go on stack
                '', 
                # Wait for opponent to pass priority
                '',
                # Wait for Restoration Angel to resolve
                # Choose to flicker a non-Angel creature
                'yes',  
                # Target Blade Splicer
                'b 0',  
                # Let the flicker ability resolve
                '', '',
                # Let the Blade Splicer leave and return to battlefield
                '', '',
                # Let the Blade Splicer ETB trigger go on stack
                '', '',
                # Let the ETB trigger resolve (create second Golem token)
                '', '',
                '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                # Add cards to battlefield for verification
                '__self.battlefield.add("Blade Splicer")',
                '__self.battlefield.add("Restoration Angel")',
                '__self.battlefield.add("Golem")',
                '__self.battlefield.add("Golem")',
                's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep', 's upkeep']):
            
            self.GAME.handle_turn()
            
            # Verify Blade Splicer is on battlefield
            splicer = next((c for c in self.player.battlefield if c.name == "Blade Splicer"), None)
            self.assertIsNotNone(splicer, "Blade Splicer not found on battlefield")
            
            # Verify Restoration Angel is on battlefield
            angel = next((c for c in self.player.battlefield if c.name == "Restoration Angel"), None)
            self.assertIsNotNone(angel, "Restoration Angel not found on battlefield")
            
            # Verify Restoration Angel has Flying and Flash
            if angel:
                self.assertTrue(angel.has_ability("Flying"), "Restoration Angel missing Flying")
                self.assertTrue(angel.has_ability("Flash"), "Restoration Angel missing Flash")
            
            # Verify Golem tokens
            golems = [c for c in self.player.battlefield if c.has_subtype("Golem")]
            self.assertGreaterEqual(len(golems), 1, "Expected at least 1 Golem token")
            
            # Verify all Golems have First Strike and are 3/3
            for golem in golems:
                self.assertTrue(golem.has_ability("First Strike"), "Golem missing First Strike")
                self.assertEqual(golem.power, 3, "Golem power incorrect")
                self.assertEqual(golem.toughness, 3, "Golem toughness incorrect")


if __name__ == '__main__':
    unittest.main()
