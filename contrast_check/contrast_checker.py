"""
Contrast ratio calculation and WCAG compliance checking.
"""

import math
from typing import Dict, Tuple


class ContrastChecker:
    """
    Calculate contrast ratios and check WCAG compliance.
    """

    # WCAG 2.1 contrast ratio thresholds
    WCAG_AA_NORMAL = 4.5
    WCAG_AA_LARGE = 3.0
    WCAG_AAA_NORMAL = 7.0
    WCAG_AAA_LARGE = 4.5

    @staticmethod
    def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """
        Calculate relative luminance according to WCAG guidelines.

        Args:
            rgb: RGB color tuple (0-255 range)

        Returns:
            Relative luminance value (0-1 range)
        """
        # Convert to 0-1 range
        r, g, b = [x / 255.0 for x in rgb]

        # Apply gamma correction
        def gamma_correct(channel):
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return math.pow((channel + 0.055) / 1.055, 2.4)

        r_linear = gamma_correct(r)
        g_linear = gamma_correct(g)
        b_linear = gamma_correct(b)

        # Calculate luminance
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
        return luminance

    @classmethod
    def calculate_contrast_ratio(
        cls, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
    ) -> float:
        """
        Calculate contrast ratio between two colors.

        Args:
            color1: First RGB color tuple
            color2: Second RGB color tuple

        Returns:
            Contrast ratio (1-21 range)
        """
        lum1 = cls.calculate_relative_luminance(color1)
        lum2 = cls.calculate_relative_luminance(color2)

        # Ensure lighter color is in numerator
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        return contrast_ratio

    @classmethod
    def check_wcag_compliance(
        cls, contrast_ratio: float, is_large_text: bool = False
    ) -> Dict[str, bool]:
        """
        Check WCAG compliance levels for a contrast ratio.

        Args:
            contrast_ratio: Calculated contrast ratio
            is_large_text: Whether the text is considered large (18pt+ or 14pt+ bold)

        Returns:
            Dictionary with compliance results for AA and AAA levels
        """
        if is_large_text:
            aa_pass = contrast_ratio >= cls.WCAG_AA_LARGE
            aaa_pass = contrast_ratio >= cls.WCAG_AAA_LARGE
        else:
            aa_pass = contrast_ratio >= cls.WCAG_AA_NORMAL
            aaa_pass = contrast_ratio >= cls.WCAG_AAA_NORMAL

        return {"AA": aa_pass, "AAA": aaa_pass, "ratio": round(contrast_ratio, 2)}

    @classmethod
    def get_contrast_level(cls, contrast_ratio: float) -> str:
        """
        Get a descriptive level for the contrast ratio.

        Args:
            contrast_ratio: Calculated contrast ratio

        Returns:
            String describing the contrast level
        """
        if contrast_ratio >= cls.WCAG_AAA_NORMAL:
            return "Excellent (AAA)"
        elif contrast_ratio >= cls.WCAG_AA_NORMAL:
            return "Good (AA)"
        elif contrast_ratio >= cls.WCAG_AA_LARGE:
            return "Acceptable for large text"
        else:
            return "Poor (Fails WCAG)"

    @classmethod
    def analyze_contrast(
        cls,
        text_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int],
        is_large_text: bool = False,
    ) -> Dict:
        """
        Perform complete contrast analysis.

        Args:
            text_color: RGB tuple of text color
            bg_color: RGB tuple of background color
            is_large_text: Whether the text is considered large

        Returns:
            Dictionary with complete analysis results
        """
        contrast_ratio = cls.calculate_contrast_ratio(text_color, bg_color)
        compliance = cls.check_wcag_compliance(contrast_ratio, is_large_text)
        level = cls.get_contrast_level(contrast_ratio)

        return {
            "text_color": text_color,
            "bg_color": bg_color,
            "contrast_ratio": round(contrast_ratio, 2),
            "wcag_aa": compliance["AA"],
            "wcag_aaa": compliance["AAA"],
            "level": level,
            "is_large_text": is_large_text,
        }
