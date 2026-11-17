"""Data access layer for the tasks API.

The API talks to a repository object, so tests can swap in an in-memory
fake and never need a running PostgreSQL instance.
"""
import psycopg2
import psycopg2.extras


class TaskRepository:
    def __init__(self, dsn):
        self.dsn = dsn

    def _connect(self):
        return psycopg2.connect(self.dsn, connect_timeout=3)

    def ping(self):
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)

    def list_tasks(self):
        with self._connect() as conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                "SELECT id, title, done, created_at FROM tasks ORDER BY id"
            )
            rows = cur.fetchall()
        for row in rows:
            row["created_at"] = row["created_at"].isoformat()
        return rows

    def add_task(self, title):
        with self._connect() as conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) "
                "RETURNING id, title, done, created_at",
                (title,),
            )
            row = cur.fetchone()
        row["created_at"] = row["created_at"].isoformat()
        return row

    def set_done(self, task_id, done):
        with self._connect() as conn, conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            cur.execute(
                "UPDATE tasks SET done = %s WHERE id = %s "
                "RETURNING id, title, done, created_at",
                (done, task_id),
            )
            row = cur.fetchone()
        if row is None:
            return None
        row["created_at"] = row["created_at"].isoformat()
        return row

    def delete_task(self, task_id):
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cur.rowcount > 0
