from pathlib import Path
import re

path = Path("backend/api/rag/planner.py")
source = path.read_text(encoding="utf-8")

backup = path.with_suffix(".py.backup")
backup.write_text(source, encoding="utf-8")

method = '''
    def _optimize_floor_dimensions(
        self,
        specs: List[Dict[str, Any]],
        plot_width: float,
        plot_height: float,
    ) -> None:
        plot_area = plot_width * plot_height

        if self._required_area(specs) <= plot_area:
            return

        fixed_specs = [
            spec for spec in specs
            if spec.get("kind") in ("site_feature", "open_space")
            or spec.get("type") == "parking"
        ]

        flexible_specs = [
            spec for spec in specs
            if not (
                spec.get("kind") in ("site_feature", "open_space")
                or spec.get("type") == "parking"
            )
        ]

        fixed_area = self._required_area(fixed_specs)
        flexible_area = self._required_area(flexible_specs)

        target_area = plot_area * 0.95
        available_room_area = target_area - fixed_area

        if available_room_area <= 0 or flexible_area <= 0:
            raise ValueError(
                "Fixed site features leave insufficient space for rooms."
            )

        scale = min(1.0, (available_room_area / flexible_area) ** 0.5)

        if scale < 0.90:
            raise ValueError(
                "The requested layout cannot fit while preserving minimum "
                "room dimensions. Increase the plot size or reduce rooms."
            )

        for spec in flexible_specs:
            original_width = spec["width"]
            original_height = spec["height"]

            min_width = int(original_width * 0.90 / 50) * 50
            min_height = int(original_height * 0.90 / 50) * 50

            spec["width"] = max(
                min_width,
                int(original_width * scale / 50) * 50,
            )

            spec["height"] = max(
                min_height,
                int(original_height * scale / 50) * 50,
            )

'''

if "_optimize_floor_dimensions" not in source:
    anchor = "    def _create_floor("
    if anchor not in source:
        raise SystemExit("Could not find _create_floor(). No changes made.")

    source = source.replace(anchor, method + anchor, 1)

call_anchor = (
    "        specs = [dict(spec) for spec in feature_specs]\n"
    "        specs.extend(dict(spec) for spec in room_specs)\n"
)

if "self._optimize_floor_dimensions(" not in source:
    if call_anchor not in source:
        raise SystemExit("Could not find the specs initialization block. No changes made.")

    source = source.replace(
        call_anchor,
        call_anchor +
        "\n        self._optimize_floor_dimensions(\n"
        "            specs,\n"
        "            plot_width,\n"
        "            plot_height,\n"
        "        )\n",
        1,
    )

path.write_text(source, encoding="utf-8")
print("Successfully updated planner.py")
print(f"Backup created: {backup}")
