import * as THREE from "three";

export function createCamera(container) {
    const aspect = container.clientWidth / Math.max(container.clientHeight, 1);

    const camera = new THREE.PerspectiveCamera(
        45,
        aspect,
        0.1,
        2000
    );

    camera.position.set(18, 15, 20);
    camera.lookAt(0, 0, 0);

    return camera;
}

export function updateCameraAspect(camera, container) {
    camera.aspect = container.clientWidth / Math.max(container.clientHeight, 1);
    camera.updateProjectionMatrix();
}

export function setCameraView(camera, view, target = new THREE.Vector3()) {
    const distance = 25;

    const positions = {
        "3d": new THREE.Vector3(distance, distance * 0.8, distance),
        "top": new THREE.Vector3(0, distance * 1.8, 0.001),
        "front": new THREE.Vector3(0, distance * 0.6, distance),
        "side": new THREE.Vector3(distance, distance * 0.6, 0)
    };

    const direction = positions[view] || positions["3d"];

    camera.position.copy(target).add(direction);
    camera.lookAt(target);
    camera.updateProjectionMatrix();
}
