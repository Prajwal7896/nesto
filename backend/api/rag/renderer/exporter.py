
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt

from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.svg import SVGBackend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


class Exporter:

    def __init__(self, doc, output_dir="output"):

        self.doc = doc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_dxf(self, filename="floorplan.dxf"):

        path = self.output_dir / filename

        try:
            self.doc.saveas(str(path))
            return str(path)

        except Exception as error:
            raise RuntimeError(
                f"DXF export failed: {error}"
            ) from error

    def export_json(self, data, filename="floorplan.json"):

        path = self.output_dir / filename

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, default=str)

            return str(path)

        except Exception as error:
            raise RuntimeError(
                f"JSON export failed: {error}"
            ) from error

    def export_svg(self, path):

        from ezdxf.addons.drawing.layout import Page

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            backend = SVGBackend()
            context = RenderContext(self.doc)

            frontend = Frontend(context, backend)

            frontend.draw_layout(
                self.doc.modelspace(),
                finalize=True
            )

            page = Page(210, 297)

            svg_string = backend.get_string(page)

            path.write_text(
                svg_string,
                encoding="utf-8"
            )

            return str(path)

        except Exception as error:
            raise RuntimeError(
                f"SVG export failed: {error}"
            ) from error

    def export_png(self, filename="floorplan.png", dpi=300):

        path = self.output_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        fig = None

        try:
            fig = plt.figure(figsize=(12, 12))

            ax = fig.add_axes([0, 0, 1, 1])

            context = RenderContext(self.doc)

            backend = MatplotlibBackend(ax)

            frontend = Frontend(context, backend)

            frontend.draw_layout(
                self.doc.modelspace(),
                finalize=True
            )

            ax.set_aspect("equal", adjustable="datalim")
            ax.autoscale_view()
            ax.axis("off")

            fig.savefig(
                str(path),
                dpi=dpi,
                bbox_inches="tight",
                pad_inches=0.2,
                facecolor="white"
            )

            return str(path)

        except Exception as error:
            raise RuntimeError(
                f"PNG export failed: {error}"
            ) from error

        finally:
            if fig is not None:
                plt.close(fig)

    def export_all(self, base_name="floorplan", metadata=None):

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
