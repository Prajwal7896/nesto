
import * as THREE from "three";

const MM = 0.001;

const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x343d48,
    metalness: 0.8,
    roughness: 0.3
});

const glassMaterial = new THREE.MeshPhysicalMaterial({
    color: 0x9bd8ed,
    metalness: 0.05,
    roughness: 0.08,
    transmission: 0.35,
    transparent: true,
    opacity: 0.48,
    thickness: 0.04,
    side: THREE.DoubleSide,
    depthWrite: false
});

const handleMaterial = new THREE.MeshStandardMaterial({
    color: 0xc5cbd2,
    metalness: 0.9,
    roughness: 0.2
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

function createWindowPanel(parent, width, height, thickness, x, frameSize, id) {
    const panelGroup = new THREE.Group();
    panelGroup.position.x = x;
    parent.add(panelGroup);

    const glassWidth = Math.max(width - frameSize * 2, 0.05);
    const glassHeight = Math.max(height - frameSize * 2, 0.05);

    const glass = addBox(
        panelGroup,
        glassWidth,
        glassHeight,
        0.018,
        0,
        0,
        0,
        glassMaterial
    );

    glass.userData.type = "window-panel";
    glass.userData.windowId = id;

    // Sash frame
    addBox(
        panelGroup, width, frameSize, thickness,
        0, height / 2 - frameSize / 2, 0, frameMaterial
    );

    addBox(
        panelGroup, width, frameSize, thickness,
        0, -height / 2 + frameSize / 2, 0, frameMaterial
    );

    addBox(
        panelGroup, frameSize, height, thickness,
        -width / 2 + frameSize / 2, 0, 0, frameMaterial
    );

    addBox(
        panelGroup, frameSize, height, thickness,
        width / 2 - frameSize / 2, 0, 0, frameMaterial
    );

    // Handle
    addBox(
        panelGroup,
        0.025,
        0.09,
        0.035,
        width / 2 - frameSize - 0.06,
        0,
        0.035,
        handleMaterial
    );

    return { group: panelGroup, glass };
}

export function createWindows(sceneData, houseGroup) {
    const windows = [];
    const processed = new Set();

    for (const floor of sceneData.floors || []) {
        const elevation = Number(floor.elevation || 0) * MM;

        for (const wall of floor.walls || []) {
            if (!wall.start || !wall.end) continue;

            const startX = Number(wall.start[0]) * MM;
            const startZ = Number(wall.start[1]) * MM;
            const endX = Number(wall.end[0]) * MM;
            const endZ = Number(wall.end[1]) * MM;

            const dx = endX - startX;
            const dz = endZ - startZ;
            const wallLength = Math.hypot(dx, dz);

            if (wallLength <= 0) continue;

            const rotation = -Math.atan2(dz, dx);

            for (const opening of wall.openings || []) {
                if (opening.kind !== "window") continue;
                if (processed.has(opening.id)) continue;

                processed.add(opening.id);

                const width = Number(opening.width) * MM;
                const height = Number(opening.height) * MM;
                const sill = Number(opening.sill_height || 0) * MM;

                if (width <= 0 || height <= 0) continue;

                const position = Math.max(
                    0,
                    Math.min(1, Number(opening.position ?? 0.5))
                );

                const openingStart = wallLength * position - width / 2;

                const frameSize = 0.055;
                const frameDepth = Math.max(
                    Number(wall.thickness || 150) * MM * 1.15,
                    0.12
                );

                const root = new THREE.Group();

                root.position.set(
                    startX + (dx / wallLength) * openingStart,
                    elevation + sill,
                    startZ + (dz / wallLength) * openingStart
                );

                root.rotation.y = rotation;
                root.userData.type = "window";
                root.userData.windowId = opening.id;

                // Outer frame
                addBox(
                    root, frameSize, height, frameDepth,
                    frameSize / 2, height / 2, 0, frameMaterial
                );

                addBox(
                    root, frameSize, height, frameDepth,
                    width - frameSize / 2, height / 2, 0, frameMaterial
                );

                addBox(
                    root, width, frameSize, frameDepth,
                    width / 2, height - frameSize / 2, 0, frameMaterial
                );

                addBox(
                    root, width, frameSize, frameDepth,
                    width / 2, frameSize / 2, 0, frameMaterial
                );

                // Two independently sliding panels
                const panelWidth = width / 2;
                const panelY = height / 2;
                const panelOffset = panelWidth / 2;

                const left = createWindowPanel(
                    root,
                    panelWidth,
                    height - frameSize * 2,
                    0.045,
                    panelOffset,
                    frameSize * 0.65,
                    opening.id
                );

                const right = createWindowPanel(
                    root,
                    panelWidth,
                    height - frameSize * 2,
                    0.045,
                    panelOffset + panelWidth,
                    frameSize * 0.65,
                    opening.id
                );

                // Position panels vertically inside the outer frame
                left.group.position.y = panelY;
                right.group.position.y = panelY;

                // Keep both panels in front of the outer frame.
                left.group.position.z = 0.035;
                right.group.position.z = 0.035;

                // Store animation targets.
                const windowData = {
                    id: opening.id,
                    root,
                    panels: [left.group, right.group],
                    glass: [left.glass, right.glass],
                    open: false,
                    closedPositions: [
                        left.group.position.x,
                        right.group.position.x
                    ],
                    openDistance: panelWidth * 0.85
                };

                root.userData.windowData = windowData;

                houseGroup.add(root);
                windows.push(windowData);
            }
        }
    }

    console.log("[NESTO] Interactive windows created:", windows.length);

    return windows;
}
