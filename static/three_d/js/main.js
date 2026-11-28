
import * as THREE from "three";

import { createScene } from "./scene.js";

import {
    createCamera,
    setCameraView,
    updateCameraAspect
} from "./camera.js";
import { createWindows } from "./window_builder.js";
import { createFurniture } from "./furniture_builder.js";
import {
    toggleWindow,
    updateWindowAnimations
} from "./window_animation.js";
import { fetchScene } from "./api.js";
import { createControls } from "./controls.js";
import { addLighting } from "./lighting.js";
import { buildHouse } from "./house_builder.js";

import { createDoors } from "./door_builder.js";

import {
    toggleDoor,
    updateDoorAnimations
} from "./door_animation.js";

// ==========================================
// DOM ELEMENTS
// ==========================================

const container = document.getElementById("three-viewport");
const loadingScreen = document.getElementById("loading-screen");
const sceneMessage = document.getElementById("scene-message");
const sceneStatus = document.getElementById("scene-status");

// ==========================================
// ENGINE VARIABLES
// ==========================================

let engine = null;
let camera = null;
let controls = null;
let animationFrame = null;
let houseGroup = null;

let activeView = "3d";
let doors = [];
let windows = [];
let furniture = {
    groups: [],
    pickMeshes: []
};
const clock = new THREE.Clock();
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

// ==========================================
// STATUS HANDLER
// ==========================================

function updateStatus(message) {
    if (sceneMessage) {
        sceneMessage.textContent = message;
    }

    if (sceneStatus) {
        sceneStatus.textContent = message.toUpperCase();
    }

    console.log("[NESTO 3D]", message);
    if (window.parent !== window) {
        window.parent.postMessage({
            type: "nesto-3d-status",
            message,
            level: /failed|error|unavailable/i.test(message)
                ? "error"
                : (/^House generated/i.test(message) ? "success" : "info")
        }, window.location.origin);
    }
}

// ==========================================
// INITIALIZATION
// ==========================================

async function initialize() {
    try {
        console.info("[NESTO 3D] Viewer module initializing", {
            url: window.location.href,
            viewport: container ? { width: container.clientWidth, height: container.clientHeight } : null
        });
        if (!container) {
            throw new Error("Three.js viewport container not found.");
        }

        updateStatus("Initializing Three.js engine...");

        // 1. Initialize scene and renderer
        engine = createScene(container);

        const { scene, renderer } = engine;
        console.info("[NESTO 3D] Renderer initialized", {
            canvas: renderer.domElement.tagName,
            width: renderer.domElement.width,
            height: renderer.domElement.height,
            cssWidth: renderer.domElement.clientWidth,
            cssHeight: renderer.domElement.clientHeight,
            webgl2: renderer.capabilities.isWebGL2
        });

        // 2. Initialize camera
        camera = createCamera(container);

        // 3. Initialize controls
        controls = createControls(camera, renderer);

        // 4. Lighting
        addLighting(scene);

        // 5. Read scene ID
        const params = new URLSearchParams(window.location.search);
        const sceneId = params.get("scene_id");

        if (!sceneId) {
            updateStatus("3D engine ready. Waiting for house layout.");
        } else {
            updateStatus("Loading house layout...");

            // 6. Fetch saved scene
            console.info("[NESTO 3D] Fetching saved scene", { sceneId });
            const response = await fetchScene(sceneId);
            console.info("[NESTO 3D] Saved scene fetch complete", { sceneId });

            console.log("[NESTO] API response:", response);

            const sceneData = response.scene ?? response;

            if (!Array.isArray(sceneData.floors)) {
                throw new Error(
                    "Invalid scene data: floors array is missing."
                );
            }

            const roomCount = sceneData.floors.reduce(
                (total, floor) =>
                    total + (floor.rooms?.length ?? 0),
                0
            );

            console.log("[NESTO] Floor count:", sceneData.floors.length);
            console.log("[NESTO] Room count:", roomCount);

            if (roomCount === 0) {
                throw new Error("No rooms found in the generated scene.");
            }

            updateStatus("Building 3D house geometry...");

            // 7. Build house
            console.info("[NESTO 3D] Building house", {
                floors: sceneData.floors.length,
                rooms: roomCount,
                walls: sceneData.floors.reduce((n, floor) => n + (floor.walls?.length || 0), 0)
            });
            const result = buildHouse(sceneData, scene);

            if (!result || !result.group) {
                throw new Error(
                    "House builder did not return a valid group."
                );
            }

            houseGroup = result.group;
            console.info("[NESTO 3D] House build complete", {
                floors: result.floorCount,
                wallGroups: result.wallCount,
                sceneHasHouse: scene.children.includes(houseGroup)
            });

            console.log("[NESTO] House generation result:", {
                floors: result.floorCount,
                walls: result.wallCount,
                rooms: roomCount
            });

            // 8. Create interactive doors
            doors = createDoors(sceneData, houseGroup);
            windows = createWindows(sceneData, houseGroup);
            furniture = createFurniture(sceneData, houseGroup);

            console.log(
                "[NESTO] Furniture objects:",
                furniture.groups.length
            );
            console.log("[NESTO] Interactive windows:", windows.length);
            console.log("[NESTO] Interactive doors:", doors.length);

            // 9. Calculate house bounds
            const bounds = new THREE.Box3().setFromObject(houseGroup);

            if (bounds.isEmpty()) {
                throw new Error("Generated house geometry is empty.");
            }

            const center = bounds.getCenter(new THREE.Vector3());
            const size = bounds.getSize(new THREE.Vector3());

            console.log("[NESTO] House dimensions:", size);
            console.log("[NESTO] House center:", center);

            // 10. Position camera
            controls.target.copy(center);

            const maxDimension = Math.max(
                size.x,
                size.y,
                size.z
            );

            const distance = Math.max(maxDimension * 1.8, 10);

            camera.position.set(
                center.x + distance,
                center.y + distance * 0.8,
                center.z + distance
            );

            camera.lookAt(center);
            camera.updateProjectionMatrix();
            controls.update();
            camera.updateMatrixWorld();
            console.info("[NESTO 3D] Camera framed on house", {
                position: camera.position.toArray(),
                target: controls.target.toArray(),
                bounds: { min: bounds.min.toArray(), max: bounds.max.toArray() },
                inFrustum: new THREE.Frustum().setFromProjectionMatrix(
                    new THREE.Matrix4().multiplyMatrices(
                        camera.projectionMatrix,
                        camera.matrixWorldInverse
                    )
                ).intersectsBox(bounds)
            });

            // 11. Count meshes
            let meshCount = 0;

            houseGroup.traverse(object => {
                if (object.isMesh) {
                    meshCount++;
                }
            });

            console.log("[NESTO] Total meshes:", meshCount);

            updateStatus(
                `House generated | Rooms: ${roomCount} | Floors: ${result.floorCount} | Walls: ${result.wallCount} | Doors: ${doors.length} | Windows: ${windows.length} | Furniture: ${furniture.groups.length}`
            );
            if (sceneMessage) {
                sceneMessage.style.display = "none";
            }
        }

        // 12. Hide loading screen
        if (loadingScreen) {
            loadingScreen.style.display = "none";
        }

        // 13. Setup toolbar and interactions
        setupToolbar();
        setupResize();
        setupDoorInteraction();
        setupWindowInteraction();
        setupFurnitureInteraction();
        setupLayerVisibility();

        // 14. Start animation
        console.info("[NESTO 3D] Starting render loop", {
            camera: camera?.position.toArray(),
            canvas: engine?.renderer?.domElement ? {
                width: engine.renderer.domElement.width,
                height: engine.renderer.domElement.height,
                cssWidth: engine.renderer.domElement.clientWidth,
                cssHeight: engine.renderer.domElement.clientHeight
            } : null
        });
        animate();

        console.log("[NESTO] Three.js engine initialized successfully.");

    } catch (error) {
        console.error("[NESTO] Initialization failed:", error);

        updateStatus(`Initialization failed: ${error.message}`);
        console.error("[NESTO 3D] Initialization exception", error);

        if (loadingScreen) {
            loadingScreen.style.display = "none";
        }

        if (sceneStatus) {
            sceneStatus.textContent = "ENGINE ERROR";
        }
    }
}

// ==========================================
// RENDER LOOP
// ==========================================

function animate() {
    animationFrame = requestAnimationFrame(animate);

    const delta = Math.min(clock.getDelta(), 0.05);

    controls?.update();

    updateDoorAnimations(doors, delta);
    updateWindowAnimations(windows, delta);
    if (engine && camera) {
        engine.renderer.render(engine.scene, camera);
    }
}

// ==========================================
// FURNITURE INTERACTION
// ==========================================

function setupFurnitureInteraction() {
    const canvas = engine?.renderer?.domElement;

    if (!canvas) return;

    canvas.addEventListener("click", event => {
        if (!furniture.pickMeshes.length || !camera) return;

        const rect = canvas.getBoundingClientRect();

        if (!rect.width || !rect.height) return;

        pointer.x =
            ((event.clientX - rect.left) / rect.width) * 2 - 1;

        pointer.y =
            -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);

        const hits = raycaster.intersectObjects(
            furniture.pickMeshes.filter(mesh => {
                let parent = mesh;

                while (parent) {
                    if (!parent.visible) return false;
                    parent = parent.parent;
                }

                return true;
            }),
            false
        );

        if (!hits.length) return;

        const selected = hits[0].object;

        const item = selected.userData;

        const furnitureGroup = furniture.groups.find(
            group => group.userData.furnitureId === item.furnitureId
        );

        if (!furnitureGroup) return;

        const dimensions = furnitureGroup.userData.dimensions;

        const selectedElement = document.getElementById(
            "selected-object"
        );

        if (selectedElement) {
            selectedElement.textContent =
                `${item.furnitureType.replaceAll("_", " ")} | ${item.roomId}`;
        }

        const widthElement = document.getElementById("object-width");
        const heightElement = document.getElementById("object-height");
        const depthElement = document.getElementById("object-depth");

        if (widthElement) {
            widthElement.textContent =
                `${(dimensions.width / 1000).toFixed(2)} m`;
        }

        if (heightElement) {
            heightElement.textContent =
                `${(dimensions.height / 1000).toFixed(2)} m`;
        }

        if (depthElement) {
            depthElement.textContent =
                `${(dimensions.depth / 1000).toFixed(2)} m`;
        }

        updateStatus(
            `Selected ${item.furnitureType} in ${item.roomId}`
        );

        console.log("[NESTO] Furniture selected:", item);
    });

    console.log("[NESTO] Furniture interaction initialized.");
}

// ==========================================
// DOOR INTERACTION
// ==========================================

function setupWindowInteraction() {
    const canvas = engine?.renderer?.domElement;

    if (!canvas) return;

    canvas.addEventListener("click", event => {
        if (!windows.length || !camera) return;

        const rect = canvas.getBoundingClientRect();

        if (!rect.width || !rect.height) return;

        pointer.x =
            ((event.clientX - rect.left) / rect.width) * 2 - 1;

        pointer.y =
            -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);

        const glassPanels = windows.flatMap(item => item.glass);

        const hits = raycaster.intersectObjects(glassPanels, false);

        if (!hits.length) return;

        const windowId = hits[0].object.userData.windowId;

        const selectedWindow = windows.find(
            item => item.id === windowId
        );

        if (!selectedWindow) return;

        toggleWindow(selectedWindow);

        updateStatus(
            `Window ${windowId}: ${
                selectedWindow.open ? "Opening" : "Closing"
            }`
        );
    });

    console.log("[NESTO] Window interaction initialized.");
}

function setupDoorInteraction() {
    const canvas = engine?.renderer?.domElement;

    if (!canvas) {
        console.warn("[NESTO] Renderer canvas unavailable.");
        return;
    }

    canvas.addEventListener("click", event => {
        if (!doors.length || !camera) return;

        const rect = canvas.getBoundingClientRect();

        if (!rect.width || !rect.height) return;

        pointer.x =
            ((event.clientX - rect.left) / rect.width) * 2 - 1;

        pointer.y =
            -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);

        const panels = doors.map(door => door.panel);

        const hits = raycaster.intersectObjects(panels, false);

        if (!hits.length) return;

        const doorId = hits[0].object.userData.doorId;

        const selectedDoor = doors.find(
            door => door.id === doorId
        );

        if (!selectedDoor) return;

        toggleDoor(selectedDoor.hinge);

        updateStatus(
            `Door ${doorId}: ${
                selectedDoor.hinge.userData.open
                    ? "Opening"
                    : "Closing"
            }`
        );

        console.log("[NESTO] Door toggled:", doorId);
    });

    console.log("[NESTO] Door interaction initialized.");
}
// ==========================================
// LAYER VISIBILITY
// ==========================================

function setupLayerVisibility() {
    document.querySelectorAll("[data-layer]").forEach(checkbox => {
        const layer = checkbox.dataset.layer;

        checkbox.addEventListener("change", () => {
            if (layer === "furniture") {
                furniture.groups.forEach(group => {
                    group.visible = checkbox.checked;
                });

                updateStatus(
                    checkbox.checked
                        ? "Furniture layer visible"
                        : "Furniture layer hidden"
                );
            }
        });
    });

    // Apply the initial checkbox state.
    const furnitureCheckbox = document.querySelector(
        '[data-layer="furniture"]'
    );

    if (furnitureCheckbox) {
        furniture.groups.forEach(group => {
            group.visible = furnitureCheckbox.checked;
        });
    }

    console.log("[NESTO] Layer visibility initialized.");
}
// ==========================================
// RESIZE
// ==========================================

function setupResize() {
    window.addEventListener("resize", () => {
        if (!camera || !container) return;

        updateCameraAspect(camera, container);
    });
}

// ==========================================
// FOCUS HOUSE
// ==========================================

function focusHouse() {
    if (!houseGroup || !camera || !controls) return;

    const bounds = new THREE.Box3().setFromObject(houseGroup);

    if (bounds.isEmpty()) {
        console.warn("[NESTO] House geometry is empty.");
        return;
    }

    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());

    const maxDimension = Math.max(size.x, size.y, size.z);
    const distance = Math.max(maxDimension * 1.8, 10);

    controls.target.copy(center);

    camera.position.set(
        center.x + distance,
        center.y + distance * 0.8,
        center.z + distance
    );

    camera.lookAt(center);
    camera.updateProjectionMatrix();

    controls.update();
}

// ==========================================
// TOOLBAR
// ==========================================

function setupToolbar() {

    // Reset camera
    document.getElementById("reset-view")?.addEventListener("click", () => {
        activeView = "3d";

        const target = controls.target;

        if (houseGroup) {
            const bounds = new THREE.Box3().setFromObject(houseGroup);

            if (!bounds.isEmpty()) {
                bounds.getCenter(target);
            }
        }

        setCameraView(camera, "3d", target);

        controls.update();
        updateActiveTab("3d");
    });

    // Zoom in
    document.getElementById("zoom-in")?.addEventListener("click", () => {
        zoomCamera(0.8);
    });

    // Zoom out
    document.getElementById("zoom-out")?.addEventListener("click", () => {
        zoomCamera(1.25);
    });

    // Focus house
    document.getElementById("focus-house")?.addEventListener("click", () => {
        focusHouse();
    });

    // Fullscreen
    document.getElementById("fullscreen")?.addEventListener("click", async () => {
        const viewport = document.querySelector(".viewport-container");

        if (!viewport) return;

        try {
            if (!document.fullscreenElement) {
                await viewport.requestFullscreen();
            } else {
                await document.exitFullscreen();
            }
        } catch (error) {
            console.error("[NESTO] Fullscreen error:", error);
        }
    });

    // Camera views
    document.querySelectorAll(".view-tab").forEach(button => {
        button.addEventListener("click", () => {
            const view = button.dataset.view;

            activeView = view;

            setCameraView(camera, view, controls.target);
            controls.update();

            updateActiveTab(view);
        });
    });
}

// ==========================================
// ZOOM
// ==========================================

function zoomCamera(factor) {
    if (!camera || !controls) return;

    const offset = camera.position.clone().sub(controls.target);

    offset.multiplyScalar(factor);

    const distance = offset.length();

    if (distance < 2 || distance > 300) return;

    camera.position.copy(controls.target).add(offset);

    controls.update();
}

// ==========================================
// ACTIVE TAB
// ==========================================

function updateActiveTab(view) {
    document.querySelectorAll(".view-tab").forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.view === view
        );
    });
}

// ==========================================
// CLEANUP
// ==========================================

window.addEventListener("pagehide", () => {
    if (animationFrame !== null) {
        cancelAnimationFrame(animationFrame);
    }

    controls?.dispose();
    engine?.dispose();
});

// ==========================================
// START
// ==========================================

initialize();
