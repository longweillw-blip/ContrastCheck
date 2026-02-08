"""
Unit tests for ColorExtractor module.
"""

import unittest

import numpy as np

from contrast_check.color_extractor import ColorExtractor


class TestColorExtractor(unittest.TestCase):
    """Test cases for ColorExtractor class."""

    def setUp(self):
        """Set up test cases."""
        self.extractor = ColorExtractor(n_text_colors=3, n_bg_colors=3)

    def test_initialization(self):
        """Test ColorExtractor initialization."""
        self.assertEqual(self.extractor.n_text_colors, 3)
        self.assertEqual(self.extractor.n_bg_colors, 3)

    def test_extract_text_color_single_color(self):
        """Test text color extraction with uniform color."""
        # Create a uniform black image (BGR format)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.ones((100, 100), dtype=bool)

        color = self.extractor.extract_text_color(image, mask)

        # Should extract black color (0, 0, 0) in RGB
        self.assertEqual(color, (0, 0, 0))

    def test_extract_text_color_empty_mask(self):
        """Test text color extraction with empty mask."""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=bool)

        color = self.extractor.extract_text_color(image, mask)

        # Should return default black for empty mask
        self.assertEqual(color, (0, 0, 0))

    def test_extract_background_color_uniform(self):
        """Test background color extraction with uniform background."""
        # Create white image (BGR format)
        image = np.ones((100, 100, 3), dtype=np.uint8) * 255

        # Small text region in center
        text_mask = np.zeros((100, 100), dtype=bool)
        text_mask[40:60, 40:60] = True

        bbox = [[40, 40], [60, 40], [60, 60], [40, 60]]

        color = self.extractor.extract_background_color(image, text_mask, bbox)

        # Should extract white color (255, 255, 255) in RGB
        self.assertEqual(color, (255, 255, 255))

    def test_extract_background_color_with_margin(self):
        """Test background color extraction respects margin."""
        # Create image with different colored regions
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, :] = [255, 0, 0]  # Blue in BGR

        text_mask = np.zeros((100, 100), dtype=bool)
        text_mask[45:55, 45:55] = True

        bbox = [[45, 45], [55, 45], [55, 55], [45, 55]]

        color = self.extractor.extract_background_color(
            image, text_mask, bbox, margin=10
        )

        # Should extract blue color (0, 0, 255) in RGB
        self.assertEqual(color, (0, 0, 255))

    def test_rgb_to_hex_black(self):
        """Test RGB to hex conversion for black."""
        rgb = (0, 0, 0)
        hex_color = self.extractor.rgb_to_hex(rgb)
        self.assertEqual(hex_color, "#000000")

    def test_rgb_to_hex_white(self):
        """Test RGB to hex conversion for white."""
        rgb = (255, 255, 255)
        hex_color = self.extractor.rgb_to_hex(rgb)
        self.assertEqual(hex_color, "#ffffff")

    def test_rgb_to_hex_custom_color(self):
        """Test RGB to hex conversion for custom color."""
        rgb = (128, 64, 192)
        hex_color = self.extractor.rgb_to_hex(rgb)
        self.assertEqual(hex_color, "#8040c0")

    def test_extract_dominant_color_from_mixed(self):
        """Test extraction of dominant color from mixed pixels."""
        # Create image with mostly red pixels and some blue
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:80, :] = [0, 0, 255]  # Red in BGR (80% of image)
        image[80:, :] = [255, 0, 0]  # Blue in BGR (20% of image)

        mask = np.ones((100, 100), dtype=bool)

        color = self.extractor.extract_text_color(image, mask)

        # Should extract red as dominant color (255, 0, 0) in RGB
        # Allow some tolerance due to clustering
        self.assertTrue(color[0] > 200)  # High red channel
        self.assertTrue(color[1] < 50)  # Low green channel
        self.assertTrue(color[2] < 50)  # Low blue channel

    def test_color_extraction_boundary_cases(self):
        """Test color extraction at image boundaries."""
        image = np.ones((50, 50, 3), dtype=np.uint8) * 128

        # Text region at corner
        text_mask = np.zeros((50, 50), dtype=bool)
        text_mask[0:10, 0:10] = True

        bbox = [[0, 0], [10, 0], [10, 10], [0, 10]]

        # Should not crash and should return a valid color
        color = self.extractor.extract_background_color(image, text_mask, bbox)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)


if __name__ == "__main__":
    unittest.main()
