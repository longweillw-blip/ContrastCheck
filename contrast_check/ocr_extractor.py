"""
OCR text extraction module using PaddleOCR.
"""

from typing import Any, Dict, List, Tuple

import cv2
import numpy as np


class OCRExtractor:
    """
    Extract text and coordinates from images using PaddleOCR.
    """

    def __init__(self, use_gpu: bool = False, lang: str = "en"):
        """
        Initialize OCR extractor.

        Args:
            use_gpu: Whether to use GPU for inference
            lang: Language for OCR recognition (default: 'en')
        """
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            raise ImportError(
                "PaddleOCR is not installed. Please install it with: "
                "pip install paddleocr"
            )

        self.ocr = PaddleOCR(
            use_angle_cls=True, lang=lang, use_gpu=use_gpu, show_log=False
        )

    def extract_text_regions(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text regions from an image.

        Args:
            image_path: Path to the input image

        Returns:
            List of dictionaries containing:
                - text: Extracted text
                - confidence: OCR confidence score
                - bbox: Bounding box coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                - center: Center point of the text region (x, y)
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image from {image_path}")

        # Run OCR
        result = self.ocr.ocr(image_path, cls=True)

        if not result or not result[0]:
            return []

        text_regions = []
        for line in result[0]:
            bbox = line[0]
            text_info = line[1]
            text = text_info[0]
            confidence = text_info[1]

            # Calculate center point
            bbox_array = np.array(bbox)
            center_x = int(np.mean(bbox_array[:, 0]))
            center_y = int(np.mean(bbox_array[:, 1]))

            text_regions.append(
                {
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox,
                    "center": (center_x, center_y),
                }
            )

        return text_regions

    def get_text_region_mask(
        self, image_shape: Tuple[int, int, int], bbox: List[List[float]]
    ) -> np.ndarray:
        """
        Create a binary mask for a text region.

        Args:
            image_shape: Shape of the original image (height, width, channels)
            bbox: Bounding box coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

        Returns:
            Binary mask with text region marked as True
        """
        mask = np.zeros(image_shape[:2], dtype=np.uint8)
        points = np.array(bbox, dtype=np.int32)
        cv2.fillPoly(mask, [points], 1)
        return mask.astype(bool)
