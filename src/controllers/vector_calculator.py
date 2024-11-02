import numpy as np


class VectorCalculator:
    @staticmethod
    def calculate_vectors(lengths, is_clockwise):
        """
        Calculate vectors from lengths and direction

        Args:
            lengths (list): List of three vector lengths
            is_clockwise (bool): Direction of rotation

        Returns:
            ndarray: 3x2 array of vector coordinates
        """
        vectors = np.zeros((3, 2))
        angle = 0

        for i, length in enumerate(lengths):
            radians = np.radians(angle)
            vectors[i] = [
                length * np.cos(radians),
                length * np.sin(radians)
            ]
            angle += -120 if is_clockwise else 120

        return vectors

    @staticmethod
    def calculate_resultant(vectors):
        """
        Calculate resultant vector from array of vectors

        Args:
            vectors (ndarray): Array of vectors

        Returns:
            ndarray: Resultant vector coordinates
        """
        return np.sum(vectors, axis=0)

    @staticmethod
    def rotate_vector(vector, angle_degrees):
        """
        Rotate vector by given angle

        Args:
            vector (ndarray): Vector to rotate
            angle_degrees (float): Rotation angle in degrees

        Returns:
            ndarray: Rotated vector coordinates
        """
        angle_rad = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        return np.dot(rotation_matrix, vector)

    @staticmethod
    def vector_magnitude(vector):
        """
        Calculate vector magnitude

        Args:
            vector (ndarray): Input vector

        Returns:
            float: Vector magnitude
        """
        return np.linalg.norm(vector)

    @staticmethod
    def vector_angle(vector):
        """
        Calculate vector angle in degrees

        Args:
            vector (ndarray): Input vector

        Returns:
            float: Angle in degrees
        """
        return np.degrees(np.arctan2(vector[1], vector[0])) % 360