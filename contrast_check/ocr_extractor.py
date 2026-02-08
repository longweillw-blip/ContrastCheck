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
            use_gpu: Deprecated. GPU is auto-detected by PaddleOCR 3.x+.
            lang: Language for OCR recognition (default: 'en')

        Note:
            PaddleOCR 3.x removed use_angle_cls, use_gpu, show_log parameters,
            and cls parameter from ocr() method.
            GPU acceleration and text direction classification are automatic.
        """
        import os

        # PaddlePaddle with OpenBlas requires OMP_NUM_THREADS=1
        # Setting to 1 prevents "does not support multi-threads" error
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("MKL_NUM_THREADS", "1")
        os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

        try:
            from paddleocr import PaddleOCR
        except ImportError:
            raise ImportError(
                "PaddleOCR is not installed. Please install it with: "
                "pip install paddleocr"
            )

        # Warn if use_gpu is explicitly set (for backward compatibility)
        if use_gpu:
            import warnings

            warnings.warn(
                "use_gpu parameter is deprecated in PaddleOCR 3.x and will be "
                "ignored. GPU is automatically detected and used when available.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Use simplified initialization for PaddleOCR 3.x compatibility
        self.ocr = PaddleOCR(lang=lang)

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
        import gc
        import tempfile

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image from {image_path}")

        # Resize large images to prevent memory issues
        # Max dimension: 1920 pixels (maintains aspect ratio)
        max_dimension = 1920
        height, width = image.shape[:2]
        scale = 1.0

        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(
                image, (new_width, new_height), interpolation=cv2.INTER_AREA
            )

            # Save resized image to temp file for OCR
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                temp_path = tmp.name
                cv2.imwrite(temp_path, image)

            # Use temp file for OCR
            ocr_input = temp_path
        else:
            ocr_input = image_path
            temp_path = None

        try:
            # Run OCR
            # Note: cls parameter removed in PaddleOCR 3.x (text direction classification is automatic)
            result = self.ocr.ocr(ocr_input)
        finally:
            # Clean up temp file and force garbage collection
            if temp_path:
                import os

                try:
                    os.unlink(temp_path)
                except:
                    pass
            del image
            gc.collect()

        if not result or not result[0]:
            return []

        ocr_result = result[0]
        text_regions = []

        # PaddleOCR 3.x returns OCRResult object (dict-like)
        # Check if it's the new format (dict with rec_polys, rec_texts, rec_scores)
        if isinstance(ocr_result, dict):
            # New format: PaddleOCR 3.x OCRResult object
            boxes = ocr_result.get("rec_polys", ocr_result.get("dt_polys", []))
            texts = ocr_result.get("rec_texts", [])
            scores = ocr_result.get("rec_scores", [])

            if not boxes or not texts:
                return []

            for i in range(len(texts)):
                try:
                    bbox = boxes[i]
                    text = texts[i]
                    confidence = scores[i] if i < len(scores) else 1.0

                    # Scale bbox back to original image coordinates if image was resized
                    if scale != 1.0:
                        bbox = [[x / scale, y / scale] for x, y in bbox]

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
                except (IndexError, TypeError, ValueError) as e:
                    import warnings

                    warnings.warn(f"Skipping malformed OCR result: {e}", RuntimeWarning)
                    continue

        elif isinstance(ocr_result, list):
            # Old format: list of [bbox, (text, confidence)]
            for line in ocr_result:
                try:
                    bbox = line[0]
                    text_info = line[1]

                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text = text_info[0]
                        confidence = text_info[1]
                    elif isinstance(text_info, str):
                        text = text_info
                        confidence = 1.0
                    else:
                        continue

                    # Scale bbox back to original image coordinates if image was resized
                    if scale != 1.0:
                        bbox = [[x / scale, y / scale] for x, y in bbox]

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
                except (IndexError, TypeError, ValueError) as e:
                    import warnings

                    warnings.warn(f"Skipping malformed OCR result: {e}", RuntimeWarning)
                    continue

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
