"""
Setup script for ContrastCheck.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='contrastcheck',
    version='0.1.0',
    author='ContrastCheck Contributors',
    description='A tool for analyzing text-background contrast ratios in UI screenshots',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/longway-code/ContrastCheck',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    python_requires='>=3.10',
    install_requires=[
        'paddleocr>=2.7.0',
        'paddlepaddle>=2.5.0',
        'numpy>=1.21.0',
        'opencv-python>=4.5.0',
        'Pillow>=9.0.0',
        'scikit-learn>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'pytest-mock>=3.6.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
            'isort>=5.10.0',
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'contrastcheck=contrast_check.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
