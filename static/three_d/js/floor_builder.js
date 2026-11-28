import * as THREE from "three";

const MM = 0.001;

export function buildFloors(sceneData, houseGroup) {
    let count = 0;

    const materials = [
        0xd8cbb8,
        0xc9d7df,
        0xd8d0c1,
        0xc8d6c5
    ];

    for (const [floorIndex, floor] of (sceneData.floors || []).entries()) {
        const elevation = Number(floor.elevation || 0) * MM;

        for (const room of floor.rooms || []) {
            const polygon = room.polygon || room.points || room.vertices || [];

            if (polygon.length < 3) {
                console.warn("[NESTO 3D] Room has no renderable polygon", {
                    roomId: room.id,
                    polygonPoints: polygon.length
                });
                continue;
            }

            const vertices = polygon.map(point => {
                const x = Number(Array.isArray(point) ? point[0] : point.x);
                const z = Number(Array.isArray(point) ? point[1] : (point.y ?? point.z));

                return new THREE.Vector2(x * MM, z * MM);
            });

            if (vertices.some(p => !Number.isFinite(p.x) || !Number.isFinite(p.y))) {
                console.warn("[NESTO 3D] Invalid floor polygon coordinates", { roomId: room.id });
                continue;
            }

            const shape = new THREE.Shape(vertices);
            const geometry = new THREE.ShapeGeometry(shape);

            // ShapeGeometry lies in XY. Keep plan Z aligned with walls and furniture.
            geometry.rotateX(-Math.PI / 2);
            geometry.computeVertexNormals();

            const mesh = new THREE.Mesh(
                geometry,
                new THREE.MeshStandardMaterial({
                    color: materials[count % materials.length],
                    roughness: 0.85,
                    side: THREE.DoubleSide
                })
            );

            mesh.position.set(0, elevation + 0.001, 0);
            mesh.receiveShadow = true;
            mesh.name = "Floor_" + floorIndex + "_" + (room.id || count);

            mesh.userData = {
                layer: "floors",
                roomId: room.id,
                floorIndex
            };

            houseGroup.add(mesh);
            count++;
        }
    }

    console.info("[NESTO 3D] Floor mesh creation complete", {
        floorMeshes: count,
        roomCount: (sceneData.floors || []).reduce((n, floor) => n + (floor.rooms?.length || 0), 0)
    });
    return count;
}

