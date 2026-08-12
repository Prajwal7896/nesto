import json
from pathlib import Path

from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.svg import SVGBackend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
class Exporter:

    def __init__(self, doc, output_dir="output"):

        self.doc = doc
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    def export_dxf(self, filename="floorplan.dxf"):

        path = self.output_dir / filename

        self.doc.saveas(
            str(path)
        )

        return str(path)


    def export_json(self, data, filename="floorplan.json"):

        path = self.output_dir / filename

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

        return str(path)


    def export_svg(self, path):

        from ezdxf.addons.drawing.layout import Page

        path = Path(path)

        try:
            backend = SVGBackend()

            ctx = RenderContext(self.doc)

            Frontend(
                ctx,
                backend
            ).draw_layout(
                self.doc.modelspace()
            )

            page = Page(
                210,   # width (A4)
                297    # height (A4)
            )

            svg_string = backend.get_string(page)

            path.write_text(
                svg_string,
                encoding="utf-8"
            )

            return str(path)

        except Exception as e:
            raise RuntimeError(f"SVG export failed: {e}")

    def export_png(
        self,
        filename="floorplan.png",
        dpi=300
    ):

        path = self.output_dir / filename

        import matplotlib.pyplot as plt


        fig = plt.figure(
            figsize=(12,12)
        )

        ax = fig.add_axes(
            [0,0,1,1]
        )


        ctx = RenderContext(
            self.doc
        )


        backend = MatplotlibBackend(
            ax
        )


        Frontend(
            ctx,
            backend
        ).draw_layout(
            self.doc.modelspace()
        )


        ax.set_aspect(
            "equal"
        )


        ax.autoscale()


        plt.savefig(
            str(path),
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.2
        )


        plt.close(fig)


        return str(path)



    def export_all(
        self,
        base_name="floorplan",
        metadata=None
    ):

        results = {}


        results["dxf"] = self.export_dxf(
            f"{base_name}.dxf"
        )


        results["svg"] = self.export_svg(
            self.output_dir / f"{base_name}.svg"
        )


        results["png"] = self.export_png(
            f"{base_name}.png"
        )


        if metadata:

            results["json"] = self.export_json(
                metadata,
                f"{base_name}.json"
            )


        return results