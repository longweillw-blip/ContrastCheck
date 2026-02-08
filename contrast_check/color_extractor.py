"""
Color extraction module using K-means clustering.
"""

from typing import List, Tuple

import cv2
import numpy as np
from sklearn.cluster import KMeans


class ColorExtractor:
    """
    Extract text and background colors using K-means clustering.
    """

    def __init__(self, n_text_colors: int = 3, n_bg_colors: int = 3):
        """
        Initialize color extractor.

        Args:
            n_text_colors: Number of clusters for text color extraction
            n_bg_colors: Number of clusters for background color extraction
        """
        self.n_text_colors = n_text_colors
        self.n_bg_colors = n_bg_colors

    def extract_text_color(
        self, image: np.ndarray, text_mask: np.ndarray
    ) -> Tuple[int, int, int]:
        """
        Extract dominant text color from the masked region.

        Args:
            image: Input image (BGR format)
            text_mask: Binary mask indicating text region

        Returns:
            RGB tuple of the dominant text color
        """
        # Extract pixels in text region
        text_pixels = image[text_mask]

        if len(text_pixels) == 0:
            return (0, 0, 0)

        # Convert BGR to RGB
        text_pixels_rgb = cv2.cvtColor(
            text_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2RGB
        ).reshape(-1, 3)

        # Use K-means to find dominant colors
        kmeans = KMeans(
            n_clusters=min(self.n_text_colors, len(text_pixels)),
            random_state=42,
            n_init=10,
        )
        kmeans.fit(text_pixels_rgb)

        # Get the most common cluster (dominant color)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        dominant_cluster = np.argmax(counts)
        dominant_color = kmeans.cluster_centers_[dominant_cluster]

        return tuple(dominant_color.astype(int))

    def extract_background_color(
        self,
        image: np.ndarray,
        text_mask: np.ndarray,
        bbox: List[List[float]],
        margin: int = 10,
    ) -> Tuple[int, int, int]:
        """
        Extract background color around the text region.

        Args:
            image: Input image (BGR format)
            text_mask: Binary mask indicating text region
            bbox: Bounding box coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            margin: Margin around text box for background sampling

        Returns:
            RGB tuple of the dominant background color
        """
        h, w = image.shape[:2]

        # Get bounding box with margin
        bbox_array = np.array(bbox)
        x_min = max(0, int(np.min(bbox_array[:, 0])) - margin)
        x_max = min(w, int(np.max(bbox_array[:, 0])) + margin)
        y_min = max(0, int(np.min(bbox_array[:, 1])) - margin)
        y_max = min(h, int(np.max(bbox_array[:, 1])) + margin)

        # Create background mask (region around text, excluding text itself)
        bg_mask = np.zeros((h, w), dtype=bool)
        bg_mask[y_min:y_max, x_min:x_max] = True
        bg_mask[text_mask] = False

        # Extract background pixels
        bg_pixels = image[bg_mask]

        if len(bg_pixels) == 0:
            return (255, 255, 255)

        # Convert BGR to RGB
        bg_pixels_rgb = cv2.cvtColor(
            bg_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2RGB
        ).reshape(-1, 3)

        # Use K-means to find dominant colors
        kmeans = KMeans(
            n_clusters=min(self.n_bg_colors, len(bg_pixels)), random_state=42, n_init=10
        )
        kmeans.fit(bg_pixels_rgb)

        # Get the most common cluster (dominant color)
        labels = kmeans.labels_
        counts = np.bincount(labels)
        dominant_cluster = np.argmax(counts)
        dominant_color = kmeans.cluster_centers_[dominant_cluster]

        return tuple(dominant_color.astype(int))

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color code.

        Args:
            rgb: RGB tuple

        Returns:
            Hex color code string
        """
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
