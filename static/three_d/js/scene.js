
import * as THREE from "three";

export function createScene(container) {
    if (!container) {
        throw new Error("Three.js viewport not found.");
    }

    const probe = document.createElement("canvas");
    const webgl2Available = !!probe.getContext("webgl2");
    const webglAvailable = webgl2Available || !!probe.getContext("webgl");
    if (!webglAvailable) {
        throw new Error("WebGL is unavailable in this browser. Enable hardware acceleration or use a browser with WebGL support.");
    }

    let renderer;

    try {
        renderer = new THREE.WebGLRenderer({
            antialias: false,
            alpha: false,
            powerPreference: "low-power",
            failIfMajorPerformanceCaveat: false
        });
    } catch (error) {
        throw new Error(
            "WebGL initialization failed. Enable Chrome hardware acceleration, " +
            "update your graphics driver, and restart the browser. " + error.message
        );
    }

    renderer.setPixelRatio(
        Math.min(window.devicePixelRatio || 1, 1.5)
    );

    renderer.setSize(
        container.clientWidth,
        container.clientHeight
    );
    if (container.clientWidth <= 0 || container.clientHeight <= 0) {
        throw new Error(`3D viewport has invalid size (${container.clientWidth}×${container.clientHeight}).`);
    }

    renderer.shadowMap.enabled = false;

    renderer.outputColorSpace = THREE.SRGBColorSpace;

    container.appendChild(renderer.domElement);
    console.info("[NESTO 3D] WebGL canvas attached", {
        webgl2Available,
        width: renderer.domElement.width,
        height: renderer.domElement.height,
        cssWidth: renderer.domElement.clientWidth,
        cssHeight: renderer.domElement.clientHeight
    });

    const scene = new THREE.Scene();

    scene.background = new THREE.Color(0x0b1320);

    const grid = new THREE.GridHelper(
        100,
        100,
        0x64748b,
        0x334155
    );

    scene.add(grid);

    const groundGeometry = new THREE.PlaneGeometry(200, 200);

    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x172033,
        roughness: 1
    });

    const ground = new THREE.Mesh(
        groundGeometry,
        groundMaterial
    );

    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.03;

    scene.add(ground);

    const resizeObserver = new ResizeObserver(() => {
        const width = container.clientWidth;
        const height = container.clientHeight;

        if (width > 0 && height > 0) {
            renderer.setSize(width, height);
            console.info("[NESTO 3D] Renderer resized", {
                width: renderer.domElement.width,
                height: renderer.domElement.height,
                cssWidth: width,
                cssHeight: height
            });
        }
    });

    resizeObserver.observe(container);

    return {
        scene,
        renderer,
        ground,
        grid,

        dispose() {
            resizeObserver.disconnect();

            scene.traverse(object => {
                if (object.geometry) {
                    object.geometry.dispose();
                }

                if (object.material) {
                    const materials = Array.isArray(object.material)
                        ? object.material
                        : [object.material];

                    materials.forEach(material => material.dispose());
                }
            });

            renderer.dispose();
            renderer.domElement.remove();
        }
    };
}
