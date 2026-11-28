
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

_projects = {}


def create_project_id():
    return uuid4().hex


def get_project(user_id: str, project_id: str):
    project = _projects.get(project_id)

    if not project or project["user_id"] != user_id:
        return None

    return deepcopy(project)


def list_projects(user_id: str):
    projects = []

    for project in _projects.values():
        if project["user_id"] == user_id:
            projects.append({
                "project_id": project["project_id"],
                "title": project["title"],
                "created_at": project["created_at"],
                "updated_at": project["updated_at"],
            })

    return sorted(
        projects,
        key=lambda item: item["updated_at"],
        reverse=True
    )


def load(user_id: str, project_id: str):
    project = get_project(user_id, project_id)

    if not project:
        return None

    return deepcopy(project["requirements"])


def save(
    user_id: str,
    project_id: str,
    requirements,
    prompt: str
):
    now = datetime.now(timezone.utc).isoformat()

    existing = _projects.get(project_id)

    if existing and existing["user_id"] != user_id:
        raise PermissionError("You do not own this project.")

    title = (
        existing["title"]
        if existing
        else prompt.strip()[:60] or "Untitled Project"
    )

    _projects[project_id] = {
        "project_id": project_id,
        "user_id": user_id,
        "title": title,
        "requirements": deepcopy(requirements),
        "last_prompt": prompt,
        "created_at": (
            existing["created_at"] if existing else now
        ),
        "updated_at": now,
    }

    return project_id
