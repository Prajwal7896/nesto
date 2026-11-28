const API_BASE = "/api/3d";

export async function fetchScene(sceneId) {
    console.info("[NESTO 3D] Fetching scene", {
        sceneId,
        url: `${API_BASE}/scene/${encodeURIComponent(sceneId)}`,
        credentials: "same-origin"
    });
    const response = await fetch(
        `${API_BASE}/scene/${encodeURIComponent(sceneId)}`,
        {
            method: "GET",
            credentials: "same-origin",
            headers: {
                Accept: "application/json"
            }
        }
    );

    const result = await response.json().catch(() => ({}));
    console.info("[NESTO 3D] Scene response received", {
        status: response.status,
        ok: response.ok,
        sceneId,
        floors: result.scene?.floors?.length,
        rooms: (result.scene?.floors || []).reduce((n, floor) => n + (floor.rooms?.length || 0), 0),
        walls: (result.scene?.floors || []).reduce((n, floor) => n + (floor.walls?.length || 0), 0),
        furniture: (result.scene?.floors || []).reduce((n, floor) => n + (floor.furniture?.length || 0), 0)
    });

    if (!response.ok) {
        throw new Error(
            result.detail || `Unable to load scene (HTTP ${response.status}).`
        );
    }

    const scene = result.scene ?? result;

    console.log("NESTO 3D API RESPONSE:", result);
    console.log("NESTO 3D SCENE DATA:", scene);

    if (!Array.isArray(scene.floors) || scene.floors.length === 0) {
        throw new Error(
            "3D scene has no floors. Check the backend scene response."
        );
    }

    return scene;
}

export async function createScene(layout, metadata = {}) {
    const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body: JSON.stringify({ layout, metadata })
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || `Could not create scene (HTTP ${response.status}).`
        );
    }

    return data;
}
