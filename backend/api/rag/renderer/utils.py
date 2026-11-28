import math
import uuid
import logging
from pathlib import Path

MM = "mm"
CM = "cm"
M = "m"


def generate_id():
    return str(uuid.uuid4())


def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def midpoint(p1, p2):
    return (
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2
    )


def angle(p1, p2):
    return math.degrees(
        math.atan2(
            p2[1] - p1[1],
            p2[0] - p1[0]
        )
    )


def mm_to_cm(value):
    return value / 10


def cm_to_mm(value):
    return value * 10


def mm_to_m(value):
    return value / 1000


def m_to_mm(value):
    return value * 1000


def rotate_point(point, angle_deg, origin=(0, 0)):
    angle_rad = math.radians(angle_deg)

    x = point[0] - origin[0]
    y = point[1] - origin[1]

    xr = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    yr = x * math.sin(angle_rad) + y * math.cos(angle_rad)

    return (
        xr + origin[0],
        yr + origin[1]
    )


def translate_point(point, dx, dy):
    return (
        point[0] + dx,
        point[1] + dy
    )


def polygon_area(points):
    area = 0

    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]

        area += x1 * y2
        area -= y1 * x2

    return abs(area) / 2


def bounding_box(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys)
    }


def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def setup_logger(name="renderer"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger()