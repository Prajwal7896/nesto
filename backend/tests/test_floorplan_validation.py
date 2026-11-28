import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.api.rag.layout_validator import validate_layout
from backend.api.rag.planner import LayoutPlanner
from backend.api.rag.pipeline import _validate_generated_layout
from backend.api.rag.renderer.renderer import Renderer
from backend.api.three_d.core.scene_builder import SceneBuilder


class LayoutValidationTests(unittest.TestCase):
    def room(self, room_id, room_type, x, y, width=2000, height=2000):
        return {
            "id": room_id,
            "type": room_type,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "area": width * height,
            "polygon": [
                [x, y],
                [x + width, y],
                [x + width, y + height],
                [x, y + height],
            ],
        }

    def layout(self, rooms, width=10000, height=10000):
        return {
            "plot": {"width": width, "height": height},
            "rooms": rooms,
            "adjacency_graph": [],
            "circulation": {},
            "structure": {},
            "engineering": {},
        }

    def test_duplicate_coordinates_are_rejected(self):
        rooms = [
            self.room("living_1", "living_room", 0, 0),
            self.room("bedroom_1", "bedroom", 0, 0),
        ]

        result = validate_layout(
            self.layout(rooms),
            {"space_constraints": {"rooms": {}}},
        )

        self.assertFalse(result["valid"])
        self.assertTrue(any("Duplicate room coordinates" in error for error in result["errors"]))

    def test_overlapping_rooms_are_rejected(self):
        rooms = [
            self.room("living_1", "living_room", 0, 0),
            self.room("bedroom_1", "bedroom", 1500, 1500),
        ]

        result = validate_layout(
            self.layout(rooms),
            {"space_constraints": {"rooms": {}}},
        )

        self.assertFalse(result["valid"])
        self.assertTrue(any("overlap" in error for error in result["errors"]))

    def test_out_of_bounds_room_is_rejected(self):
        rooms = [self.room("living_1", "living_room", 9000, 0)]

        result = validate_layout(
            self.layout(rooms, width=10000),
            {"space_constraints": {"rooms": {}}},
        )

        self.assertFalse(result["valid"])
        self.assertTrue(any("outside the plot boundary" in error for error in result["errors"]))

    def test_incorrect_room_count_is_rejected(self):
        rooms = [self.room("bedroom_1", "bedroom", 0, 0)]

        result = validate_layout(
            self.layout(rooms),
            {"space_constraints": {"rooms": {"bedrooms": 2}}},
        )

        self.assertFalse(result["valid"])
        self.assertTrue(any("expected 2, found 1" in error for error in result["errors"]))

    def test_planner_creates_exact_unique_rooms_without_overlap(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12000,
                "plot_height": 10000,
                "rooms": {
                    "living_room": 1,
                    "bedrooms": 2,
                    "master_bedrooms": 1,
                    "bathrooms": 1,
                    "attached_bathrooms": 0,
                    "common_bathrooms": 0,
                    "kitchen": 1,
                    "dining_room": 0,
                    "utility_room": 0,
                    "balcony": 0,
                },
            },
            "structural_constraints": {
                "balcony_cantilever_supported": True,
            },
        }

        layout = LayoutPlanner().generate_layout(constraints)
        result = validate_layout(layout, constraints)

        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(layout["room_count"], 5)
        self.assertEqual(len({room["id"] for room in layout["rooms"]}), 5)
        self.assertEqual(
            sum(room["type"] == "master_bedroom" for room in layout["rooms"]),
            1,
        )
        self.assertFalse(any(room["type"] in ("utility_room", "balcony") for room in layout["rooms"]))

    def test_room_subtypes_are_included_in_requested_totals(self):
        specs = LayoutPlanner()._requested_rooms({
            "bedrooms": 3,
            "master_bedrooms": 2,
            "bathrooms": 2,
            "common_bathrooms": 1,
            "family_room": 1,
        })
        types = [room["type"] for room in specs]

        self.assertEqual(types.count("master_bedroom"), 2)
        self.assertEqual(types.count("bedroom"), 1)
        self.assertEqual(types.count("common_bathroom"), 1)
        self.assertEqual(types.count("bathroom"), 1)
        self.assertNotIn("family_room", types)

    def test_family_room_is_only_expanded_when_enclosed(self):
        specs = LayoutPlanner()._requested_rooms({
            "family_room": 1,
            "family_room_enclosed": True,
        })

        self.assertEqual([room["type"] for room in specs], ["family_room"])

    def test_shared_walls_are_valid_and_detected_as_contact(self):
        planner = LayoutPlanner()
        rooms = [
            self.room("living_1", "living_room", 0, 0),
            self.room("bedroom_1", "bedroom", 2000, 0),
        ]

        result = validate_layout(self.layout(rooms))

        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(
            planner._contact_length(0, 0, 2000, 2000, [rooms[1]]),
            2000,
        )

    def test_disconnected_circulation_is_rejected(self):
        rooms = [
            self.room("living_1", "living_room", 0, 0),
            self.room("bedroom_1", "bedroom", 5000, 0),
        ]

        result = validate_layout(self.layout(rooms))

        self.assertFalse(result["valid"])
        self.assertTrue(
            any("Circulation is disconnected" in error for error in result["errors"])
        )

    def test_room_placement_respects_plot_boundaries(self):
        rooms = LayoutPlanner().create_rooms(
            {"living_room": 1},
            plot_width=4800,
            plot_height=4200,
            vastu={},
        )

        self.assertEqual(rooms[0]["x"], 0)
        self.assertEqual(rooms[0]["y"], 0)
        self.assertEqual(rooms[0]["x"] + rooms[0]["width"], 4800)
        self.assertEqual(rooms[0]["y"] + rooms[0]["height"], 4200)

    def test_impossible_site_requirements_have_a_useful_diagnostic(self):
        constraints = {
            "space_constraints": {
                "plot_width": 3000,
                "plot_height": 3000,
                "rooms": {"living_room": 1},
            },
            "building_constraints": {
                "floors": 2,
                "parking": {"required": True, "cars": 1, "bikes": 2},
            },
        }

        with self.assertRaisesRegex(
            ValueError,
            "ground floor.*Parking.*Staircase.*Circulation",
        ):
            LayoutPlanner().generate_layout(constraints)

    def test_two_floor_30_by_40_foot_house_reserves_site_features(self):
        constraints = {
            "space_constraints": {
                "plot_width": 9144,
                "plot_height": 12192,
                "rooms": {
                    "living_room": 1,
                    "family_room": 1,
                    "family_room_enclosed": False,
                    "bedrooms": 3,
                    "master_bedrooms": 2,
                    "bathrooms": 2,
                    "common_bathrooms": 1,
                    "kitchen": 1,
                    "dining_room": 1,
                    "balcony": 1,
                    "utility_room": 1,
                },
            },
            "building_constraints": {
                "floors": 2,
                "staircase": True,
                "parking": {"required": True, "cars": 1, "bikes": 2},
            },
            "structural_constraints": {},
        }

        layout = LayoutPlanner().generate_layout(constraints)
        floors = layout["floors"]

        self.assertEqual(set(floors), {"ground_floor", "first_floor"})
        self.assertEqual(layout["room_count"], 10)
        self.assertTrue(layout["family_lounge"])
        self.assertEqual(
            sum(room["type"] in ("master_bedroom", "bedroom")
                for room in floors["first_floor"]["rooms"]),
            3,
        )
        self.assertEqual(
            sum(room["type"] in ("common_bathroom", "bathroom")
                for floor in floors.values() for room in floor["rooms"]),
            2,
        )
        self.assertEqual(
            sum(room["type"] == "balcony"
                for floor in floors.values() for room in floor["rooms"]),
            1,
        )
        self.assertEqual(
            sum(room["type"] == "utility_room"
                for floor in floors.values() for room in floor["rooms"]),
            1,
        )
        self.assertEqual(
            sum(room["type"] == "family_room"
                for floor in floors.values() for room in floor["rooms"]),
            0,
        )

        ground_features = {
            feature["type"]: feature
            for feature in floors["ground_floor"]["site_features"]
        }
        first_features = {
            feature["type"]: feature
            for feature in floors["first_floor"]["site_features"]
        }
        ground_open_spaces = {
            area["type"]: area
            for area in floors["ground_floor"]["open_spaces"]
        }
        first_open_spaces = {
            area["type"]: area
            for area in floors["first_floor"]["open_spaces"]
        }
        self.assertIn("parking", ground_features)
        self.assertEqual(ground_features["parking"]["width"], 3500)
        self.assertEqual(ground_features["parking"]["height"], 5000)
        self.assertIn("circulation", ground_open_spaces)
        self.assertIn("circulation", first_open_spaces)
        self.assertIn("family_lounge", first_open_spaces)
        self.assertEqual(
            (
                ground_features["staircase"]["x"],
                ground_features["staircase"]["y"],
            ),
            (
                first_features["staircase"]["x"],
                first_features["staircase"]["y"],
            ),
        )

        for floor in floors.values():
            checked = dict(floor)
            checked["rooms"] = (
                floor["rooms"]
                + floor["site_features"]
                + floor["open_spaces"]
            )
            result = validate_layout(checked)
            self.assertTrue(result["valid"], result["errors"])

    def test_fixed_rectangle_cannot_overhang_without_cantilever_support(self):
        planner = LayoutPlanner()
        support = [
            {"x": 0, "y": 0, "width": 3000, "height": 3000},
        ]
        balcony = {
            "id": "balcony_1",
            "type": "balcony",
            "name": "Balcony 1",
            "width": 3000,
            "height": 1500,
            "fixed_x": 3000,
            "fixed_y": 0,
        }

        self.assertIsNone(
            planner._pack_rooms(
                [balcony],
                6000,
                3000,
                support_footprint=support,
            )
        )
        balcony["cantilever_supported"] = True
        placed = planner._pack_rooms(
            [balcony],
            6000,
            3000,
            support_footprint=support,
        )
        self.assertIsNotNone(placed)
        self.assertTrue(placed[0]["cantilever_supported"])

    def test_40_by_60_foot_four_bedroom_three_bathroom_g_plus_one(self):
        planner = LayoutPlanner()
        constraints = {
            "space_constraints": {
                "plot_width": 40 * 304.8,
                "plot_height": 60 * 304.8,
                "rooms": {
                    "living_room": 1,
                    "dining_room": 1,
                    "kitchen": 1,
                    "bedrooms": 4,
                    "master_bedrooms": 1,
                    "bathrooms": 3,
                    "attached_bathrooms": 1,
                    "common_bathrooms": 2,
                    "balcony": 1,
                },
            },
            "building_constraints": {
                "floors": 2,
                "staircase": True,
                "parking": {"required": True, "cars": 1},
            },
            "structural_constraints": {
                "balcony_cantilever_supported": True,
            },
        }

        layout = planner.generate_layout(constraints)
        floors = layout["floors"]
        self.assertEqual(layout["room_count"], 11)
        self.assertTrue(_validate_generated_layout(layout)["valid"])

        ground_stair = next(
            item for item in floors["ground_floor"]["site_features"]
            if item["type"] == "staircase"
        )
        first_stair = next(
            item for item in floors["first_floor"]["site_features"]
            if item["type"] == "staircase"
        )
        self.assertEqual(
            (
                ground_stair["x"],
                ground_stair["y"],
                ground_stair["width"],
                ground_stair["height"],
            ),
            (
                first_stair["x"],
                first_stair["y"],
                first_stair["width"],
                first_stair["height"],
            ),
        )

        ground = floors["ground_floor"]
        support = [
            *[
                room for room in ground["rooms"]
                if room["type"] != "balcony"
            ],
            *[
                feature for feature in ground["site_features"]
                if feature["type"] != "parking"
            ],
            *ground["open_spaces"],
        ]
        self.assertFalse(any(item["type"] == "parking" for item in support))
        for room in floors["first_floor"]["rooms"]:
            if room["type"] == "balcony":
                self.assertTrue(room["cantilever_supported"])
                continue
            self.assertTrue(
                planner._within_support_footprint(
                    room["x"],
                    room["y"],
                    room["width"],
                    room["height"],
                    support,
                ),
                room["name"],
            )

        for floor in floors.values():
            all_items = (
                floor["rooms"]
                + floor["site_features"]
                + floor["open_spaces"]
            )
            result = validate_layout(
                {
                    **floor,
                    "rooms": all_items,
                }
            )
            self.assertTrue(result["valid"], result["errors"])
            for item in all_items:
                self.assertGreaterEqual(item["x"], 0)
                self.assertGreaterEqual(item["y"], 0)
                self.assertLessEqual(
                    item["x"] + item["width"],
                    floor["plot"]["width"],
                )
                self.assertLessEqual(
                    item["y"] + item["height"],
                    floor["plot"]["height"],
                )

        with TemporaryDirectory() as output_dir:
            renderer = Renderer()
            renderer.exporter.output_dir = Path(output_dir)
            outputs = renderer.render(
                ground,
                "40 by 60 ft house plan",
                "planner_test",
                base_name="ground_floor",
            )
            self.assertTrue(outputs)
            self.assertTrue(all(Path(path).is_file() for path in outputs.values()))

        scene = SceneBuilder().build(layout)
        self.assertEqual(len(scene.floors), 2)

    def test_single_floor_generation_still_succeeds(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12000,
                "plot_height": 10000,
                "rooms": {
                    "living_room": 1,
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "kitchen": 1,
                    "dining_room": 1,
                },
            },
            "building_constraints": {"floors": 1},
            "structural_constraints": {},
        }

        layout = LayoutPlanner().generate_layout(constraints)
        self.assertEqual(layout["floor_count"], 1)
        self.assertEqual(layout["room_count"], 6)
        self.assertTrue(_validate_generated_layout(layout)["valid"])

    def test_requested_40_by_30_foot_floor_distribution_is_preserved(self):
        constraints = {
            "space_constraints": {
                "plot_width": 40 * 304.8,
                "plot_height": 30 * 304.8,
                "rooms": {
                    "living_room": 1,
                    "family_room": 1,
                    "family_room_enclosed": False,
                    "bedrooms": 3,
                    "master_bedrooms": 1,
                    "guest_rooms": 1,
                    "bathrooms": 3,
                    "common_bathrooms": 2,
                    "attached_bathrooms": 1,
                    "kitchen": 1,
                    "dining_room": 1,
                    "balcony": 1,
                },
                "floor_allocations": {
                    "ground_floor": {
                        "living_room": 1,
                        "guest_room": 1,
                        "dining_room": 1,
                        "kitchen": 1,
                        "common_bathroom": 1,
                    },
                    "first_floor": {
                        "master_bedroom": 1,
                        "bedroom": 1,
                        "common_bathroom": 1,
                        "attached_bathroom": 1,
                        "balcony": 1,
                    },
                },
            },
            "building_constraints": {
                "floors": 2,
                "staircase": True,
                "front_porch": True,
            },
            "structural_constraints": {
                "balcony_cantilever_supported": False,
            },
        }

        layout = LayoutPlanner().generate_layout(constraints)
        floors = layout["floors"]

        self.assertEqual(floors["ground_floor"]["plot"]["width"], 12192)
        self.assertEqual(floors["ground_floor"]["plot"]["height"], 9144)
        self.assertEqual(layout["room_count"], 10)
        self.assertEqual(
            [room["type"] for room in floors["ground_floor"]["rooms"]].count(
                "common_bathroom"
            ),
            1,
        )
        self.assertEqual(
            [room["type"] for room in floors["first_floor"]["rooms"]].count(
                "common_bathroom"
            ),
            1,
        )
        self.assertEqual(
            sum(
                room["type"] in {"master_bedroom", "guest_room", "bedroom"}
                for floor in floors.values()
                for room in floor["rooms"]
            ),
            3,
        )
        self.assertIn(
            "family_lounge",
            {space["type"] for space in floors["first_floor"]["open_spaces"]},
        )
        self.assertIn(
            "front_porch",
            {feature["type"] for feature in floors["ground_floor"]["site_features"]},
        )
        self.assertIn(
            "staircase_landing",
            {feature["type"] for feature in floors["first_floor"]["site_features"]},
        )
        self.assertTrue(
            all(floor["circulation"]["connected"] for floor in floors.values())
        )

        validation = _validate_generated_layout(layout, constraints)
        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(
            validation["checks"]["room_counts"]["expected"],
            validation["checks"]["room_counts"]["generated"],
        )
        self.assertTrue(validation["checks"]["staircase_alignment"])
        self.assertTrue(validation["checks"]["structural_support"])
        self.assertTrue(validation["checks"]["front_porch"])

        scene = SceneBuilder().build(layout)
        for floor in scene.floors:
            connectivity = floor.metadata["connectivity_validation"]
            self.assertTrue(connectivity["valid"], connectivity)

    def test_incomplete_floor_allocation_is_rejected(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12192,
                "plot_height": 9144,
                "rooms": {"living_room": 1, "bedrooms": 1},
                "floor_allocations": {
                    "ground_floor": {"living_room": 1},
                    "first_floor": {},
                },
            },
            "building_constraints": {"floors": 2},
        }

        with self.assertRaisesRegex(ValueError, "do not match requested room counts"):
            LayoutPlanner().generate_layout(constraints)

    def test_two_floor_living_room_and_family_lounge_allocate_separately(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12192,
                "plot_height": 9144,
                "rooms": {
                    "living_room": 1,
                    "family_room": 1,
                    "family_room_enclosed": False,
                    "kitchen": 1,
                    "dining_room": 1,
                    "bedrooms": 1,
                    "bathrooms": 1,
                },
                "floor_allocations": {
                    "ground_floor": {
                        "living_room": 1,
                        "kitchen": 1,
                        "dining_room": 1,
                    },
                    "first_floor": {
                        "bedroom": 1,
                        "bathroom": 1,
                        "family_lounge": 1,
                    },
                },
            },
            "building_constraints": {"floors": 2},
        }

        layout = LayoutPlanner().generate_layout(constraints)
        floors = layout["floors"]
        self.assertEqual(
            [room["type"] for room in floors["ground_floor"]["rooms"]].count(
                "living_room"
            ),
            1,
        )
        self.assertEqual(
            sum(room["type"] == "living_room" for room in floors["first_floor"]["rooms"]),
            0,
        )
        self.assertEqual(
            [space["type"] for space in floors["first_floor"]["open_spaces"]].count(
                "family_lounge"
            ),
            1,
        )

    def test_two_floor_living_room_without_family_lounge(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12192,
                "plot_height": 9144,
                "rooms": {"living_room": 1},
            },
            "building_constraints": {"floors": 2},
        }

        layout = LayoutPlanner().generate_layout(constraints)
        self.assertEqual(layout["room_count"], 1)
        self.assertEqual(
            sum(
                space["type"] == "family_lounge"
                for floor in layout["floors"].values()
                for space in floor["open_spaces"]
            ),
            0,
        )

    def test_two_family_lounges_can_be_allocated_once_per_floor(self):
        constraints = {
            "space_constraints": {
                "plot_width": 12192,
                "plot_height": 9144,
                "rooms": {
                    "living_room": 1,
                    "family_room": 2,
                    "kitchen": 1,
                    "dining_room": 1,
                    "bedrooms": 1,
                    "bathrooms": 1,
                },
                "floor_allocations": {
                    "ground_floor": {
                        "living_room": 1,
                        "kitchen": 1,
                        "dining_room": 1,
                        "family_room": 1,
                    },
                    "first_floor": {
                        "bedroom": 1,
                        "bathroom": 1,
                        "family_room": 1,
                    },
                },
            },
            "building_constraints": {"floors": 2},
        }

        layout = LayoutPlanner().generate_layout(constraints)
        self.assertEqual(layout["room_count"], 5)
        self.assertEqual(
            [space["type"] for space in layout["floors"]["ground_floor"]["open_spaces"]].count(
                "family_lounge"
            ),
            1,
        )
        self.assertEqual(
            [space["type"] for space in layout["floors"]["first_floor"]["open_spaces"]].count(
                "family_lounge"
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
