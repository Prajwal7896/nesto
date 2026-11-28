
export function toggleDoor(hinge) {
    if (!hinge) return;

    hinge.userData.open = !hinge.userData.open;

    hinge.userData.targetRotation = hinge.userData.open
        ? Math.PI / 2
        : 0;
}

export function updateDoorAnimations(doors, delta) {
    for (const door of doors || []) {
        const hinge = door.hinge;

        if (!hinge) continue;

        const target = hinge.userData.targetRotation || 0;

        // Smooth frame-rate-independent interpolation
        const factor = 1 - Math.exp(-7 * delta);

        hinge.rotation.y +=
            (target - hinge.rotation.y) * factor;

        if (Math.abs(target - hinge.rotation.y) < 0.001) {
            hinge.rotation.y = target;
        }
    }
}
