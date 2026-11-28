import ezdxf


DEFAULT_LAYERS = {
    "WALLS": {
        "color": 7,
        "linetype": "CONTINUOUS",
    },
    "DOORS": {
        "color": 2,
        "linetype": "CONTINUOUS",
    },
    "WINDOWS": {
        "color": 4,
        "linetype": "CONTINUOUS",
    },
    "ROOMS": {
        "color": 3,
        "linetype": "CONTINUOUS",
    },
    "FURNITURE": {
        "color": 30,
        "linetype": "CONTINUOUS",
    },
    "STAIRCASE": {
        "color": 6,
        "linetype": "CONTINUOUS",
    },
    "ROOF": {
        "color": 1,
        "linetype": "CONTINUOUS",
    },
    "SLAB": {
        "color": 8,
        "linetype": "CONTINUOUS",
    },
    "DIMENSIONS": {
        "color": 5,
        "linetype": "CONTINUOUS",
    },
    "TEXT": {
        "color": 2,
        "linetype": "CONTINUOUS",
    },
    "LABELS": {
        "color": 140,
        "linetype": "CONTINUOUS",
    },
    "HATCH": {
        "color": 252,
        "linetype": "CONTINUOUS",
    },
    "GRID": {
        "color": 9,
        "linetype": "DASHED",
    },
    "CENTERLINES": {
        "color": 151,
        "linetype": "CENTER",
    },
    "ELECTRICAL": {
        "color": 1,
        "linetype": "CONTINUOUS",
    },
    "PLUMBING": {
        "color": 5,
        "linetype": "CONTINUOUS",
    },
    "HVAC": {
        "color": 4,
        "linetype": "CONTINUOUS",
    },
    "ANNOTATION": {
        "color": 30,
        "linetype": "CONTINUOUS",
    }
}


class LayerManager:

    def __init__(self, doc: ezdxf.EzDxf):

        self.doc = doc

    def create_layer(
        self,
        name,
        color=7,
        linetype="CONTINUOUS"
    ):

        if name not in self.doc.layers:

            self.doc.layers.new(
                name=name,
                dxfattribs={
                    "color": color,
                    "linetype": linetype
                }
            )

    def create_default_layers(self):

        for layer, cfg in DEFAULT_LAYERS.items():

            self.create_layer(
                layer,
                cfg["color"],
                cfg["linetype"]
            )

    def exists(
        self,
        name
    ):

        return name in self.doc.layers

    def delete(
        self,
        name
    ):

        if name in self.doc.layers:

            self.doc.layers.remove(name)

    def rename(
        self,
        old,
        new
    ):

        if old in self.doc.layers:

            self.doc.layers.get(old).rename(new)

    def set_color(
        self,
        layer,
        color
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).dxf.color = color

    def set_linetype(
        self,
        layer,
        linetype
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).dxf.linetype = linetype

    def lock(
        self,
        layer
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).lock()

    def unlock(
        self,
        layer
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).unlock()

    def freeze(
        self,
        layer
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).freeze()

    def thaw(
        self,
        layer
    ):

        if layer in self.doc.layers:

            self.doc.layers.get(layer).thaw()

    def list_layers(self):

        return [
            layer.dxf.name
            for layer in self.doc.layers
        ]