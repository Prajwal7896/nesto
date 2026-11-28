import * as THREE from "three";

const MM = 0.001;

const MATERIALS = {
    wood: new THREE.MeshStandardMaterial({
        color: 0x98704f,
        roughness: 0.72
    }),
    darkWood: new THREE.MeshStandardMaterial({
        color: 0x543a2b,
        roughness: 0.7
    }),
    fabric: new THREE.MeshStandardMaterial({
        color: 0x777f83,
        roughness: 0.92
    }),
    mattress: new THREE.MeshStandardMaterial({
        color: 0xe8e3d9,
        roughness: 0.95
    }),
    metal: new THREE.MeshStandardMaterial({
        color: 0x9da5aa,
        metalness: 0.7,
        roughness: 0.3
    }),
    glass: new THREE.MeshPhysicalMaterial({
        color: 0xb8dce8,
        roughness: 0.12,
        metalness: 0.05,
        transparent: true,
        opacity: 0.45
    }),
    ceramic: new THREE.MeshStandardMaterial({
        color: 0xf0f0ec,
        roughness: 0.22
    }),
    black: new THREE.MeshStandardMaterial({
        color: 0x292d31,
        roughness: 0.45
    })
};

function addBox(group, material, width, height, depth, x, y, z) {
    const geometry = new THREE.BoxGeometry(
        width * MM,
        height * MM,
        depth * MM
    );

    const mesh = new THREE.Mesh(geometry, material);

    mesh.position.set(
        x * MM,
        y * MM,
        z * MM
    );

    mesh.castShadow = true;
    mesh.receiveShadow = true;

    group.add(mesh);
    return mesh;
}

function addCylinder(group, material, radius, height, x, y, z) {
    const geometry = new THREE.CylinderGeometry(
        radius * MM,
        radius * MM,
        height * MM,
        16
    );

    const mesh = new THREE.Mesh(geometry, material);

    mesh.position.set(x * MM, y * MM, z * MM);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    group.add(mesh);
    return mesh;
}

function buildBed(group, item) {
    const w = item.width;
    const d = item.depth;
    const h = item.height;

    addBox(group, MATERIALS.darkWood, w, 180, d, 0, 90, 0);
    addBox(group, MATERIALS.mattress, w - 80, 220, d - 80, 0, 290, 0);

    // Headboard
    addBox(
        group,
        MATERIALS.wood,
        w,
        h * 0.7,
        100,
        0,
        h * 0.35,
        -d / 2 + 50
    );

    // Pillows
    const pillowWidth = w * 0.32;

    addBox(
        group, MATERIALS.mattress,
        pillowWidth, 90, 450,
        -w * 0.2, 450, -d * 0.3
    );

    addBox(
        group, MATERIALS.mattress,
        pillowWidth, 90, 450,
        w * 0.2, 450, -d * 0.3
    );
}

function buildWardrobe(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, h, d, 0, h / 2, 0);

    addBox(
        group, MATERIALS.darkWood,
        35, h * 0.85, 35,
        0, h / 2, d / 2 + 5
    );

    addCylinder(
        group, MATERIALS.metal,
        12, 100,
        w * 0.3, h * 0.5, d / 2 + 25
    );

    addCylinder(
        group, MATERIALS.metal,
        12, 100,
        -w * 0.3, h * 0.5, d / 2 + 25
    );
}

function buildSofa(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.darkWood, w * 0.92, 180, d * 0.9, 0, 90, 0);
    addBox(group, MATERIALS.fabric, w * 0.88, 220, d * 0.65, 0, 290, d * 0.08);

    addBox(
        group, MATERIALS.fabric,
        w * 0.88, h * 0.55, 180,
        0, h * 0.55, -d * 0.36
    );

    addBox(
        group, MATERIALS.fabric,
        180, h * 0.7, d * 0.9,
        -w * 0.42, h * 0.35, 0
    );

    addBox(
        group, MATERIALS.fabric,
        180, h * 0.7, d * 0.9,
        w * 0.42, h * 0.35, 0
    );
}

function buildTable(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, 65, d, 0, h - 32, 0);

    const legOffsetX = w * 0.4;
    const legOffsetZ = d * 0.35;

    for (const x of [-legOffsetX, legOffsetX]) {
        for (const z of [-legOffsetZ, legOffsetZ]) {
            addBox(
                group, MATERIALS.darkWood,
                65, h - 65, 65,
                x, (h - 65) / 2, z
            );
        }
    }
}

function buildChair(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, 70, d, 0, h * 0.48, 0);

    addBox(
        group, MATERIALS.wood,
        w, h * 0.45, 70,
        0, h * 0.75, -d * 0.42
    );

    for (const x of [-w * 0.38, w * 0.38]) {
        for (const z of [-d * 0.35, d * 0.35]) {
            addBox(
                group, MATERIALS.darkWood,
                45, h * 0.48, 45,
                x, h * 0.24, z
            );
        }
    }
}

function buildCounter(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, h - 80, d, 0, (h - 80) / 2, 0);

    addBox(
        group, MATERIALS.ceramic,
        w + 30, 80, d + 30,
        0, h - 40, 0
    );
}

function buildRefrigerator(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.ceramic, w, h, d, 0, h / 2, 0);

    addBox(
        group, MATERIALS.metal,
        20, h * 0.35, 20,
        w * 0.35, h * 0.7, d / 2 + 15
    );

    addBox(
        group, MATERIALS.metal,
        20, h * 0.35, 20,
        w * 0.35, h * 0.3, d / 2 + 15
    );
}

function buildSink(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, h - 100, d, 0, (h - 100) / 2, 0);

    addBox(
        group, MATERIALS.ceramic,
        w * 0.85, 75, d * 0.8,
        0, h - 40, 0
    );

    addCylinder(
        group, MATERIALS.metal,
        18, 130,
        0, h + 60, -d * 0.25
    );
}

function buildToilet(group, item) {
    const { width: w, depth: d } = item;

    addBox(
        group, MATERIALS.ceramic,
        w * 0.75, 350, d * 0.55,
        0, 175, 0
    );

    const bowl = new THREE.Mesh(
        new THREE.CylinderGeometry(
            w * 0.00038,
            w * 0.00038,
            90 * MM,
            24
        ),
        MATERIALS.ceramic
    );

    bowl.position.set(0, 380 * MM, d * 0.12 * MM);
    group.add(bowl);

    addBox(
        group, MATERIALS.ceramic,
        w * 0.72, 65, d * 0.55,
        0, 430, -d * 0.05
    );
}

function buildShower(group, item) {
    const { width: w, depth: d, height: h } = item;

    // Shower tray
    addBox(
        group, MATERIALS.ceramic,
        w, 70, d,
        0, 35, 0
    );

    // Glass partition panels
    addBox(
        group, MATERIALS.glass,
        35, h, d,
        -w / 2 + 20, h / 2, 0
    );

    addBox(
        group, MATERIALS.glass,
        w, h, 35,
        0, h / 2, -d / 2 + 20
    );

    addCylinder(
        group, MATERIALS.metal,
        35, 100, 0, h - 100, -d / 2 + 100
    );
}

function buildBedsideTable(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, h, d, 0, h / 2, 0);

    addBox(
        group, MATERIALS.darkWood,
        w * 0.8, 35, 35,
        0, h * 0.65, d / 2 + 10
    );
}

function buildTVUnit(group, item) {
    const { width: w, depth: d, height: h } = item;

    addBox(group, MATERIALS.wood, w, h, d, 0, h / 2, 0);

    addBox(
        group, MATERIALS.black,
        w * 0.85, h * 0.65, 45,
        0, h + 300, 0
    );
}

function buildFurnitureMesh(group, item) {
    const type = item.type;

    if (type === "bedside_table") {
    buildBedsideTable(group, item);
    } else if (type.includes("bed")) {
        buildBed(group, item);
    } else if (type === "wardrobe") {
        buildWardrobe(group, item);
    } else if (type.includes("sofa")) {
        buildSofa(group, item);
    } else if (type.includes("table") && type !== "bedside_table") {
        buildTable(group, item);
    } else if (type === "dining_chair" || type === "office_chair") {
        buildChair(group, item);
    } else if (type === "bedside_table") {
        buildBedsideTable(group, item);
    } else if (type === "tv_unit") {
        buildTVUnit(group, item);
    } else if (type === "kitchen_counter") {
        buildCounter(group, item);
    } else if (type === "refrigerator") {
        buildRefrigerator(group, item);
    } else if (type === "sink" || type === "washbasin") {
        buildSink(group, item);
    } else if (type === "toilet") {
        buildToilet(group, item);
    } else if (type === "shower") {
        buildShower(group, item);
    } else {
        addBox(
            group,
            MATERIALS.wood,
            item.width,
            item.height,
            item.depth,
            0,
            item.height / 2,
            0
        );
    }
}

export function createFurniture(sceneData, houseGroup) {
    const furnitureGroups = [];
    const pickMeshes = [];

    for (const floor of sceneData.floors ?? []) {
        for (const item of floor.furniture ?? []) {
            if (
                !Array.isArray(item.position) ||
                item.position.length !== 2 ||
                !item.width ||
                !item.depth ||
                !item.height
            ) {
                console.warn("[NESTO] Skipping invalid furniture:", item);
                continue;
            }

            const group = new THREE.Group();

            group.name = `Furniture_${item.id}`;
            group.userData = {
                type: "furniture",
                furnitureId: item.id,
                furnitureType: item.type,
                roomId: item.room_id,
                dimensions: {
                    width: item.width,
                    depth: item.depth,
                    height: item.height
                }
            };

            group.position.set(
                Number(item.position[0]) * MM,
                Number(item.elevation ?? floor.elevation ?? 0) * MM,
                Number(item.position[1]) * MM
            );

            group.rotation.y = THREE.MathUtils.degToRad(
                Number(item.rotation ?? 0)
            );

            buildFurnitureMesh(group, item);

            group.traverse(object => {
                if (!object.isMesh) return;

                object.userData.furnitureId = item.id;
                object.userData.furnitureType = item.type;
                object.userData.roomId = item.room_id;

                pickMeshes.push(object);
            });

            houseGroup.add(group);
            furnitureGroups.push(group);
        }
    }

    console.log(
        `[NESTO] Generated ${furnitureGroups.length} furniture objects.`
    );

    return {
        groups: furnitureGroups,
        pickMeshes
    };
}