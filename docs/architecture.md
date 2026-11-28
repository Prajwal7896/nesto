# Nesto System Architecture Documentation

## Overview

Nesto is an AI-powered smart house planning system designed to extract spatial design requirements from natural language, cross-reference them against architectural knowledge via Retrieval-Augmented Generation (RAG), generate spatial 2D room layouts, validate them before rendering, and export CAD blueprints.

---

## High-Level Architecture Diagram

```
+-----------------------------------------------------------------------+
|                            USER INTERFACE                             |
|                (HTML5 + Tailwind CSS + Vanilla JS)                    |
+-----------------------------------------------------------------------+
                                   |
                         HTTP POST /generate
                                   v
+-----------------------------------------------------------------------+
|                            FASTAPI BACKEND                            |
|             (Routing, Authentication, Dependency Injection)          |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                        RAG & AI PIPELINE                              |
|                                                                       |
|  1. Extractor (Gemini 2.5 Flash + Pydantic Schema)                     |
|  2. Memory Merger (Session State + Conversation History)              |
|  3. Vector Retriever (FAISS + gemini-embedding-001 + Knowledge Base)    |
|  4. Constraint Processing (Space, Structural, Vastu, Cost)            |
|  5. Layout Planner (Spatial Coordinates, Polygon Adjacency Graph)      |
|  6. Layout Placement & Validator (boundaries, counts, overlap, access)  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         CAD RENDERER ENGINE                           |
|                                                                       |
|  - ezdxf Modelspace Construction                                      |
|  - Wall Extrusion Generator                                           |
|  - Door Arc & Window Cutout Generators                                |
|  - Furniture Block Placement                                          |
|  - Room Centroid Annotation & Floor Hatching                          |
|  - Exporter Engine (DXF / SVG / PNG)                                  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         OUTPUT FILE STORAGE                           |
|        (/output/floorplan_{id}.dxf, .svg, .png, .json)               |
+-----------------------------------------------------------------------+
```

---

## Detailed Subsystem Breakdown

### 1. Requirement Extraction & Normalization
- **Module**: `backend/api/rag/extractor.py` & `backend/api/rag/extractor_1/`
- **Mechanism**: Passes user prompt to `gemini-2.5-flash` with zero temperature and structured JSON response mode.
- **Pydantic Validation**: Parses JSON into `Requirements` models (`ProjectRequirements`, `PlotRequirements`, `RoomRequirements`, `PreferenceRequirements`, `ConstructionRequirements`).
- **Coordinates**: Plot dimensions are converted from the declared plot unit to millimetres before layout generation.

### 2. Retrieval-Augmented Generation (RAG) System
- **Module**: `backend/api/rag/retriever.py` & `backend/api/rag/indexing/`
- **Embedding Model**: Google `gemini-embedding-001` (3072 dimensions); embedding failures are surfaced rather than replaced with unrelated vectors.
- **Vector DB**: Normalized FAISS `IndexFlatIP` stored in `backend/data/embeddings/index/faiss.index`. The adjacent `index_config.json` records the model, dimension, metric, and vector count; retrieval rejects missing or mismatched metadata.
- **Rebuild after model changes**: From the repository root, run `python -m backend.data.embeddings.build_index` with `GOOGLE_API_KEY` configured. The old index was created using incompatible fallback vectors and must be rebuilt before RAG retrieval is used. Rebuilding replaces the existing index and metadata.
- **Knowledge Base Corpora**:
  - `building_codes/`: Setbacks, height restrictions, lighting regulations.
  - `vastu/`: Directional guidelines for entrance, kitchen, master bedroom.
  - `structural/`: Column grid rules, beam spacing limits, slab thickness.
  - `cost/`: Material budget estimations per square foot.

### 3. Constraint Processing & Layout Planner
- **Module**: `backend/api/rag/constraints.py` & `backend/api/rag/planner.py`
- **Constraint Building**: Fuses user requirements with retrieved category chunks into a unified `constraints` dictionary.
- **Spatial Geometry**: Packs exactly the requested room instances as non-overlapping 2D bounding boxes in millimetres, with unique IDs and matching 4-point polygons.
- **Adjacency and openings**: Builds connectivity from shared room boundaries and emits supported door/window placements for the renderer.

### 4. Layout Validation
- **Module**: `backend/api/rag/layout_validator.py`
- **Rule Checks**:
  - **Room counts**: Requires exact agreement with requested counts, including zero-count room types.
  - **Geometry**: Checks positive dimensions, area and polygon consistency, unique IDs/coordinates, overlaps, and plot containment.
  - **Openings**: Checks that door and window wall references and dimensions are valid.
- Invalid placements are retried by the planner; layouts that still fail validation are rejected before DXF, SVG, or PNG rendering.

### 5. CAD Renderer Engine
- **Module**: `backend/api/rag/renderer/`
- **Modelspace Setup**: Creates `ezdxf` document using R2010 format (`AC1024`).
- **Generators**:
  - `WallGenerator`: Extrudes wall segments from polygon boundaries.
  - `DoorGenerator`: Adds door frames and swing arcs along wall segments.
  - `WindowGenerator`: Inserts standard window symbols into wall lines.
  - `FurnitureGenerator`: Places bed, sofa, dining table block primitives inside room polygons.
  - `LabelGenerator` & `HatchGenerator`: Attaches room title/area labels at room centroids and applies hatch patterns.
  - `Exporter`: Produces native DXF, SVG via `ezdxf.addons.drawing.svg.SVGBackend`, and high-resolution 300 DPI PNG via `MatplotlibBackend`.
