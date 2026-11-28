# Nesto API Endpoint Specification

## Overview

The Nesto backend API is built using **FastAPI**. It exposes endpoints for authentication, profile management, and floor plan generation.

---

## Base URL
`http://localhost:8000`

---

## Endpoints Summary

| Path | Method | Content-Type | Description |
| :--- | :--- | :--- | :--- |
| `/generate` | `POST` | `application/json` | Primary endpoint for floor plan layout generation |
| `/login` | `GET`, `POST` | `application/x-www-form-urlencoded` | User login authentication |
| `/register` | `GET`, `POST` | `application/x-www-form-urlencoded` | User registration |
| `/profile` | `GET` | `text/html` | User profile page view |
| `/profile/update` | `POST` | `multipart/form-data` | Update user details & upload avatar |
| `/logout` | `POST` | N/A | Logout session redirect |

---

## Endpoint Details

### 1. `POST /generate`

#### Description
Parses user prompt, extracts requirements, executes RAG retrieval, plans room spatial layout, validates rules, and renders DXF, SVG, and PNG files.

#### Request Body (`application/json`)
```json
{
  "prompt": "Create a modern 2-floor house with 3 bedrooms, 2 bathrooms, open kitchen, and east entrance."
}
```

#### Successful Response (`200 OK`)
```json
{
  "status": "success",
  "prompt": "Create a modern 2-floor house with 3 bedrooms, 2 bathrooms, open kitchen, and east entrance.",
  "requirements": {
    "project": { "building_type": "villa", "style": "modern" },
    "plot": { "width": 40.0, "length": 60.0, "area": 2400.0 },
    "rooms": {
      "living_room": 1,
      "bedrooms": 3,
      "bathrooms": 2,
      "kitchen": 1,
      "dining_room": 1,
      "balcony": 1
    }
  },
  "layout": {
    "plot": { "width": 12000, "height": 18000 },
    "rooms": [
      {
        "id": "living_room_500_500",
        "type": "living_room",
        "x": 500,
        "y": 500,
        "width": 5000,
        "height": 4500,
        "area": 22500000,
        "polygon": [[500, 500], [5500, 500], [5500, 5000], [500, 5000]]
      }
    ],
    "adjacency_graph": [
      { "from": "living_room", "to": "kitchen" }
    ],
    "total_area": 145000000
  },
  "validation": {
    "valid": true,
    "score": 100,
    "errors": [],
    "warnings": []
  },
  "files": {
    "dxf": "output/floorplan_1.dxf",
    "svg": "output/floorplan_1.svg",
    "png": "output/floorplan_1.png",
    "dxf_url": "/output/floorplan_1.dxf",
    "svg_url": "/output/floorplan_1.svg",
    "png_url": "/output/floorplan_1.png"
  },
  "summary": {
    "rooms": 10,
    "valid": true
  }
}
```

---

### 2. `POST /login`

#### Description
Authenticates user against stored database password hash.

#### Form Parameters (`application/x-www-form-urlencoded`)
- `email`: User email address
- `password`: User password

#### Response
- `302 Found`: Redirects to `/profile` on success.
- `200 OK` (with `error` context): Re-renders `login.html` on invalid credentials.

---

### 3. `POST /register`

#### Description
Registers a new user account in the database.

#### Form Parameters (`application/x-www-form-urlencoded`)
- `name`: User full name
- `email`: User email address
- `password`: Password string
- `confirm_password`: Password confirmation string
- `role`: Account role
- `terms`: Acceptance indicator

#### Response
- `302 Found`: Redirects to `/login` on successful creation.

---

### 4. `POST /profile/update`

#### Description
Updates existing user attributes and handles profile image uploads.

#### Form Data (`multipart/form-data`)
- `name`: String
- `email`: String
- `phone_number`: Optional string
- `age`: Optional integer
- `role`: Optional string
- `profile_image`: Optional binary image file

#### Response
- `303 See Other`: Redirects to `/`.
