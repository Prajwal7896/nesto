
export function toggleWindow(windowData) {
    if (!windowData) return;

    windowData.open = !windowData.open;

    const direction = windowData.open ? -1 : 1;

    windowData.targetPositions = windowData.open
        ? [
            windowData.closedPositions[0] -
                windowData.openDistance / 2,
            windowData.closedPositions[1] +
                windowData.openDistance / 2
        ]
        : [...windowData.closedPositions];

    console.log(
        `[NESTO] Window ${windowData.id}:`,
        windowData.open ? "Opening" : "Closing"
    );
}

export function updateWindowAnimations(windows, delta) {
    const factor = 1 - Math.exp(-6 * delta);

    for (const windowData of windows || []) {
        if (!windowData.targetPositions) continue;

        windowData.panels.forEach((panel, index) => {
            const target = windowData.targetPositions[index];

            panel.position.x +=
                (target - panel.position.x) * factor;

            if (Math.abs(target - panel.position.x) < 0.001) {
                panel.position.x = target;
            }
        });
    }
}
