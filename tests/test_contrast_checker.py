"""
Unit tests for ContrastChecker module.
"""

import unittest

from contrast_check.contrast_checker import ContrastChecker


class TestContrastChecker(unittest.TestCase):
    """Test cases for ContrastChecker class."""

    def setUp(self):
        """Set up test cases."""
        self.checker = ContrastChecker()

    def test_calculate_relative_luminance_black(self):
        """Test luminance calculation for black."""
        black = (0, 0, 0)
        luminance = self.checker.calculate_relative_luminance(black)
        self.assertAlmostEqual(luminance, 0.0, places=5)

    def test_calculate_relative_luminance_white(self):
        """Test luminance calculation for white."""
        white = (255, 255, 255)
        luminance = self.checker.calculate_relative_luminance(white)
        self.assertAlmostEqual(luminance, 1.0, places=5)

    def test_contrast_ratio_black_white(self):
        """Test contrast ratio between black and white."""
        black = (0, 0, 0)
        white = (255, 255, 255)
        ratio = self.checker.calculate_contrast_ratio(black, white)
        self.assertAlmostEqual(ratio, 21.0, places=1)

    def test_contrast_ratio_same_color(self):
        """Test contrast ratio for same color."""
        color = (128, 128, 128)
        ratio = self.checker.calculate_contrast_ratio(color, color)
        self.assertAlmostEqual(ratio, 1.0, places=1)

    def test_contrast_ratio_symmetry(self):
        """Test that contrast ratio is symmetric."""
        color1 = (100, 150, 200)
        color2 = (200, 100, 50)
        ratio1 = self.checker.calculate_contrast_ratio(color1, color2)
        ratio2 = self.checker.calculate_contrast_ratio(color2, color1)
        self.assertAlmostEqual(ratio1, ratio2, places=5)

    def test_wcag_compliance_aa_normal_pass(self):
        """Test WCAG AA compliance for normal text (passing)."""
        black = (0, 0, 0)
        white = (255, 255, 255)
        ratio = self.checker.calculate_contrast_ratio(black, white)
        compliance = self.checker.check_wcag_compliance(ratio, is_large_text=False)
        self.assertTrue(compliance["AA"])
        self.assertTrue(compliance["AAA"])

    def test_wcag_compliance_aa_normal_fail(self):
        """Test WCAG AA compliance for normal text (failing)."""
        # Light gray on white has low contrast
        light_gray = (200, 200, 200)
        white = (255, 255, 255)
        ratio = self.checker.calculate_contrast_ratio(light_gray, white)
        compliance = self.checker.check_wcag_compliance(ratio, is_large_text=False)
        self.assertFalse(compliance["AA"])
        self.assertFalse(compliance["AAA"])

    def test_wcag_compliance_large_text(self):
        """Test WCAG compliance for large text."""
        # A ratio that passes for large text but fails for normal
        color1 = (118, 118, 118)
        color2 = (255, 255, 255)
        ratio = self.checker.calculate_contrast_ratio(color1, color2)

        # The ratio should be around 3.9:1, which passes large text AA
        self.assertGreater(ratio, 3.0)

    def test_get_contrast_level_excellent(self):
        """Test contrast level description for excellent contrast."""
        level = self.checker.get_contrast_level(7.5)
        self.assertEqual(level, "Excellent (AAA)")

    def test_get_contrast_level_good(self):
        """Test contrast level description for good contrast."""
        level = self.checker.get_contrast_level(5.0)
        self.assertEqual(level, "Good (AA)")

    def test_get_contrast_level_acceptable_large(self):
        """Test contrast level description for acceptable large text."""
        level = self.checker.get_contrast_level(3.5)
        self.assertEqual(level, "Acceptable for large text")

    def test_get_contrast_level_poor(self):
        """Test contrast level description for poor contrast."""
        level = self.checker.get_contrast_level(2.0)
        self.assertEqual(level, "Poor (Fails WCAG)")

    def test_analyze_contrast_complete(self):
        """Test complete contrast analysis."""
        text_color = (0, 0, 0)
        bg_color = (255, 255, 255)
        analysis = self.checker.analyze_contrast(text_color, bg_color)

        self.assertEqual(analysis["text_color"], text_color)
        self.assertEqual(analysis["bg_color"], bg_color)
        self.assertAlmostEqual(analysis["contrast_ratio"], 21.0, places=1)
        self.assertTrue(analysis["wcag_aa"])
        self.assertTrue(analysis["wcag_aaa"])
        self.assertIn("Excellent", analysis["level"])

    def test_known_contrast_values(self):
        """Test against known WCAG contrast values."""
        # Test case: #595959 on #FFFFFF should be approximately 7.0:1
        color1 = (89, 89, 89)
        color2 = (255, 255, 255)
        ratio = self.checker.calculate_contrast_ratio(color1, color2)
        self.assertAlmostEqual(ratio, 7.0, delta=0.5)


if __name__ == "__main__":
    unittest.main()
