import * as THREE from "three";
import { buildFloors } from "./floor_builder.js";
import { buildWalls } from "./wall_builder.js";

export function buildHouse(sceneData, scene) {
    if (!sceneData || !scene) {
        throw new Error("Scene data or Three.js scene is missing.");
    }

    const floors = sceneData.floors;

    if (!Array.isArray(floors) || floors.length === 0) {
        throw new Error("No floors found in the 3D scene data.");
    }

    const houseGroup = new THREE.Group();
    houseGroup.name = "NestoHouse";

    const floorCount = buildFloors(sceneData, houseGroup);
    console.info("[NESTO 3D] Floor meshes created", { count: floorCount });
    const wallCount = buildWalls(sceneData, houseGroup);
    let meshCount = 0;
    houseGroup.traverse(object => { if (object.isMesh) meshCount++; });
    console.info("[NESTO 3D] Wall groups and house meshes created", {
        wallGroups: wallCount,
        meshCount
    });

    if (floorCount === 0) {
        throw new Error("No valid room polygons found to generate floors.");
    }

    scene.add(houseGroup);
    console.info("[NESTO 3D] House group added to Three.js scene", {
        sceneChildren: scene.children.length,
        houseChildren: houseGroup.children.length
    });

    return {
        group: houseGroup,
        floorCount,
        wallCount
    };
}
