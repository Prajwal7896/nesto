from math import sqrt, atan2, degrees, radians, sin, cos

from .point import Point


EPSILON = 1e-9


def almost_equal(a, b, tolerance=EPSILON):

    return abs(a - b) <= tolerance


def clamp(value, minimum, maximum):

    return max(minimum, min(value, maximum))


def distance(p1: Point, p2: Point):

    return sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def midpoint(p1: Point, p2: Point):

    return Point(
        (p1.x + p2.x) / 2,
        (p1.y + p2.y) / 2
    )


def angle_between_points(
    p1: Point,
    p2: Point
):

    return degrees(
        atan2(
            p2.y - p1.y,
            p2.x - p1.x
        )
    )


def polar_point(
    origin: Point,
    distance: float,
    angle: float
):

    angle = radians(angle)

    return Point(
        origin.x + distance * cos(angle),
        origin.y + distance * sin(angle)
    )


def lerp(a, b, t):

    return a + (b - a) * t


def lerp_point(
    p1: Point,
    p2: Point,
    t: float
):

    return Point(
        lerp(p1.x, p2.x, t),
        lerp(p1.y, p2.y, t)
    )


def polygon_centroid(points):

    x = sum(
        p.x for p in points
    ) / len(points)

    y = sum(
        p.y for p in points
    ) / len(points)

    return Point(x, y)


def polygon_area(points):

    area = 0

    n = len(points)

    for i in range(n):

        j = (i + 1) % n

        area += (
            points[i].x *
            points[j].y
        )

        area -= (
            points[j].x *
            points[i].y
        )

    return abs(area) / 2


def bounding_box(points):

    xs = [p.x for p in points]
    ys = [p.y for p in points]

    return (
        min(xs),
        min(ys),
        max(xs),
        max(ys)
    )


def remove_duplicate_points(
    points,
    tolerance=EPSILON
):

    result = []

    for p in points:

        if not any(
            distance(p, q) <= tolerance
            for q in result
        ):
            result.append(p)

    return result