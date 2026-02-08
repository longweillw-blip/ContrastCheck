"""
Unit tests for OCRExtractor module.
"""

import unittest
from unittest.mock import Mock, patch

import numpy as np

from contrast_check.ocr_extractor import OCRExtractor


class TestOCRExtractor(unittest.TestCase):
    """Test cases for OCRExtractor class."""

    @patch("paddleocr.PaddleOCR")
    def test_initialization(self, mock_paddle):
        """Test OCRExtractor initialization."""
        OCRExtractor(use_gpu=False, lang="en")

        # Check that PaddleOCR was called with correct parameters
        mock_paddle.assert_called_once_with(
            use_angle_cls=True, lang="en", use_gpu=False, show_log=False
        )

    @patch("paddleocr.PaddleOCR")
    def test_initialization_with_gpu(self, mock_paddle):
        """Test OCRExtractor initialization with GPU."""
        OCRExtractor(use_gpu=True, lang="ch")

        mock_paddle.assert_called_once_with(
            use_angle_cls=True, lang="ch", use_gpu=True, show_log=False
        )

    def test_get_text_region_mask(self):
        """Test text region mask creation."""
        # Create a dummy extractor (without actual PaddleOCR initialization)
        with patch("paddleocr.PaddleOCR"):
            extractor = OCRExtractor()

        # Test with a simple rectangular bbox
        image_shape = (100, 100, 3)
        bbox = [[10, 10], [50, 10], [50, 30], [10, 30]]

        mask = extractor.get_text_region_mask(image_shape, bbox)

        # Check mask properties
        self.assertEqual(mask.shape, (100, 100))
        self.assertEqual(mask.dtype, bool)

        # Check that mask contains True values in the region
        self.assertTrue(np.any(mask))

        # Check approximate region size (should be roughly 40x20 = 800 pixels)
        true_count = np.sum(mask)
        self.assertGreater(true_count, 700)
        self.assertLess(true_count, 900)

    def test_get_text_region_mask_complex_shape(self):
        """Test mask creation with a complex polygon."""
        with patch("paddleocr.PaddleOCR"):
            extractor = OCRExtractor()

        image_shape = (200, 200, 3)
        # Quadrilateral (trapezoid)
        bbox = [[20, 20], [80, 30], [70, 50], [30, 40]]

        mask = extractor.get_text_region_mask(image_shape, bbox)

        self.assertEqual(mask.shape, (200, 200))
        self.assertTrue(np.any(mask))

    @patch("contrast_check.ocr_extractor.cv2.imread")
    @patch("paddleocr.PaddleOCR")
    def test_extract_text_regions_empty_result(self, mock_paddle, mock_imread):
        """Test extraction with no text detected."""
        # Mock OCR to return empty result
        mock_ocr_instance = Mock()
        mock_ocr_instance.ocr.return_value = [[]]
        mock_paddle.return_value = mock_ocr_instance

        # Mock image reading
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        extractor = OCRExtractor()
        results = extractor.extract_text_regions("dummy_path.jpg")

        self.assertEqual(results, [])

    @patch("contrast_check.ocr_extractor.cv2.imread")
    @patch("paddleocr.PaddleOCR")
    def test_extract_text_regions_with_data(self, mock_paddle, mock_imread):
        """Test extraction with mock OCR data."""
        # Mock OCR result format: [bbox, (text, confidence)]
        mock_ocr_result = [
            [[[10, 10], [50, 10], [50, 30], [10, 30]], ("Hello", 0.95)],
            [[[60, 20], [100, 20], [100, 40], [60, 40]], ("World", 0.92)],
        ]

        mock_ocr_instance = Mock()
        mock_ocr_instance.ocr.return_value = [mock_ocr_result]
        mock_paddle.return_value = mock_ocr_instance

        # Mock image reading
        mock_imread.return_value = np.zeros((100, 150, 3), dtype=np.uint8)

        extractor = OCRExtractor()
        results = extractor.extract_text_regions("dummy_path.jpg")

        # Check results
        self.assertEqual(len(results), 2)

        # Check first result
        self.assertEqual(results[0]["text"], "Hello")
        self.assertAlmostEqual(results[0]["confidence"], 0.95)
        self.assertEqual(len(results[0]["bbox"]), 4)
        self.assertIsInstance(results[0]["center"], tuple)

        # Check second result
        self.assertEqual(results[1]["text"], "World")
        self.assertAlmostEqual(results[1]["confidence"], 0.92)

    @patch("contrast_check.ocr_extractor.cv2.imread")
    @patch("paddleocr.PaddleOCR")
    def test_extract_text_regions_invalid_image(self, mock_paddle, mock_imread):
        """Test extraction with invalid image path."""
        mock_ocr_instance = Mock()
        mock_paddle.return_value = mock_ocr_instance

        # Mock imread to return None (failed to read)
        mock_imread.return_value = None

        extractor = OCRExtractor()

        with self.assertRaises(ValueError):
            extractor.extract_text_regions("invalid_path.jpg")

    @patch("contrast_check.ocr_extractor.cv2.imread")
    @patch("paddleocr.PaddleOCR")
    def test_center_calculation(self, mock_paddle, mock_imread):
        """Test that center point is calculated correctly."""
        mock_ocr_result = [[[[0, 0], [100, 0], [100, 50], [0, 50]], ("Test", 0.99)]]

        mock_ocr_instance = Mock()
        mock_ocr_instance.ocr.return_value = [mock_ocr_result]
        mock_paddle.return_value = mock_ocr_instance

        mock_imread.return_value = np.zeros((100, 150, 3), dtype=np.uint8)

        extractor = OCRExtractor()
        results = extractor.extract_text_regions("dummy_path.jpg")

        # Center should be at (50, 25)
        self.assertEqual(results[0]["center"], (50, 25))


if __name__ == "__main__":
    unittest.main()
