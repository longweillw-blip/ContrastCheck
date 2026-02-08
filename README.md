# ContrastCheck

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful tool for analyzing text-background contrast ratios in UI screenshots using PaddleOCR and K-means clustering to ensure WCAG accessibility compliance.

## Features

- **Automatic Text Detection**: Uses PaddleOCR to automatically detect and extract text regions from UI screenshots
- **Intelligent Color Extraction**: Employs K-means clustering to accurately identify text and background colors
- **WCAG Compliance Checking**: Validates contrast ratios against WCAG 2.1 AA and AAA standards
- **Multiple Output Formats**: Generate reports in both JSON and human-readable text formats
- **Easy to Use**: Simple CLI and Python API for seamless integration
- **Comprehensive**: Analyzes all text regions in an image with detailed results

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/longweillw-blip/ContrastCheck.git
cd ContrastCheck
pip install -e .
```

### Install dependencies

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

### GPU Support (Optional)

For faster OCR processing with GPU:

```bash
pip uninstall paddlepaddle
pip install paddlepaddle-gpu
```

## Quick Start

### Command Line Usage

Analyze a UI screenshot:

```bash
contrastcheck your_screenshot.png
```

Generate a JSON report:

```bash
contrastcheck your_screenshot.png -f json -o report.json
```

Analyze with large text threshold:

```bash
contrastcheck your_screenshot.png --large-text
```

Use GPU acceleration:

```bash
contrastcheck your_screenshot.png --gpu
```

### Python API Usage

```python
from contrast_check.main import ContrastAnalyzer

# Initialize analyzer
analyzer = ContrastAnalyzer(use_gpu=False, lang='en')

# Analyze image
results = analyzer.analyze_image('screenshot.png')

# Print results
for result in results:
    print(f"Text: {result['text']}")
    print(f"Contrast Ratio: {result['contrast_ratio']}:1")
    print(f"WCAG AA: {'PASS' if result['wcag_aa'] else 'FAIL'}")
    print()

# Generate report
report = analyzer.generate_report(results, output_format='text')
print(report)
```

## How It Works

1. **Text Detection**: PaddleOCR identifies all text regions in the screenshot and extracts their bounding boxes
2. **Color Extraction**:
   - Text colors are extracted from pixels within the detected text regions
   - Background colors are sampled from areas surrounding the text
   - K-means clustering identifies the dominant colors
3. **Contrast Calculation**: Calculates relative luminance and contrast ratios according to WCAG 2.1 guidelines
4. **Compliance Check**: Compares ratios against WCAG AA (4.5:1 normal, 3:1 large) and AAA (7:1 normal, 4.5:1 large) thresholds

## WCAG Compliance Levels

### Normal Text
- **WCAG AA**: Minimum contrast ratio of 4.5:1
- **WCAG AAA**: Minimum contrast ratio of 7:1

### Large Text (18pt+ or 14pt+ bold)
- **WCAG AA**: Minimum contrast ratio of 3:1
- **WCAG AAA**: Minimum contrast ratio of 4.5:1

## Example Output

### Text Format

```
================================================================================
CONTRAST ANALYSIS REPORT
================================================================================

Total text regions analyzed: 3

--------------------------------------------------------------------------------
Text #0: Sign In
  OCR Confidence: 95.2%
  Text Color: RGB(0, 0, 0) (#000000)
  Background Color: RGB(255, 255, 255) (#ffffff)
  Contrast Ratio: 21.0:1
  WCAG AA: ✓ PASS
  WCAG AAA: ✓ PASS
  Level: Excellent (AAA)

--------------------------------------------------------------------------------
Text #1: Username
  OCR Confidence: 92.8%
  Text Color: RGB(102, 102, 102) (#666666)
  Background Color: RGB(255, 255, 255) (#ffffff)
  Contrast Ratio: 5.7:1
  WCAG AA: ✓ PASS
  WCAG AAA: ✗ FAIL
  Level: Good (AA)

================================================================================
SUMMARY
================================================================================
WCAG AA Compliance: 3/3 (100.0%)
WCAG AAA Compliance: 2/3 (66.7%)
================================================================================
```

### JSON Format

```json
[
  {
    "index": 0,
    "text": "Sign In",
    "confidence": 0.952,
    "text_color": [0, 0, 0],
    "text_color_hex": "#000000",
    "bg_color": [255, 255, 255],
    "bg_color_hex": "#ffffff",
    "contrast_ratio": 21.0,
    "wcag_aa": true,
    "wcag_aaa": true,
    "level": "Excellent (AAA)"
  }
]
```

## CLI Options

```
usage: contrastcheck [-h] [-o OUTPUT] [-f {json,text}] [--large-text]
                     [--gpu] [--lang LANG] image

positional arguments:
  image                 Path to the UI screenshot image

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path for the report
  -f {json,text}, --format {json,text}
                        Output format (default: text)
  --large-text          Treat all text as large text (18pt+ or 14pt+ bold)
  --gpu                 Use GPU for OCR processing
  --lang LANG           Language for OCR (default: en)
```

## Project Structure

```
ContrastCheck/
├── contrast_check/          # Main package
│   ├── __init__.py
│   ├── ocr_extractor.py     # OCR text extraction
│   ├── color_extractor.py   # Color extraction using K-means
│   ├── contrast_checker.py  # Contrast ratio calculation
│   └── main.py              # Main application and CLI
├── tests/                   # Unit tests
│   ├── test_ocr_extractor.py
│   ├── test_color_extractor.py
│   ├── test_contrast_checker.py
│   └── test_main.py
├── examples/                # Usage examples
│   └── simple_usage.py
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── setup.py                 # Package setup
├── pytest.ini               # Pytest configuration
├── LICENSE                  # MIT License
└── README.md                # This file
```

## Development

### Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=contrast_check --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_contrast_checker.py
```

### Code Quality

Format code with Black:

```bash
black contrast_check/ tests/
```

Check code style:

```bash
flake8 contrast_check/ tests/
```

Sort imports:

```bash
isort contrast_check/ tests/
```

Type checking:

```bash
mypy contrast_check/
```

## Dependencies

- **PaddleOCR**: Text detection and recognition
- **OpenCV**: Image processing
- **scikit-learn**: K-means clustering for color extraction
- **NumPy**: Numerical computations
- **Pillow**: Image handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for the excellent OCR engine
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) for accessibility standards
- The open-source community for continuous support

## Citation

If you use ContrastCheck in your research or project, please cite:

```bibtex
@software{contrastcheck2026,
  title = {ContrastCheck: UI Screenshot Contrast Ratio Analyzer},
  author = {ContrastCheck Contributors},
  year = {2026},
  url = {https://github.com/longweillw-blip/ContrastCheck}
}
```

## Support

If you encounter any issues or have questions:

- Open an issue on [GitHub](https://github.com/yourusername/ContrastCheck/issues)
- Check the [examples](examples/) directory for usage examples
- Read the [WCAG 2.1 documentation](https://www.w3.org/WAI/WCAG21/quickref/) for accessibility guidelines

## Roadmap

- [ ] Support for multiple languages in OCR
- [ ] Batch processing of multiple images
- [ ] Visual output with highlighted regions
- [ ] Web interface for easy access
- [ ] Integration with CI/CD pipelines
- [ ] Support for PDF documents
- [ ] Color blindness simulation

---

Made with ❤️ for better web accessibility
