from typing import List, Tuple, Union
import numpy as np
from functools import lru_cache
from numpy.typing import NDArray


class VectorCalculator:
    """
    Calculator for vector operations with validation and error handling.
    All methods are static and thread-safe.
    """

    EPSILON = 1e-10  # Constant for floating point comparisons

    @staticmethod
    def validate_lengths(lengths: List[float]) -> None:
        """
        Validate vector lengths.

        Args:
            lengths: List of vector lengths

        Raises:
            ValueError: If lengths are invalid
        """
        if not isinstance(lengths, (list, tuple)) or len(lengths) != 3:
            raise ValueError("Must provide exactly 3 vector lengths")
        if not all(isinstance(x, (int, float)) for x in lengths):
            raise ValueError("All lengths must be numeric")
        if any(x < 0 for x in lengths):
            raise ValueError("Vector lengths cannot be negative")

    @staticmethod
    def calculate_vectors(lengths: List[float], is_clockwise: bool) -> NDArray:
        """
        Calculate vectors from lengths and direction.

        Args:
            lengths: List of three vector lengths
            is_clockwise: Direction of rotation

        Returns:
            NDArray: 3x2 array of vector coordinates

        Raises:
            ValueError: If input validation fails
        """
        VectorCalculator.validate_lengths(lengths)

        vectors = np.zeros((3, 2))
        angle = 0

        for i, length in enumerate(lengths):
            if abs(length) < VectorCalculator.EPSILON:
                continue  # Skip zero-length vectors

            radians = np.radians(angle)
            vectors[i] = [
                length * np.cos(radians),
                length * np.sin(radians)
            ]
            angle += -120 if is_clockwise else 120

        return vectors

    @staticmethod
    def calculate_resultant(vectors: NDArray) -> NDArray:
        """
        Calculate resultant vector from array of vectors.

        Args:
            vectors: Array of vectors

        Returns:
            NDArray: Resultant vector coordinates

        Raises:
            ValueError: If vectors array is invalid
        """
        if not isinstance(vectors, np.ndarray):
            raise ValueError("Vectors must be a numpy array")
        if vectors.shape[1] != 2:
            raise ValueError("Each vector must have 2 coordinates")

        resultant = np.sum(vectors, axis=0)
        if np.all(np.abs(resultant) < VectorCalculator.EPSILON):
            return np.zeros(2)  # Return zero vector explicitly

        return resultant

    @staticmethod
    @lru_cache(maxsize=128)
    def _calculate_rotation_matrix(angle_degrees: float) -> NDArray:
        """
        Calculate and cache rotation matrix for given angle.

        Args:
            angle_degrees: Rotation angle in degrees

        Returns:
            NDArray: 2x2 rotation matrix
        """
        angle_rad = np.radians(angle_degrees)
        return np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])

    @staticmethod
    def rotate_vector(vector: NDArray, angle_degrees: float) -> NDArray:
        """
        Rotate vector by given angle.

        Args:
            vector: Vector to rotate
            angle_degrees: Rotation angle in degrees

        Returns:
            NDArray: Rotated vector coordinates

        Raises:
            ValueError: If vector is invalid
        """
        if not isinstance(vector, np.ndarray) or vector.shape != (2,):
            raise ValueError("Vector must be a 2D numpy array")

        if np.all(np.abs(vector) < VectorCalculator.EPSILON):
            return np.zeros(2)  # No need to rotate zero vector

        rotation_matrix = VectorCalculator._calculate_rotation_matrix(angle_degrees)
        return np.dot(rotation_matrix, vector)

    @staticmethod
    def vector_magnitude(vector: NDArray) -> float:
        """
        Calculate vector magnitude.

        Args:
            vector: Input vector

        Returns:
            float: Vector magnitude

        Raises:
            ValueError: If vector is invalid
        """
        if not isinstance(vector, np.ndarray):
            raise ValueError("Vector must be a numpy array")

        magnitude = np.linalg.norm(vector)
        return 0.0 if magnitude < VectorCalculator.EPSILON else magnitude

    @staticmethod
    def vector_angle(vector: NDArray) -> float:
        """
        Calculate vector angle in degrees.

        Args:
            vector: Input vector

        Returns:
            float: Angle in degrees [0, 360)

        Raises:
            ValueError: If vector is invalid or zero vector
        """
        if not isinstance(vector, np.ndarray) or vector.shape != (2,):
            raise ValueError("Vector must be a 2D numpy array")

        if np.all(np.abs(vector) < VectorCalculator.EPSILON):
            raise ValueError("Cannot calculate angle for zero vector")

        return np.degrees(np.arctan2(vector[1], vector[0])) % 360