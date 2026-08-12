from math import radians, sin, cos

from .point import Point


def translate_point(
    point: Point,
    dx: float,
    dy: float
) -> Point:

    return Point(
        point.x + dx,
        point.y + dy
    )


def scale_point(
    point: Point,
    factor: float,
    origin: Point = Point(0, 0)
) -> Point:

    return Point(
        origin.x + (point.x - origin.x) * factor,
        origin.y + (point.y - origin.y) * factor
    )


def rotate_point(
    point: Point,
    angle: float,
    origin: Point = Point(0, 0)
) -> Point:

    angle = radians(angle)

    tx = point.x - origin.x
    ty = point.y - origin.y

    rx = tx * cos(angle) - ty * sin(angle)
    ry = tx * sin(angle) + ty * cos(angle)

    return Point(
        rx + origin.x,
        ry + origin.y
    )


def mirror_x(point: Point) -> Point:

    return Point(
        point.x,
        -point.y
    )


def mirror_y(point: Point) -> Point:

    return Point(
        -point.x,
        point.y
    )


def translate_points(
    points,
    dx,
    dy
):

    return [
        translate_point(p, dx, dy)
        for p in points
    ]


def scale_points(
    points,
    factor,
    origin=Point(0, 0)
):

    return [
        scale_point(
            p,
            factor,
            origin
        )
        for p in points
    ]


def rotate_points(
    points,
    angle,
    origin=Point(0, 0)
):

    return [
        rotate_point(
            p,
            angle,
            origin
        )
        for p in points
    ]


def mirror_points_x(points):

    return [
        mirror_x(p)
        for p in points
    ]


def mirror_points_y(points):

    return [
        mirror_y(p)
        for p in points
    ]


def centroid(points):

    x = sum(
        p.x for p in points
    ) / len(points)

    y = sum(
        p.y for p in points
    ) / len(points)

    return Point(x, y)