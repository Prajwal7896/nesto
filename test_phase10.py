from backend.api.three_d.exporters import SceneExporter

scene = {
    "name": "Nesto Test House",
    "units": "mm",
    "objects": [
        {
            "id": "wall_1",
            "name": "Test Wall",
            "geometry": {
                "vertices": [
                    [0, 0, 0],
                    [3000, 0, 0],
                    [3000, 2800, 0],
                    [0, 2800, 0]
                ],
                "faces": [
                    [0, 1, 2],
                    [0, 2, 3]
                ]
            },
            "material": {
                "name": "concrete",
                "color": "#999999",
                "roughness": 0.9,
                "metalness": 0.0
            }
        }
    ]
}

exporter = SceneExporter(units="mm")

for file_format in ("json", "gltf", "glb"):
    result = exporter.export(
        scene,
        f"output/test_house.{file_format}"
    )
    print(result)
