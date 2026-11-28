"""Component animation data generation for Three.js."""


class ComponentAnimationData:

    SUPPORTED_ANIMATIONS = {
        "reveal",
        "rise",
        "fade",
        "scale"
    }

    def generate(
        self,
        component,
        animation_type="rise",
        start_time=0.0,
        duration=2.0
    ):
        if not isinstance(component, dict):
            raise TypeError("Component must be a dictionary")

        if animation_type not in self.SUPPORTED_ANIMATIONS:
            raise ValueError(
                f"Unsupported animation: {animation_type}"
            )

        if start_time < 0:
            raise ValueError("Start time cannot be negative")

        if duration <= 0:
            raise ValueError("Duration must be positive")

        component_id = component.get("id")

        if not component_id:
            raise ValueError("Component must have an id")

        animation = {
            "component_id": component_id,
            "component_type": component.get("type", "unknown"),
            "animation_type": animation_type,
            "start_time": float(start_time),
            "duration": float(duration),
            "end_time": float(start_time + duration),
            "initial_state": {},
            "final_state": {
                "visible": True,
                "opacity": 1.0,
                "scale": [1.0, 1.0, 1.0]
            },
            "easing": "easeInOutCubic"
        }

        if animation_type == "rise":
            animation["initial_state"] = {
                "visible": True,
                "opacity": 1.0,
                "offset_y": -1000
            }

        elif animation_type == "fade":
            animation["initial_state"] = {
                "visible": True,
                "opacity": 0.0
            }

        elif animation_type == "scale":
            animation["initial_state"] = {
                "visible": True,
                "opacity": 1.0,
                "scale": [0.001, 0.001, 0.001]
            }

        elif animation_type == "reveal":
            animation["initial_state"] = {
                "visible": False,
                "opacity": 1.0
            }

        return animation

    def generate_for_components(
        self,
        components,
        animation_type="rise",
        interval=0.25,
        duration=2.0
    ):
        if interval < 0:
            raise ValueError("Interval cannot be negative")

        animations = []

        for index, component in enumerate(components):
            start_time = index * interval

            animations.append(
                self.generate(
                    component=component,
                    animation_type=animation_type,
                    start_time=start_time,
                    duration=duration
                )
            )

        return animations
