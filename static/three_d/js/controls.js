import { OrbitControls } from "three/addons/controls/OrbitControls.js";

export function createControls(camera, renderer) {
    const controls = new OrbitControls(camera, renderer.domElement);

    controls.enableDamping = true;
    controls.dampingFactor = 0.06;

    controls.enableRotate = true;
    controls.enableZoom = true;
    controls.enablePan = true;

    controls.minDistance = 2;
    controls.maxDistance = 300;

    controls.minPolarAngle = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;

    controls.target.set(0, 0, 0);
    controls.update();

    return controls;
}
