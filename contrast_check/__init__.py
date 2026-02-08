"""
ContrastCheck - UI Screenshot Contrast Ratio Analyzer

A tool for analyzing text-background contrast ratios in UI screenshots
using PaddleOCR and K-means clustering.
"""

__version__ = "0.1.0"
__author__ = "ContrastCheck Contributors"

from .color_extractor import ColorExtractor
from .contrast_checker import ContrastChecker
from .ocr_extractor import OCRExtractor

__all__ = ["OCRExtractor", "ColorExtractor", "ContrastChecker"]
