# Nesto System Architecture Documentation

## Overview

Nesto is an AI-powered smart house planning system designed to extract spatial design requirements from natural language, cross-reference them against architectural knowledge via Retrieval-Augmented Generation (RAG), generate spatial 2D room layouts, optimize them through automated constraint validation, and export CAD blueprints.

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
|  3. Vector Retriever (FAISS + text-embedding-004 + Knowledge Base)     |
|  4. Constraint Processing (Space, Structural, Vastu, Cost)            |
|  5. Layout Planner (Spatial Coordinates, Polygon Adjacency Graph)      |
|  6. Layout Optimizer & Validator (5x Iterative Rule Evaluation)        |
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
- **Normalizer**: Converts dimensional strings (e.g. "30 ft x 40 ft") into standard millimeters (300mm scale factor in coordinate planning).

### 2. Retrieval-Augmented Generation (RAG) System
- **Module**: `backend/api/rag/retriever.py` & `backend/api/rag/indexing/`
- **Embedding Model**: Google `text-embedding-004` (3072 dimensions) with SHA-256 local hash vector fallback.
- **Vector DB**: FAISS Flat L2 Index stored in `backend/data/embeddings/index/faiss.index`.
- **Knowledge Base Corpora**:
  - `building_codes/`: Setbacks, height restrictions, lighting regulations.
  - `vastu/`: Directional guidelines for entrance, kitchen, master bedroom.
  - `structural/`: Column grid rules, beam spacing limits, slab thickness.
  - `cost/`: Material budget estimations per square foot.

### 3. Constraint Processing & Layout Planner
- **Module**: `backend/api/rag/constraints.py` & `backend/api/rag/planner.py`
- **Constraint Building**: Fuses user requirements with retrieved category chunks into a unified `constraints` dictionary.
- **Spatial Geometry**: Computes 2D room bounding boxes (`x`, `y`, `width`, `height`, `area`) and constructs 4-point polygon arrays (`[[x, y], [x+w, y], [x+w, y+h], [x, y+h]]`).
- **Adjacency Graph**: Constructs topological links between living rooms, kitchens, bedrooms, and bathrooms.

### 4. Layout Validation & Optimization Loop
- **Module**: `backend/api/rag/layout_validator.py` & `backend/api/rag/optimizer.py`
- **Optimization Loop**: Executes up to 5 iterations.
- **Rule Checks**:
  - **Required Rooms**: Verifies that generated room polygons cover requested bedroom, bathroom, living room counts.
  - **Area Thresholds**: Evaluates plot area versus sum of room polygon areas.
  - **Structural & Planning Integrity**: Checks cross-ventilation flags and privacy parameters.
  - **Vastu Compliance**: Verifies main entrance and room orientation vectors against Vastu constraints.

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
