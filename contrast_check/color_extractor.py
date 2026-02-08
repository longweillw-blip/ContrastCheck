"""
Color extraction module using K-means clustering.
"""

from typing import List, Tuple

import cv2
import numpy as np
from sklearn.cluster import KMeans


class ColorExtractor:
    """
    Extract dominant colors using K-means clustering.
    """

    def __init__(self, n_colors: int = 2):
        """
        Initialize color extractor.

        Args:
            n_colors: Number of color clusters (default: 2)
        """
        self.n_colors = n_colors

    def _color_distance(
        self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
    ) -> float:
        """
        Calculate Euclidean distance between two RGB colors.

        Args:
            color1: First RGB color tuple
            color2: Second RGB color tuple

        Returns:
            Euclidean distance between colors
        """
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

    def extract_colors(
        self, image: np.ndarray, bbox: List[List[float]], margin: int = 10
    ) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Extract the two dominant colors from a region using K-means.

        Uses K-means clustering to find the two most dominant colors.
        The colors are returned sorted by frequency (most common first).
        ContrastChecker.calculate_contrast_ratio will handle determining
        which color is lighter/darker for proper contrast calculation.

        Args:
            image: Input image (BGR format)
            bbox: Bounding box coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            margin: Margin around text box for sampling (default: 10 pixels)

        Returns:
            Tuple of (color1, color2) as RGB tuples, sorted by frequency
        """
        h, w = image.shape[:2]

        # Get bounding box with margin
        bbox_array = np.array(bbox)
        x_min = max(0, int(np.min(bbox_array[:, 0])) - margin)
        x_max = min(w, int(np.max(bbox_array[:, 0])) + margin)
        y_min = max(0, int(np.min(bbox_array[:, 1])) - margin)
        y_max = min(h, int(np.max(bbox_array[:, 1])) + margin)

        # Extract region pixels
        region = image[y_min:y_max, x_min:x_max]

        if region.size == 0:
            return ((0, 0, 0), (255, 255, 255))

        # Convert BGR to RGB and flatten
        pixels_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB).reshape(-1, 3)

        if len(pixels_rgb) < self.n_colors:
            # Not enough pixels for clustering
            return ((0, 0, 0), (255, 255, 255))

        # Use K-means to find the two dominant colors
        kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels_rgb)

        # Get cluster centers sorted by pixel count
        labels = kmeans.labels_
        counts = np.bincount(labels)

        # Sort clusters by count (descending)
        sorted_indices = np.argsort(counts)[::-1]
        colors = kmeans.cluster_centers_[sorted_indices]

        # Return the two dominant colors
        color1 = tuple(colors[0].astype(int))
        color2 = tuple(colors[1].astype(int)) if len(colors) > 1 else (255, 255, 255)

        # If colors are too similar, try to find more distinct colors
        min_distance = 50  # Minimum Euclidean distance for distinct colors
        if self._color_distance(color1, color2) < min_distance:
            # Try with more clusters and pick the two most distinct ones
            try:
                kmeans_more = KMeans(
                    n_clusters=min(5, len(pixels_rgb)), random_state=42, n_init=10
                )
                kmeans_more.fit(pixels_rgb)
                labels_more = kmeans_more.labels_
                counts_more = np.bincount(labels_more)
                sorted_indices_more = np.argsort(counts_more)[::-1]
                colors_more = kmeans_more.cluster_centers_[sorted_indices_more]

                # Find two colors that are sufficiently different
                best_pair = None
                best_distance = 0
                for i in range(min(3, len(colors_more))):
                    for j in range(i + 1, min(4, len(colors_more))):
                        c1 = tuple(colors_more[i].astype(int))
                        c2 = tuple(colors_more[j].astype(int))
                        dist = self._color_distance(c1, c2)
                        if dist > best_distance:
                            best_distance = dist
                            best_pair = (c1, c2)
                        if dist >= min_distance:
                            return (c1, c2)

                # If we found a better pair, use it
                if best_pair and best_distance >= 10:
                    return best_pair

            except Exception:
                pass

            # Fallback: return white and black if colors are too similar
            if self._color_distance(color1, (255, 255, 255)) > self._color_distance(
                color1, (0, 0, 0)
            ):
                return (color1, (0, 0, 0))
            else:
                return (color1, (255, 255, 255))

        return (color1, color2)

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
