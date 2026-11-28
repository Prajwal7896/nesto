
import * as THREE from "three";

const MM_TO_M = 0.001;
const TOLERANCE = 0.003;

const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0xe5e1d8,
    roughness: 0.85,
    metalness: 0
});

function toMeters(value) {
    return Number(value || 0) * MM_TO_M;
}

function mergeIntervals(intervals) {
    if (!intervals.length) return [];

    const sorted = intervals
        .map(([start, end]) => [
            Math.min(start, end),
            Math.max(start, end)
        ])
        .sort((a, b) => a[0] - b[0]);

    const merged = [sorted[0]];

    for (let i = 1; i < sorted.length; i++) {
        const current = sorted[i];
        const last = merged[merged.length - 1];

        if (current[0] <= last[1] + TOLERANCE) {
            last[1] = Math.max(last[1], current[1]);
        } else {
            merged.push([...current]);
        }
    }

    return merged;
}

function createWallMesh(
    houseGroup,
    start,
    end,
    height,
    thickness,
    elevation,
    metadata
) {
    const dx = end.x - start.x;
    const dz = end.z - start.z;
    const length = Math.hypot(dx, dz);

    if (length < 0.001 || height <= 0 || thickness <= 0) return;

    const geometry = new THREE.BoxGeometry(
        length,
        height,
        thickness
    );

    const mesh = new THREE.Mesh(geometry, wallMaterial);

    mesh.position.set(
        (start.x + end.x) / 2,
        elevation + height / 2,
        (start.z + end.z) / 2
    );

    mesh.rotation.y = -Math.atan2(dz, dx);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    mesh.userData = {
        type: "wall",
        ...metadata
    };

    houseGroup.add(mesh);
}

function createLinePoint(unit, normal, offset, distance) {
    return {
        x: unit.x * distance + normal.x * offset,
        z: unit.z * distance + normal.z * offset
    };
}

function buildWallGroups(walls) {
    const groups = new Map();

    for (const wall of walls) {
        if (!wall.start || !wall.end) continue;

        const start = {
            x: toMeters(wall.start[0]),
            z: toMeters(wall.start[1])
        };

        const end = {
            x: toMeters(wall.end[0]),
            z: toMeters(wall.end[1])
        };

        let dx = end.x - start.x;
        let dz = end.z - start.z;

        const length = Math.hypot(dx, dz);
        if (length < 0.001) continue;

        let ux = dx / length;
        let uz = dz / length;

        // Give opposite wall directions the same canonical direction.
        if (ux < -0.0001 || (Math.abs(ux) <= 0.0001 && uz < 0)) {
            ux *= -1;
            uz *= -1;
        }

        const unit = { x: ux, z: uz };
        const normal = { x: -uz, z: ux };

        const offset = start.x * normal.x + start.z * normal.z;

        const height = toMeters(wall.height || 3000);
        const thickness = toMeters(wall.thickness || 150);

        const key = [
            ux.toFixed(4),
            uz.toFixed(4),
            offset.toFixed(3),
            height.toFixed(3),
            thickness.toFixed(3)
        ].join("_");

        if (!groups.has(key)) {
            groups.set(key, {
                unit,
                normal,
                offset,
                height,
                thickness,
                spans: [],
                openings: [],
                wallIds: []
            });
        }

        const group = groups.get(key);

        const startDistance = start.x * ux + start.z * uz;
        const endDistance = end.x * ux + end.z * uz;

        const low = Math.min(startDistance, endDistance);
        const high = Math.max(startDistance, endDistance);

        group.spans.push([low, high]);
        group.wallIds.push(wall.id);

        for (const opening of wall.openings || []) {
            const width = toMeters(opening.width);
            const openingHeight = toMeters(opening.height);
            const sill = toMeters(opening.sill_height || 0);

            if (width <= 0 || openingHeight <= 0) continue;

            const position = Math.max(
                0,
                Math.min(1, Number(opening.position ?? 0.5))
            );

            const center = startDistance +
                (endDistance - startDistance) * position;

            group.openings.push({
                id: opening.id,
                kind: opening.kind,
                start: center - width / 2,
                end: center + width / 2,
                height: openingHeight,
                sill
            });
        }
    }

    return [...groups.values()];
}

function buildMergedWall(group, houseGroup, elevation) {
    const mergedSpans = mergeIntervals(group.spans);

    for (const [spanStart, spanEnd] of mergedSpans) {
        const openings = group.openings
            .filter(opening =>
                opening.end > spanStart &&
                opening.start < spanEnd
            )
            .sort((a, b) => a.start - b.start);

        const validOpenings = [];
        let previousEnd = spanStart;

        for (const opening of openings) {
            const start = Math.max(spanStart, opening.start);
            const end = Math.min(spanEnd, opening.end);

            if (end <= start || start < previousEnd - TOLERANCE) {
                continue;
            }

            const sill = Math.max(0, opening.sill);
            const top = Math.min(
                group.height,
                sill + opening.height
            );

            if (top <= sill) continue;

            validOpenings.push({
                ...opening,
                start,
                end,
                sill,
                top
            });

            previousEnd = end;
        }

        let cursor = spanStart;

        for (const opening of validOpenings) {
            // Solid wall before the opening.
            if (opening.start > cursor + TOLERANCE) {
                createWallMesh(
                    houseGroup,
                    createLinePoint(
                        group.unit, group.normal, group.offset, cursor
                    ),
                    createLinePoint(
                        group.unit, group.normal, group.offset, opening.start
                    ),
                    group.height,
                    group.thickness,
                    elevation,
                    { wallIds: group.wallIds }
                );
            }

            // Wall below a window opening.
            if (opening.sill > TOLERANCE) {
                createWallMesh(
                    houseGroup,
                    createLinePoint(
                        group.unit, group.normal, group.offset, opening.start
                    ),
                    createLinePoint(
                        group.unit, group.normal, group.offset, opening.end
                    ),
                    opening.sill,
                    group.thickness,
                    elevation,
                    { openingId: opening.id, wallIds: group.wallIds }
                );
            }

            // Wall above the opening.
            if (opening.top < group.height - TOLERANCE) {
                const headerHeight = group.height - opening.top;

                createWallMesh(
                    houseGroup,
                    createLinePoint(
                        group.unit, group.normal, group.offset, opening.start
                    ),
                    createLinePoint(
                        group.unit, group.normal, group.offset, opening.end
                    ),
                    headerHeight,
                    group.thickness,
                    elevation + opening.top,
                    { openingId: opening.id, wallIds: group.wallIds }
                );
            }

            cursor = opening.end;
        }

        // Solid wall after the final opening.
        if (cursor < spanEnd - TOLERANCE) {
            createWallMesh(
                houseGroup,
                createLinePoint(
                    group.unit, group.normal, group.offset, cursor
                ),
                createLinePoint(
                    group.unit, group.normal, group.offset, spanEnd
                ),
                group.height,
                group.thickness,
                elevation,
                { wallIds: group.wallIds }
            );
        }
    }
}

export function buildWalls(sceneData, houseGroup) {
    let totalWalls = 0;

    for (const floor of sceneData.floors || []) {
        const walls = floor.walls || [];
        const elevation = toMeters(floor.elevation || 0);

        const groups = buildWallGroups(walls);

        for (const group of groups) {
            buildMergedWall(group, houseGroup, elevation);
        }

        totalWalls += groups.length;
    }

    let wallMeshCount = 0;
    houseGroup.traverse(object => {
        if (object.isMesh && object.userData.type === "wall") wallMeshCount++;
    });
    console.info("[NESTO 3D] Wall mesh creation complete", {
        wallGroups: totalWalls,
        wallMeshes: wallMeshCount,
        sourceWalls: (sceneData.floors || []).reduce((n, floor) => n + (floor.walls?.length || 0), 0)
    });

    return totalWalls;
}
