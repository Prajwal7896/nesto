# Contributing to Nesto AI Smart House Planning System

Thank you for your interest in contributing to **Nesto**! We welcome contributions from developers, architects, AI researchers, and CAD engineers.

---

## 📜 Code of Conduct

Maintain a respectful, inclusive, and professional environment. Focus on constructive feedback, technical excellence, and collaboration.

---

## 🛠️ Getting Started

1. **Fork the Repository**: Create a fork of `https://github.com/Prajwal7896/nesto.git` under your GitHub account.
2. **Clone your Fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nesto.git
   cd nesto
   ```
3. **Set Up Development Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

---

## 🌿 Branching Strategy

Follow standard Git Feature Branching rules:
- `main` / `master`: Production-ready code. All PRs target this branch.
- `feature/<short-description>`: New features (e.g., `feature/3d-obj-exporter`, `feature/vitu-rules-expansion`).
- `fix/<issue-number>-<short-description>`: Bug fixes (e.g., `fix/wall-polygon-alignment`).
- `docs/<topic>`: Documentation enhancements.

---

## 🎨 Code Style Guidelines

### Python (Backend & RAG Engine)
- Follow **PEP 8** style guidelines.
- Use explicit type annotations where appropriate (`typing.Dict`, `typing.List`, Pydantic models).
- Format code with `black` or `autopep8`:
  ```bash
  black backend/
  ```
- Docstrings: Use Google-style or standard Python docstrings for major functions and class methods.

### JavaScript & Frontend
- Use modern ES6+ standards (`const`/`let`, async/await, arrow functions).
- Keep DOM selectors centralized and avoid mutating third-party library properties.

---

## 🧪 Testing Guidelines

Before opening a Pull Request:
1. Verify backend route functionality:
   ```bash
   pytest test/
   ```
2. Verify FAISS index builder script execution:
   ```bash
   python backend/api/rag/indexing/builder.py
   ```
3. Verify test floorplan creation manually or programmatically via `/generate`.

---

## 📬 Submitting Pull Requests

1. **Keep PRs Focused**: A PR should resolve a single feature or bug.
2. **Commit Messages**: Use clean, descriptive commit messages:
   - `feat: add door opening clipping to wall generator`
   - `fix: resolve float conversion error in requirement normalizer`
   - `docs: update API schema for /generate endpoint`
3. **PR Description**: Include a clear summary of changes, rationale, testing performed, and screenshots/artifacts if UI or CAD outputs are modified.
