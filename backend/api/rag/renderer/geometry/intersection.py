from math import sqrt

from .point import Point
from .line import Line
from .circle import Circle


EPSILON = 1e-9


def line_line(line1: Line, line2: Line):
    """
    Returns intersection point of two line segments.
    """

    x1, y1 = line1.start.x, line1.start.y
    x2, y2 = line1.end.x, line1.end.y

    x3, y3 = line2.start.x, line2.start.y
    x4, y4 = line2.end.x, line2.end.y

    denominator = (
        (x1 - x2) * (y3 - y4)
        -
        (y1 - y2) * (x3 - x4)
    )

    if abs(denominator) < EPSILON:
        return None

    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4)
        -
        (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denominator

    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4)
        -
        (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denominator

    p = Point(px, py)

    if (
        line1.contains_point(p)
        and
        line2.contains_point(p)
    ):
        return p

    return None


def line_circle(
    line: Line,
    circle: Circle
):
    """
    Returns intersection points.
    """

    dx = line.end.x - line.start.x
    dy = line.end.y - line.start.y

    fx = line.start.x - circle.center.x
    fy = line.start.y - circle.center.y

    a = dx * dx + dy * dy

    b = 2 * (
        fx * dx +
        fy * dy
    )

    c = (
        fx * fx +
        fy * fy -
        circle.radius ** 2
    )

    discriminant = b * b - 4 * a * c

    if discriminant < 0:
        return []

    discriminant = sqrt(discriminant)

    t1 = (-b - discriminant) / (2 * a)

    t2 = (-b + discriminant) / (2 * a)

    points = []

    if 0 <= t1 <= 1:
        points.append(
            Point(
                line.start.x + dx * t1,
                line.start.y + dy * t1
            )
        )

    if 0 <= t2 <= 1 and discriminant > EPSILON:
        points.append(
            Point(
                line.start.x + dx * t2,
                line.start.y + dy * t2
            )
        )

    return points


def circle_circle(
    c1: Circle,
    c2: Circle
):
    """
    Returns circle intersection points.
    """

    d = c1.center.distance_to(c2.center)

    if d > c1.radius + c2.radius:
        return []

    if d < abs(c1.radius - c2.radius):
        return []

    if d == 0:
        return []

    a = (
        c1.radius ** 2
        -
        c2.radius ** 2
        +
        d ** 2
    ) / (2 * d)

    h_sq = c1.radius ** 2 - a ** 2

    if h_sq < 0:
        return []

    h = sqrt(h_sq)

    px = c1.center.x + a * (
        c2.center.x - c1.center.x
    ) / d

    py = c1.center.y + a * (
        c2.center.y - c1.center.y
    ) / d

    rx = -(
        c2.center.y - c1.center.y
    ) * h / d

    ry = (
        c2.center.x - c1.center.x
    ) * h / d

    p1 = Point(px + rx, py + ry)

    p2 = Point(px - rx, py - ry)

    if p1 == p2:
        return [p1]

    return [p1, p2]


def rectangles_intersect(
    r1,
    r2
):

    return (
        r1.bounding_box.intersects(
            r2.bounding_box
        )
    )


def bounding_boxes_intersect(
    b1,
    b2
):

    return b1.intersects(b2)