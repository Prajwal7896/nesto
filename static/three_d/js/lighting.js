import * as THREE from "three";

export function addLighting(scene) {
    const hemisphere = new THREE.HemisphereLight(
        0xdceaff,
        0x263448,
        2.0
    );

    scene.add(hemisphere);

    const sunlight = new THREE.DirectionalLight(
        0xffffff,
        3.0
    );

    sunlight.position.set(20, 30, 15);
    sunlight.castShadow = true;

    sunlight.shadow.mapSize.width = 2048;
    sunlight.shadow.mapSize.height = 2048;

    sunlight.shadow.camera.left = -40;
    sunlight.shadow.camera.right = 40;
    sunlight.shadow.camera.top = 40;
    sunlight.shadow.camera.bottom = -40;

    sunlight.shadow.camera.near = 0.5;
    sunlight.shadow.camera.far = 100;

    sunlight.shadow.bias = -0.0001;

    scene.add(sunlight);

    const fillLight = new THREE.DirectionalLight(
        0x9bbcff,
        0.7
    );

    fillLight.position.set(-15, 12, -20);
    scene.add(fillLight);

    return {
        hemisphere,
        sunlight,
        fillLight
    };
}
