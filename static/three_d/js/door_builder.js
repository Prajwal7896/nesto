
import * as THREE from "three";

const MM = 0.001;

const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x795b3d,
    roughness: 0.75
});

const doorMaterial = new THREE.MeshStandardMaterial({
    color: 0x9b704b,
    roughness: 0.65
});

const metalMaterial = new THREE.MeshStandardMaterial({
    color: 0xb9bec5,
    metalness: 0.8,
    roughness: 0.25
});

function addBox(parent, width, height, depth, x, y, z, material) {
    const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(width, height, depth),
        material
    );

    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);

    return mesh;
}

export function createDoors(sceneData, houseGroup) {
    const doorPanels = [];
    const processed = new Set();

    for (const floor of sceneData.floors || []) {
        const elevation = Number(floor.elevation || 0) * MM;

        for (const wall of floor.walls || []) {
            if (!wall.start || !wall.end) continue;

            const startX = wall.start[0] * MM;
            const startZ = wall.start[1] * MM;
            const endX = wall.end[0] * MM;
            const endZ = wall.end[1] * MM;

            const dx = endX - startX;
            const dz = endZ - startZ;
            const wallLength = Math.hypot(dx, dz);

            if (wallLength <= 0) continue;

            const ux = dx / wallLength;
            const uz = dz / wallLength;

            const rotation = -Math.atan2(uz, ux);

            for (const opening of wall.openings || []) {
                if (opening.kind !== "door") continue;
                if (processed.has(opening.id)) continue;

                processed.add(opening.id);

                const width = Number(opening.width) * MM;
                const height = Number(opening.height) * MM;
                const thickness = Math.max(
                    Number(wall.thickness || 150) * MM,
                    0.12
                );

                if (width <= 0 || height <= 0) continue;

                const position = Math.max(
                    0,
                    Math.min(1, Number(opening.position ?? 0.5))
                );

                const center = wallLength * position;
                const openingStart = center - width / 2;

                const root = new THREE.Group();

                root.position.set(
                    startX + ux * openingStart,
                    elevation,
                    startZ + uz * openingStart
                );

                root.rotation.y = rotation;
                root.userData.type = "door";
                root.userData.doorId = opening.id;

                const frameWidth = 0.065;
                const frameDepth = thickness * 1.2;

                // Left and right frame posts
                addBox(
                    root, frameWidth, height, frameDepth,
                    frameWidth / 2, height / 2, 0, frameMaterial
                );

                addBox(
                    root, frameWidth, height, frameDepth,
                    width - frameWidth / 2, height / 2, 0, frameMaterial
                );

                // Top frame
                addBox(
                    root, width, frameWidth, frameDepth,
                    width / 2, height - frameWidth / 2, 0,
                    frameMaterial
                );

                // Hinged door panel
                const hinge = new THREE.Group();
                root.add(hinge);

                const panel = addBox(
                    hinge,
                    width - frameWidth * 2,
                    height - frameWidth,
                    0.045,
                    (width - frameWidth * 2) / 2,
                    (height - frameWidth) / 2,
                    0,
                    doorMaterial
                );

                panel.userData.doorId = opening.id;
                panel.userData.type = "door-panel";

                // Handle
                addBox(
                    hinge,
                    0.035, 0.12, 0.055,
                    width - frameWidth - 0.11,
                    height * 0.48,
                    0.045,
                    metalMaterial
                );

                // Decorative hinges
                for (const hingeY of [0.25, height - 0.35]) {
                    addBox(
                        hinge,
                        0.035, 0.09, 0.035,
                        0.025, hingeY, 0.035,
                        metalMaterial
                    );
                }

                hinge.userData.doorId = opening.id;
                hinge.userData.open = false;
                hinge.userData.targetRotation = 0;

                root.userData.hinge = hinge;

                houseGroup.add(root);

                doorPanels.push({
                    id: opening.id,
                    panel,
                    hinge,
                    root
                });
            }
        }
    }

    console.log("[NESTO] Interactive doors created:", doorPanels.length);

    return doorPanels;
}
