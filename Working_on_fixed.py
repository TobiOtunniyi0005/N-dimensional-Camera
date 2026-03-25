from typing import Sequence, List
import math


def project_and_rotate(points, change_code, angle):
    """
    Rotate points using multiple x and y dimensions.

    change_code:
        0 -> ignore
        1 -> x-dimension
        2 -> y-dimension
    """

    x_indices = [i for i, c in enumerate(change_code) if c == 1]
    y_indices = [i for i, c in enumerate(change_code) if c == 2]

    if not x_indices or not y_indices:
        return [p[:] for p in points]

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated = []

    for p in points:
        p = p[:]  # copy

        for xi in x_indices:
            for yi in y_indices:
                x = p[xi]
                y = p[yi]

                p[xi] = x * cos_a - y * sin_a
                p[yi] = x * sin_a + y * cos_a

        rotated.append(p)

    return rotated



class Camera:
    def __init__(
        self,
        ndimensions: int,
        camera_center_vector_point: List[float],
        corners_points_positive: List[List[float]],
        corners_points_negative: List[List[float]],
    ):
        self.ndimensions = ndimensions

        self.camera_center_vector_point = camera_center_vector_point
        self.camera_corners_points_positive = corners_points_positive
        self.camera_corners_points_negative = corners_points_negative

    # =========================
    # Camera transforms
    # =========================

    def move_camera(self, delta: Sequence[float]):
        for i in range(self.ndimensions):
            self.camera_center_vector_point[i] += (
                delta[i] if i < len(delta) else 0.0
            )

    def scale_camera(self, factor: float):
        for corner in self.camera_corners_points_positive:
            for i in range(self.ndimensions):
                corner[i] *= factor

        for corner in self.camera_corners_points_negative:
            for i in range(self.ndimensions):
                corner[i] *= factor

    # =========================
    # Rotation (CORE)
    # =========================

    def project_and_rotate_camera(
        self,
        change_code: Sequence[int],
        angle: float
    ) -> None:
        """
        Rotate camera center and corners using the existing algorithm.
        """

        # rotate center
        projected_center = project_and_rotate(
            [self.camera_center_vector_point],
            change_code,
            angle
        )
        if projected_center:
            self.camera_center_vector_point = projected_center[0]

        # rotate corners
        self.camera_corners_points_positive = project_and_rotate(
            self.camera_corners_points_positive,
            change_code,
            angle
        )

        self.camera_corners_points_negative = project_and_rotate(
            self.camera_corners_points_negative,
            change_code,
            angle
        )

    # =========================
    # Projection
    # =========================

    def project_point(self, point):
        """
        Project an N-D point onto the 2D camera screen
        using two independent corner-derived basis vectors.
        """
    
        # Relative vector from camera center
        rel = [
            point[i] - self.camera_center_vector_point[i]
            for i in range(self.ndimensions)
        ]
    
        # Build screen basis vectors
        # Use first positive corner as X axis
        # Use second positive corner (or negative) as Y axis
        x_basis = [
            self.camera_corners_points_positive[0][i]
            - self.camera_center_vector_point[i]
            for i in range(self.ndimensions)
        ]
    
        y_basis = [
            self.camera_corners_points_negative[0][i]
            - self.camera_center_vector_point[i]
            for i in range(self.ndimensions)
        ]
    
        # Normalize basis vectors (VERY important)
        def normalize(v):
            mag = math.sqrt(sum(c * c for c in v))
            return [c / mag for c in v] if mag != 0 else v

        x_basis = normalize(x_basis)
        y_basis = normalize(y_basis)

        # Dot products give screen coordinates
        x = sum(rel[i] * x_basis[i] for i in range(self.ndimensions))
        y = sum(rel[i] * y_basis[i] for i in range(self.ndimensions))

        return x, y


    def project_points(self, points: List[List[float]]):
        return [self.project_point(p) for p in points]
