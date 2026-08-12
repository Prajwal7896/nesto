# Nesto | AI-Powered Smart House Planning System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4.svg?style=flat&logo=google)](https://deepmind.google/technologies/gemini/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-FF6F00.svg?style=flat)](https://github.com/facebookresearch/faiss)
[![CAD ezdxf](https://img.shields.io/badge/CAD-ezdxf-00599C.svg?style=flat)](https://ezdxf.mozman.at/)

> Transform natural language prompts into structural, code-compliant architectural floor plans and export professional DXF, SVG, and high-DPI PNG CAD blueprints in seconds.

---

## 🌟 Key Features

- **🗣️ Natural Language Requirement Extraction**: Powered by Google Gemini 2.5 Flash to convert intuitive user descriptions (*"3BHK villa with Vastu kitchen, master suite, and balcony"*) into strictly typed Pydantic requirement schemas.
- **📚 Architectural Knowledge Grounding (RAG)**: Integrates vector search (FAISS + Google `text-embedding-004`) across building codes (NBC), Vastu Shastra rules, room sizing standards, material cost data, and structural grid rules.
- **📐 Automated Spatial Layout Planner**: Generates room coordinate polygons, bounding boxes, area metrics, and topological adjacency graphs dynamically.
- **⚙️ Multi-Pass Layout Optimization Engine**: Runs up to 5 validation-optimization loops to resolve spatial overlap, missing rooms, privacy bounds, and cross-ventilation rules.
- **✍️ CAD Rendering & Multi-Format Export**: Uses `ezdxf`, SVGBackend, and Matplotlib to export native DXF CAD vector drawings (`.dxf`), vector web diagrams (`.svg`), and high-resolution raster images (`.png`).
- **👤 User Profile & Session Persistence**: Full authentication system (SQLAlchemy ORM + Bcrypt) maintaining user project histories and multi-turn prompt context.

---

## 🏗️ Architecture Overview

```
User Prompt ("Modern 2-floor 3BHK house...")
                       │
                       ▼
          [FastAPI Backend Server]
                       │
                       ▼
     [LLM Requirements Extraction Engine]
             (Gemini 2.5 Flash)
                       │
                       ▼
         [FAISS RAG Retriever & Vector DB]
   (NBC Building Codes, Vastu, Structural Rules)
                       │
                       ▼
         [Constraint Fusion Processing]
                       │
                       ▼
          [2D Spatial Layout Planner]
                       │
                       ▼
        [5x Iterative Validation Engine]
                       │
                       ▼
          [ezdxf CAD Renderer Engine]
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
   [DXF Export]   [SVG Export]   [PNG Export]
```

For complete technical details, see the [PROJECT_REPORT.md](file:///c:/Users/prajw/OneDrive/Documents/nesto/PROJECT_REPORT.md) and [docs/architecture.md](file:///c:/Users/prajw/OneDrive/Documents/nesto/docs/architecture.md).

---

## 🛠️ Technology Stack

| Domain | Technology |
| :--- | :--- |
| **Frontend** | HTML5, Jinja2 Templates, Tailwind CSS (Glassmorphic UI), Vanilla JavaScript ES6+ |
| **Backend** | FastAPI, Python 3.10+, SQLAlchemy ORM, Uvicorn |
| **Database** | PostgreSQL / SQLite, Passlib (Bcrypt hashing) |
| **AI / RAG** | Google Gemini (`gemini-2.5-flash`), `text-embedding-004`, FAISS Vector Search |
| **CAD Graphics** | `ezdxf` (AC1024 / R2010 DXF), `ezdxf.addons.drawing.svg`, Matplotlib (300 DPI PNG) |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- C++ Build Tools (for compiling `faiss-cpu` on Windows)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Prajwal7896/nesto.git
cd nesto

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install required dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./nesto.db
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Launching Application
```bash
# Run FastAPI server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Open your web browser and navigate to `http://localhost:8000`.

---

## 📖 API Usage Example

### Floor Plan Generation Endpoint
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
           "prompt": "Create a modern 2-floor house with 3 bedrooms, open kitchen, and east-facing main entrance."
         }'
```

#### Response Snippet:
```json
{
  "status": "success",
  "summary": {
    "rooms": 10,
    "valid": true
  },
  "files": {
    "dxf_url": "/output/floorplan_1.dxf",
    "svg_url": "/output/floorplan_1.svg",
    "png_url": "/output/floorplan_1.png"
  }
}
```

For full endpoint documentation, check [docs/api.md](file:///c:/Users/prajw/OneDrive/Documents/nesto/docs/api.md).

---

## 📄 License & Contributing

This project is open-source under the MIT License. Contributions are welcome! Please refer to [CONTRIBUTING.md](file:///c:/Users/prajw/OneDrive/Documents/nesto/CONTRIBUTING.md) for contribution guidelines.
