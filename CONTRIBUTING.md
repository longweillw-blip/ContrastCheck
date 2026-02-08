# Contributing to ContrastCheck

Thank you for your interest in contributing to ContrastCheck! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear, descriptive title
- Detailed steps to reproduce the issue
- Expected vs actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear, descriptive title
- Detailed description of the proposed feature
- Explanation of why this enhancement would be useful
- Possible implementation approach

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Ensure all tests pass** by running `pytest`
5. **Update documentation** if needed
6. **Commit your changes** with clear, descriptive messages
7. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Steps

1. Clone your fork:
```bash
git clone https://github.com/yourusername/ContrastCheck.git
cd ContrastCheck
```

2. Install uv if you haven't already:
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Create a virtual environment with Python 3.10+:
```bash
uv venv --python 3.10
```

4. Activate the virtual environment:
```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

5. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters (Black default)

### Code Formatting

Format your code before committing:

```bash
# Format code
black contrast_check/ tests/

# Sort imports
isort contrast_check/ tests/

# Check style
flake8 contrast_check/ tests/

# Type checking
mypy contrast_check/
```

### Documentation

- Add docstrings to all public modules, classes, and functions
- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings
- Update README.md for new features
- Include code examples where appropriate

### Testing

- Write unit tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=contrast_check --cov-report=html

# Run specific test file
pytest tests/test_contrast_checker.py -v
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Good commit message examples:
```
Add support for batch image processing

Implement WCAG AAA compliance checking

Fix color extraction edge case for small text regions

Update README with installation instructions
```

## Project Structure

```
ContrastCheck/
├── contrast_check/          # Main package
│   ├── __init__.py
│   ├── ocr_extractor.py     # OCR functionality
│   ├── color_extractor.py   # Color extraction
│   ├── contrast_checker.py  # Contrast calculation
│   └── main.py              # CLI and main app
├── tests/                   # Test suite
├── examples/                # Usage examples
├── docs/                    # Documentation (future)
└── ...
```

## Testing Guidelines

### Unit Tests

- Test individual components in isolation
- Mock external dependencies (PaddleOCR, file I/O)
- Cover edge cases and error conditions
- Use parametrized tests for multiple scenarios

### Integration Tests

- Test components working together
- Use real but small test images
- Verify end-to-end functionality

### Test Coverage

- Aim for >90% code coverage
- Focus on critical paths
- Don't sacrifice quality for coverage percentage

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Include parameter types and return types
- Provide usage examples for complex functions
- Explain the "why" not just the "what"

### README Updates

Update the README when you:
- Add new features
- Change CLI options
- Modify installation process
- Add new dependencies

## Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create a new git tag
4. Push to GitHub
5. Create a GitHub release
6. Publish to PyPI (maintainers only)

## Getting Help

- Join discussions in GitHub Issues
- Ask questions in Pull Request comments
- Check existing documentation and issues first

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to ContrastCheck! 🎉
