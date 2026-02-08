"""
Unit tests for main application module.
"""

import json
import unittest
from unittest.mock import Mock, patch

from contrast_check.main import ContrastAnalyzer


class TestContrastAnalyzer(unittest.TestCase):
    """Test cases for ContrastAnalyzer class."""

    @patch("contrast_check.main.OCRExtractor")
    @patch("contrast_check.main.ColorExtractor")
    @patch("contrast_check.main.ContrastChecker")
    def test_initialization(self, mock_checker, mock_color, mock_ocr):
        """Test ContrastAnalyzer initialization."""
        ContrastAnalyzer(use_gpu=True, lang="ch", n_text_colors=5, n_bg_colors=5)

        # Verify OCRExtractor was initialized correctly
        mock_ocr.assert_called_once_with(use_gpu=True, lang="ch")

        # Verify ColorExtractor was initialized correctly
        mock_color.assert_called_once_with(n_text_colors=5, n_bg_colors=5)

    @patch("contrast_check.main.cv2.imread")
    @patch("contrast_check.main.OCRExtractor")
    @patch("contrast_check.main.ColorExtractor")
    @patch("contrast_check.main.ContrastChecker")
    def test_analyze_image_no_text(
        self, mock_checker, mock_color, mock_ocr, mock_imread
    ):
        """Test image analysis with no text detected."""
        # Mock OCR to return empty list
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text_regions.return_value = []
        mock_ocr.return_value = mock_ocr_instance

        mock_color_instance = Mock()
        mock_color.return_value = mock_color_instance

        mock_checker_instance = Mock()
        mock_checker.return_value = mock_checker_instance

        analyzer = ContrastAnalyzer()
        results = analyzer.analyze_image("test_image.jpg")

        self.assertEqual(results, [])

    @patch("contrast_check.main.cv2.imread")
    @patch("contrast_check.main.OCRExtractor")
    @patch("contrast_check.main.ColorExtractor")
    @patch("contrast_check.main.ContrastChecker")
    def test_analyze_image_with_text(
        self, mock_checker, mock_color, mock_ocr, mock_imread
    ):
        """Test image analysis with text detected."""
        import numpy as np

        # Mock image
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        # Mock OCR results
        mock_text_regions = [
            {
                "text": "Hello",
                "confidence": 0.95,
                "bbox": [[10, 10], [50, 10], [50, 30], [10, 30]],
                "center": (30, 20),
            }
        ]

        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text_regions.return_value = mock_text_regions
        mock_ocr_instance.get_text_region_mask.return_value = np.ones(
            (100, 100), dtype=bool
        )
        mock_ocr.return_value = mock_ocr_instance

        # Mock color extraction
        mock_color_instance = Mock()
        mock_color_instance.extract_text_color.return_value = (0, 0, 0)
        mock_color_instance.extract_background_color.return_value = (255, 255, 255)
        mock_color_instance.rgb_to_hex.side_effect = (
            lambda rgb: "#{:02x}{:02x}{:02x}".format(*rgb)
        )
        mock_color.return_value = mock_color_instance

        # Mock contrast checker
        mock_checker_instance = Mock()
        mock_checker_instance.analyze_contrast.return_value = {
            "text_color": (0, 0, 0),
            "bg_color": (255, 255, 255),
            "contrast_ratio": 21.0,
            "wcag_aa": True,
            "wcag_aaa": True,
            "level": "Excellent (AAA)",
            "is_large_text": False,
        }
        mock_checker.return_value = mock_checker_instance

        analyzer = ContrastAnalyzer()
        results = analyzer.analyze_image("test_image.jpg")

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Hello")
        self.assertAlmostEqual(results[0]["confidence"], 0.95)
        self.assertEqual(results[0]["contrast_ratio"], 21.0)
        self.assertTrue(results[0]["wcag_aa"])
        self.assertTrue(results[0]["wcag_aaa"])

    def test_generate_report_json(self):
        """Test JSON report generation."""
        with (
            patch("contrast_check.main.OCRExtractor"),
            patch("contrast_check.main.ColorExtractor"),
            patch("contrast_check.main.ContrastChecker"),
        ):

            analyzer = ContrastAnalyzer()

            mock_results = [
                {
                    "index": 0,
                    "text": "Test",
                    "confidence": 0.95,
                    "contrast_ratio": 7.5,
                    "wcag_aa": True,
                    "wcag_aaa": True,
                }
            ]

            report = analyzer.generate_report(mock_results, output_format="json")

            # Should be valid JSON
            parsed = json.loads(report)
            self.assertEqual(len(parsed), 1)
            self.assertEqual(parsed[0]["text"], "Test")

    def test_generate_report_text(self):
        """Test text report generation."""
        with (
            patch("contrast_check.main.OCRExtractor"),
            patch("contrast_check.main.ColorExtractor"),
            patch("contrast_check.main.ContrastChecker"),
        ):

            analyzer = ContrastAnalyzer()

            mock_results = [
                {
                    "index": 0,
                    "text": "Test",
                    "confidence": 0.95,
                    "text_color": (0, 0, 0),
                    "text_color_hex": "#000000",
                    "bg_color": (255, 255, 255),
                    "bg_color_hex": "#ffffff",
                    "contrast_ratio": 21.0,
                    "wcag_aa": True,
                    "wcag_aaa": True,
                    "level": "Excellent (AAA)",
                }
            ]

            report = analyzer.generate_report(mock_results, output_format="text")

            # Check report contains expected sections
            self.assertIn("CONTRAST ANALYSIS REPORT", report)
            self.assertIn("Test", report)
            self.assertIn("21.0:1", report)
            self.assertIn("SUMMARY", report)
            self.assertIn("WCAG AA Compliance", report)

    def test_generate_report_invalid_format(self):
        """Test report generation with invalid format."""
        with (
            patch("contrast_check.main.OCRExtractor"),
            patch("contrast_check.main.ColorExtractor"),
            patch("contrast_check.main.ContrastChecker"),
        ):

            analyzer = ContrastAnalyzer()

            with self.assertRaises(ValueError):
                analyzer.generate_report([], output_format="invalid")

    def test_generate_report_summary_statistics(self):
        """Test that summary statistics are calculated correctly."""
        with (
            patch("contrast_check.main.OCRExtractor"),
            patch("contrast_check.main.ColorExtractor"),
            patch("contrast_check.main.ContrastChecker"),
        ):

            analyzer = ContrastAnalyzer()

            mock_results = [
                {
                    "index": 0,
                    "text": "Good",
                    "confidence": 0.95,
                    "text_color": (0, 0, 0),
                    "text_color_hex": "#000000",
                    "bg_color": (255, 255, 255),
                    "bg_color_hex": "#ffffff",
                    "contrast_ratio": 21.0,
                    "wcag_aa": True,
                    "wcag_aaa": True,
                    "level": "Excellent (AAA)",
                },
                {
                    "index": 1,
                    "text": "Poor",
                    "confidence": 0.90,
                    "text_color": (200, 200, 200),
                    "text_color_hex": "#c8c8c8",
                    "bg_color": (255, 255, 255),
                    "bg_color_hex": "#ffffff",
                    "contrast_ratio": 1.5,
                    "wcag_aa": False,
                    "wcag_aaa": False,
                    "level": "Poor (Fails WCAG)",
                },
            ]

            report = analyzer.generate_report(mock_results, output_format="text")

            # Check that summary shows 50% AA compliance (1 out of 2)
            self.assertIn("1/2", report)
            self.assertIn("50.0%", report)


if __name__ == "__main__":
    unittest.main()
