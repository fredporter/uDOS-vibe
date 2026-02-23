"""
Workflow Manager - uDOS Native Todo/Project System (Wizard)
"""

import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.workflow")


class TaskStatus(Enum):
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class WorkflowManager:
    """Native workflow/todo manager for uDOS (Wizard)."""

    def __init__(self, db_path: str = None):
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "workflow.db"
        self.db_path = Path(db_path) if db_path else default_db
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"[WIZ] Workflow manager using {self.db_path}")

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'not-started',
                priority INTEGER DEFAULT 5,
                depends_on TEXT,
                file_refs TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (task_id, tag_id)
            )
            """
        )
        conn.commit()
        conn.close()

    def create_project(self, name: str, description: str = "") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (name, description),
        )
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def get_or_create_project(self, name: str, description: str = "") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]
        conn.close()
        return self.create_project(name, description)

    def list_projects(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return projects

    def _coerce_workflow_id(self, workflow_id: str | int) -> int:
        if isinstance(workflow_id, int):
            return workflow_id
        try:
            return int(str(workflow_id).strip())
        except ValueError as exc:
            raise ValueError(f"Invalid workflow_id: {workflow_id}") from exc

    def create_workflow(
        self,
        name: str,
        description: str | None = None,
        task_ids: list[str] | None = None,
    ) -> Dict[str, Any]:
        project_id = self.create_project(name=name, description=description or "")

        linked_task_ids: list[int] = []
        if task_ids:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for task_id_raw in task_ids:
                try:
                    task_id = int(str(task_id_raw).strip())
                except ValueError:
                    continue
                cursor.execute(
                    "UPDATE tasks SET project_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (project_id, task_id),
                )
                if cursor.rowcount:
                    linked_task_ids.append(task_id)
            conn.commit()
            conn.close()

        workflow_payload = self.get_workflow(project_id)
        workflow_payload["linked_task_ids"] = linked_task_ids
        workflow_payload["message"] = "Workflow created"
        return workflow_payload

    def get_workflows(self) -> Dict[str, Any]:
        workflows: list[dict[str, Any]] = []
        for project in self.list_projects():
            project_id = project["id"]
            tasks = self.get_project_tasks(project_id)
            workflows.append(
                {
                    "id": str(project_id),
                    "name": project.get("name", ""),
                    "description": project.get("description"),
                    "status": project.get("status", "active"),
                    "created_at": project.get("created_at"),
                    "updated_at": project.get("updated_at"),
                    "task_count": len(tasks),
                }
            )
        return {"status": "success", "workflows": workflows, "count": len(workflows)}

    def get_workflow(self, workflow_id: str | int) -> Dict[str, Any]:
        project_id = self._coerce_workflow_id(workflow_id)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise ValueError(f"Workflow not found: {workflow_id}")

        project = dict(row)
        tasks = self.get_project_tasks(project_id)
        return {
            "status": "success",
            "workflow": {
                "id": str(project_id),
                "name": project.get("name", ""),
                "description": project.get("description"),
                "status": project.get("status", "active"),
                "created_at": project.get("created_at"),
                "updated_at": project.get("updated_at"),
                "task_count": len(tasks),
                "tasks": tasks,
            },
        }

    def get_workflow_tasks(self, workflow_id: str | int) -> Dict[str, Any]:
        project_id = self._coerce_workflow_id(workflow_id)
        tasks = self.get_project_tasks(project_id)
        return {
            "status": "success",
            "workflow_id": str(project_id),
            "tasks": tasks,
            "count": len(tasks),
        }

    def get_workflow_status(self, workflow_id: str | int) -> Dict[str, Any]:
        project_id = self._coerce_workflow_id(workflow_id)
        tasks = self.get_project_tasks(project_id)
        by_status: dict[str, int] = {}
        for task in tasks:
            status = str(task.get("status") or "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        return {
            "status": "success",
            "workflow_id": str(project_id),
            "summary": {
                "tasks_total": len(tasks),
                "by_status": by_status,
            },
        }

    def run_workflow(self, workflow_id: str | int) -> Dict[str, Any]:
        project_id = self._coerce_workflow_id(workflow_id)
        tasks = self.get_project_tasks(project_id)
        pending = [
            task for task in tasks
            if task.get("status") not in {TaskStatus.COMPLETED.value, "completed"}
        ]
        if not pending:
            return {
                "status": "success",
                "workflow_id": str(project_id),
                "message": "No runnable tasks",
                "run": None,
            }

        next_task = pending[0]
        task_id = int(next_task["id"])
        task_status = str(next_task.get("status") or TaskStatus.NOT_STARTED.value)
        if task_status in {TaskStatus.NOT_STARTED.value, TaskStatus.DEFERRED.value}:
            self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            task_status = TaskStatus.IN_PROGRESS.value

        return {
            "status": "success",
            "workflow_id": str(project_id),
            "message": "Workflow run started",
            "run": {
                "task_id": str(task_id),
                "task_title": next_task.get("title", ""),
                "task_status": task_status,
                "started_at": datetime.now().isoformat(),
            },
        }

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str = "",
        priority: int = 5,
        depends_on: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        depends_str = ",".join(map(str, depends_on)) if depends_on else None
        cursor.execute(
            """INSERT INTO tasks (project_id, title, description, priority, depends_on)
            VALUES (?, ?, ?, ?, ?)""",
            (project_id, title, description, priority, depends_str),
        )
        task_id = cursor.lastrowid
        if tags:
            for tag_name in tags:
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,)
                )
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                    (task_id, tag_id),
                )
        conn.commit()
        conn.close()
        return task_id

    def update_task_status(self, task_id: int, status: TaskStatus) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        completed_at = datetime.now() if status == TaskStatus.COMPLETED else None
        cursor.execute(
            """UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP, completed_at = ? WHERE id = ?""",
            (status.value, completed_at, task_id),
        )
        conn.commit()
        conn.close()

    def get_project_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT t.*, GROUP_CONCAT(tg.name) as tags
               FROM tasks t
               LEFT JOIN task_tags tt ON t.id = tt.task_id
               LEFT JOIN tags tg ON tt.tag_id = tg.id
               WHERE t.project_id = ?
               GROUP BY t.id
               ORDER BY t.priority, t.created_at""",
            (project_id,),
        )
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_blocked_tasks(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'blocked' ORDER BY priority")
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def export_to_markdown(self, project_id: Optional[int] = None) -> str:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if project_id:
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            projects = [dict(cursor.fetchone())]
        else:
            cursor.execute("SELECT * FROM projects WHERE status = 'active'")
            projects = [dict(row) for row in cursor.fetchall()]

        md = "# uDOS Workflow\n\n"
        md += f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
        for project in projects:
            md += f"## {project['name']}\n\n"
            if project.get("description"):
                md += f"{project['description']}\n\n"
            tasks = self.get_project_tasks(project["id"])
            for task in tasks:
                checkbox = "x" if task["status"] == TaskStatus.COMPLETED.value else " "
                md += f"- [{checkbox}] **{task['title']}** (Priority: {task['priority']}, Status: {task['status']})\n"
                if task.get("description"):
                    md += f"  - {task['description']}\n"
                if task.get("tags"):
                    md += f"  - Tags: {task['tags']}\n"
                md += "\n"
        conn.close()
        return md
