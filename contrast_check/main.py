"""
Main application for analyzing UI screenshot contrast ratios.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

import cv2

from .color_extractor import ColorExtractor
from .contrast_checker import ContrastChecker
from .ocr_extractor import OCRExtractor


class ContrastAnalyzer:
    """
    Main analyzer for UI screenshot contrast checking.
    """

    def __init__(
        self,
        use_gpu: bool = False,
        lang: str = "en",
        n_text_colors: int = 3,
        n_bg_colors: int = 3,
    ):
        """
        Initialize the contrast analyzer.

        Args:
            use_gpu: Whether to use GPU for OCR
            lang: Language for OCR
            n_text_colors: Number of color clusters for text
            n_bg_colors: Number of color clusters for background
        """
        self.ocr_extractor = OCRExtractor(use_gpu=use_gpu, lang=lang)
        self.color_extractor = ColorExtractor(
            n_text_colors=n_text_colors, n_bg_colors=n_bg_colors
        )
        self.contrast_checker = ContrastChecker()

    def analyze_image(self, image_path: str, is_large_text: bool = False) -> List[Dict]:
        """
        Analyze contrast ratios in an image.

        Args:
            image_path: Path to the input image
            is_large_text: Whether to treat text as large for WCAG standards

        Returns:
            List of analysis results for each text region
        """
        # Extract text regions
        text_regions = self.ocr_extractor.extract_text_regions(image_path)

        if not text_regions:
            print("No text detected in the image.")
            return []

        # Load image
        image = cv2.imread(image_path)
        image_shape = image.shape

        results = []

        for idx, region in enumerate(text_regions):
            # Create text mask
            text_mask = self.ocr_extractor.get_text_region_mask(
                image_shape, region["bbox"]
            )

            # Extract colors
            text_color = self.color_extractor.extract_text_color(image, text_mask)
            bg_color = self.color_extractor.extract_background_color(
                image, text_mask, region["bbox"]
            )

            # Analyze contrast
            analysis = self.contrast_checker.analyze_contrast(
                text_color, bg_color, is_large_text
            )

            # Add region info
            result = {
                "index": idx,
                "text": region["text"],
                "confidence": round(region["confidence"], 3),
                "bbox": region["bbox"],
                "center": region["center"],
                "text_color": text_color,
                "text_color_hex": self.color_extractor.rgb_to_hex(text_color),
                "bg_color": bg_color,
                "bg_color_hex": self.color_extractor.rgb_to_hex(bg_color),
                "contrast_ratio": analysis["contrast_ratio"],
                "wcag_aa": analysis["wcag_aa"],
                "wcag_aaa": analysis["wcag_aaa"],
                "level": analysis["level"],
            }

            results.append(result)

        return results

    def generate_report(self, results: List[Dict], output_format: str = "json") -> str:
        """
        Generate a report from analysis results.

        Args:
            results: List of analysis results
            output_format: Output format ('json' or 'text')

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return json.dumps(results, indent=2, ensure_ascii=False)

        elif output_format == "text":
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("CONTRAST ANALYSIS REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"\nTotal text regions analyzed: {len(results)}\n")

            for result in results:
                report_lines.append("-" * 80)
                report_lines.append(f"Text #{result['index']}: {result['text']}")
                report_lines.append(f"  OCR Confidence: {result['confidence']:.1%}")
                report_lines.append(
                    f"  Text Color: RGB{result['text_color']} "
                    f"({result['text_color_hex']})"
                )
                report_lines.append(
                    f"  Background Color: RGB{result['bg_color']} "
                    f"({result['bg_color_hex']})"
                )
                report_lines.append(f"  Contrast Ratio: {result['contrast_ratio']}:1")
                report_lines.append(
                    f"  WCAG AA: {'✓ PASS' if result['wcag_aa'] else '✗ FAIL'}"
                )
                report_lines.append(
                    f"  WCAG AAA: {'✓ PASS' if result['wcag_aaa'] else '✗ FAIL'}"
                )
                report_lines.append(f"  Level: {result['level']}")
                report_lines.append("")

            # Summary
            total = len(results)
            aa_pass = sum(1 for r in results if r["wcag_aa"])
            aaa_pass = sum(1 for r in results if r["wcag_aaa"])

            report_lines.append("=" * 80)
            report_lines.append("SUMMARY")
            report_lines.append("=" * 80)
            report_lines.append(
                f"WCAG AA Compliance: {aa_pass}/{total} ({aa_pass/total*100:.1f}%)"
            )
            report_lines.append(
                f"WCAG AAA Compliance: {aaa_pass}/{total} ({aaa_pass/total*100:.1f}%)"
            )
            report_lines.append("=" * 80)

            return "\n".join(report_lines)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")


def main():
    """
    Command-line interface for ContrastCheck.
    """
    parser = argparse.ArgumentParser(
        description="Analyze text-background contrast ratios in UI screenshots"
    )
    parser.add_argument("image", type=str, help="Path to the UI screenshot image")
    parser.add_argument(
        "-o", "--output", type=str, help="Output file path for the report"
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--large-text",
        action="store_true",
        help="Treat all text as large text (18pt+ or 14pt+ bold)",
    )
    parser.add_argument("--gpu", action="store_true", help="Use GPU for OCR processing")
    parser.add_argument(
        "--lang", type=str, default="en", help="Language for OCR (default: en)"
    )

    args = parser.parse_args()

    # Check if image exists
    if not Path(args.image).exists():
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    # Initialize analyzer
    print("Initializing ContrastCheck...")
    analyzer = ContrastAnalyzer(use_gpu=args.gpu, lang=args.lang)

    # Analyze image
    print(f"Analyzing image: {args.image}")
    results = analyzer.analyze_image(args.image, is_large_text=args.large_text)

    if not results:
        print("No text regions found in the image.")
        sys.exit(0)

    # Generate report
    report = analyzer.generate_report(results, output_format=args.format)

    # Output report
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
