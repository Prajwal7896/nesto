import ezdxf
import svgwrite


def convert_dxf_to_svg(
    dxf_path,
    svg_path
):

    doc = ezdxf.readfile(dxf_path)

    msp = doc.modelspace()


    dwg = svgwrite.Drawing(
        svg_path,
        profile="tiny"
    )


    for entity in msp:

        if entity.dxftype() == "LINE":

            start = entity.dxf.start
            end = entity.dxf.end

            dwg.add(
                dwg.line(
                    start=(start.x, -start.y),
                    end=(end.x, -end.y),
                    stroke="black"
                )
            )


        elif entity.dxftype() == "LWPOLYLINE":

            points = [
                (p[0], -p[1])
                for p in entity.get_points()
            ]

            dwg.add(
                dwg.polyline(
                    points,
                    fill="none",
                    stroke="black"
                )
            )


    dwg.save()