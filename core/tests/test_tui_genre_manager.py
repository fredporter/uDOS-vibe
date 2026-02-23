"""Test TUI GENRE Manager functionality."""

import unittest
import sys
from pathlib import Path

# Add core to path
CORE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CORE_PATH))

from core.services.tui_genre_manager import get_tui_genre_manager


class TestTuiGenreManager(unittest.TestCase):
    """Test TUI GENRE Manager basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = get_tui_genre_manager()

    def test_list_genres(self):
        """Test that GENRE listing works."""
        genres = self.manager.list_genres()
        self.assertIsInstance(genres, list)
        self.assertGreater(len(genres), 0)
        
        # Check that we have at least the basic genres
        genre_names = [g['name'] for g in genres]
        self.assertIn('minimal', genre_names)
        self.assertIn('retro', genre_names)
        self.assertIn('neon', genre_names)

    def test_get_active_genre(self):
        """Test getting active GENRE."""
        active = self.manager.get_active_genre()
        self.assertIsNotNone(active)
        self.assertIn(active, ['minimal', 'retro', 'neon'])

    def test_set_active_genre(self):
        """Test setting active GENRE."""
        # Test setting to a valid GENRE
        result = self.manager.set_active_genre('retro')
        self.assertTrue(result)
        self.assertEqual(self.manager.get_active_genre(), 'retro')
        
        # Test setting to an invalid GENRE
        result = self.manager.set_active_genre('nonexistent')
        self.assertFalse(result)

    def test_message_formatting(self):
        """Test message formatting with different GENREs."""
        # Test error formatting
        error_msg = self.manager.format_error("Test error")
        self.assertIn("ERROR", error_msg)
        self.assertIn("Test error", error_msg)
        
        # Test warning formatting
        warning_msg = self.manager.format_warning("Test warning")
        self.assertIn("WARNING", warning_msg)
        self.assertIn("Test warning", warning_msg)
        
        # Test success formatting
        success_msg = self.manager.format_success("Test success")
        self.assertIn("SUCCESS", success_msg)
        self.assertIn("Test success", success_msg)

    def test_box_creation(self):
        """Test box creation with active GENRE."""
        box = self.manager.create_box("Test Title", "Test content", 40)
        self.assertIsInstance(box, str)
        self.assertGreater(len(box), 0)
        
        # Check that box contains expected elements
        lines = box.split('\n')
        self.assertGreater(len(lines), 2)  # Should have at least title and content
        
        # Check for border characters (basic validation)
        box_chars = ''.join(lines)
        self.assertTrue(any(c in box_chars for c in ['┌', '┐', '└', '┘', '╔', '╗', '╚', '╝']))

    def test_genre_specific_features(self):
        """Test that different GENREs have different formatting."""
        # Set to retro GENRE
        self.manager.set_active_genre('retro')
        retro_error = self.manager.format_error("Test")
        
        # Set to neon GENRE
        self.manager.set_active_genre('neon')
        neon_error = self.manager.format_error("Test")
        
        # They should be different
        self.assertNotEqual(retro_error, neon_error)
        
        # Set to minimal GENRE
        self.manager.set_active_genre('minimal')
        minimal_error = self.manager.format_error("Test")
        
        # Minimal should be different from others
        self.assertNotEqual(minimal_error, retro_error)
        self.assertNotEqual(minimal_error, neon_error)


if __name__ == '__main__':
    unittest.main()
