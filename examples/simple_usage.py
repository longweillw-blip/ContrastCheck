"""
Simple usage example for ContrastCheck.

This script demonstrates how to use ContrastCheck to analyze
text-background contrast ratios in UI screenshots.
"""

from contrast_check.main import ContrastAnalyzer


def main():
    # Initialize the analyzer
    print("Initializing ContrastCheck...")
    analyzer = ContrastAnalyzer(
        # Note: use_gpu is deprecated in PaddleOCR 3.x+
        # GPU is automatically detected and used when available
        lang="en"  # Language for OCR (en, ch, etc.)
    )

    # Analyze an image
    image_path = "your_screenshot.png"  # Replace with your image path

    print(f"Analyzing image: {image_path}")
    results = analyzer.analyze_image(image_path)

    # Print results
    if not results:
        print("No text detected in the image.")
        return

    print(f"\nFound {len(results)} text regions\n")

    for result in results:
        print(f"Text: {result['text']}")
        print(f"  Text Color: {result['text_color_hex']}")
        print(f"  Background Color: {result['bg_color_hex']}")
        print(f"  Contrast Ratio: {result['contrast_ratio']}:1")
        print(f"  WCAG AA: {'✓ PASS' if result['wcag_aa'] else '✗ FAIL'}")
        print(f"  WCAG AAA: {'✓ PASS' if result['wcag_aaa'] else '✗ FAIL'}")
        print(f"  Level: {result['level']}")
        print()

    # Generate text report
    report = analyzer.generate_report(results, output_format="text")
    print(report)

    # Save JSON report
    json_report = analyzer.generate_report(results, output_format="json")
    with open("contrast_report.json", "w") as f:
        f.write(json_report)
    print("\nJSON report saved to: contrast_report.json")


if __name__ == "__main__":
    main()
