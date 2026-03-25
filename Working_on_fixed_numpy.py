import numpy as np
from typing import Sequence, List


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v if n == 0 else v / n


def project_and_rotate(points, change_code, angle):
    """
    Multi-plane rotation in N-D.
    change_code:
        0 = ignore
        1 = x-dims
        2 = y-dims
    """

    x_idx = [i for i, c in enumerate(change_code) if c == 1]
    y_idx = [i for i, c in enumerate(change_code) if c == 2]

    if not x_idx or not y_idx:
        return points.copy()

    c, s = np.cos(angle), np.sin(angle)
    out = points.copy()

    for xi in x_idx:
        for yi in y_idx:
            x = out[:, xi].copy()
            y = out[:, yi].copy()

            out[:, xi] = x * c - y * s
            out[:, yi] = x * s + y * c

    return out


class Camera:
    def __init__(
        self,
        ndimensions: int,
        camera_center_vector_point: Sequence[float],
        corners_points_positive: List[List[float]],
        corners_points_negative: List[List[float]],
    ):
        self.ndimensions = ndimensions

        self.center = np.array(camera_center_vector_point, dtype=float)

        # These define the screen orientation
        self.screen_x = normalize(
            np.array(corners_points_positive[0], dtype=float)
        )
        self.screen_y = normalize(
            np.array(corners_points_negative[0], dtype=float)
        )

    # ======================
    # Camera transforms
    # ======================

    def move_camera(self, delta):
        self.center += np.array(delta, dtype=float)

    def scale_camera(self, factor):
        self.screen_x *= factor
        self.screen_y *= factor

    # ======================
    # Rotation (THIS is the fix)
    # ======================

    def project_and_rotate_camera(self, change_code, angle):
        """
        Rotate the SCREEN BASIS, not the data.
        """

        basis = np.vstack([self.screen_x, self.screen_y])

        rotated = project_and_rotate(basis, change_code, angle)

        self.screen_x = normalize(rotated[0])
        self.screen_y = normalize(rotated[1])

    # ======================
    # Projection
    # ======================

    def project_point(self, point):
        p = np.array(point, dtype=float) - self.center
        x = np.dot(p, self.screen_x)
        y = np.dot(p, self.screen_y)
        return x, y

    def project_points(self, points):
        pts = np.asarray(points, dtype=float)
        rel = pts - self.center
        xs = rel @ self.screen_x
        ys = rel @ self.screen_y
        return list(zip(xs, ys))
